import pandas as pd
import asyncio 
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher, CrawlerMonitor
from bs4 import BeautifulSoup


async def main(): 
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        check_robots_txt=True,
        stream=False
    )
    
    dispatcher = MemoryAdaptiveDispatcher(
        #memory_threshold_percent=70.0,
        #check_interval=1.0,
        #max_session_permit=10,
        monitor=CrawlerMonitor()
    )
    
    columns = ["Price", "Land Size", "Building Size", "Year Built", "Rooms", "County"]
    df = pd.DataFrame(columns=columns)
    with open("urls.txt", "r") as f: 
        urls = [f"https://www.realestate.com.au{line.rstrip()}" for line in f]
                
    async with AsyncWebCrawler(config=browser_config) as crawler: 
        results = await crawler.arun_many(
            urls=urls, 
            config=run_config,
            dispatcher=dispatcher,
            return_format="html"
        )
        for result in results: 
            if result.success: 
                df =  proccessing(result, df)
            else: 
                print(f"Crawling {result.url} Failed, Error: {result.error_message}")
                
    df.to_csv("data.csv", index=False)
    
    
def proccessing(result, df): 
    soup = BeautifulSoup(result.html, "html.parser")
    price = soup.find("div", class_="sc-10v3xoh-1 cqrlhJ")
    if price: 
        price = price.get_text(strip=True)
    
    
    property_details = soup.find("div", 
                                    class_="zs0kp9-9 hp6kep-0 kyvSuM", 
                                    attrs={"data-test-id": "ListingFeaturesContainer"})
    
    data = {}
    if property_details:
        property_details_list = property_details.find_all("div")
        for item in property_details_list:
            key_tag = item.find("div", class_="basicInfoKey")
            value_tag = item.find("div", class_="basicInfoValue")
            if key_tag and value_tag:
                key = key_tag.get_text(strip=True)
                value = value_tag.get_text(strip=True) 
                data[key] = value
    try: 
        if data["Property Type"]:
            row = {
                "Price": price,
                "Land Size": data.get("Land Size"),
                "Building Size": data.get("Building Size"),
                "Year Built": data.get("Year Built"),
                "Rooms": data.get("Rooms"),
                "County": data.get("County"),
            }
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    except Exception as e: 
        pass
    
    return df

asyncio.run(main())
