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
        
    urls = ["https://www.realestate.com.au/international/us"]
    num_of_pages = 160 
    for p_num in range(2, num_of_pages+2): 
        url = f"https://www.realestate.com.au/international/us/p{p_num}"
        urls.append(url)
    
    
    async with AsyncWebCrawler(config=browser_config) as crawler: 
        results = await crawler.arun_many(
            urls=urls, 
            config=run_config,
            dispatcher=dispatcher,
            return_format="html"
        )
        
        
        for result in results: 
            if result.success: 
                await process_result(result)
                print(f"{result.url} Proccessed succesfully")
                
            else: 
                print(f"Failed to crawl {result.url}: {result.error_message}")
        
        
    
async def process_result(result): 
    soup = BeautifulSoup(result.html, "html.parser")
        
    propery_cards = soup.find_all("div", {"data-testid": "standard-listing-card"})
    
    for card in propery_cards: 
        
        link = card.find("a", href=lambda href: href and href.startswith("/international/us/")) 
        if link:
            with open("urls.txt", "a") as f: 
                f.write(link["href"]+"\n")
                
                
                
                
        
        
        
asyncio.run(main())
        
