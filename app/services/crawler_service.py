import time
import asyncio
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor

# Create a thread pool
executor = ThreadPoolExecutor(max_workers=3)

def _fetch_reviews_sync(url: str, limit: int = 10):
    """
    Synchronous version of the crawler to be run in a separate thread.
    This avoids the Windows Asyncio Proactor/Selector loop conflict.
    """
    reviews = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url)
            page.wait_for_timeout(3000)
            
            iframe = page.frame(name="entryIframe")
            if not iframe:
                iframe = page
            
            # 4. Wait for list to appear
            # Wait for specific review list item OR the review tab content container
            try:
                iframe.wait_for_selector("li.pui__X35jYm", timeout=7000) 
            except:
                print("Primary selector failed, trying text-based detection...")
            
            # 5. Scroll down to load more reviews (Deep Scan)
            # Try to scroll the list to ensure we have enough candidates (e.g. 50 items)
            # Naver Map list often responds to body scroll or specific container
            for _ in range(3):
                try:
                    iframe.locator("body").press("PageDown")
                    time.sleep(0.5)
                except:
                    pass

            # 6. Get Review Items
            # Strategy: Get all LIs that look like reviews
            review_items = iframe.locator("li.pui__X35jYm").all()
            
            if not review_items:
                # Fallback 1: Try finding list items containing "별점" or "리뷰" text hidden/visible
                # Use a more generic selector for the list items if the class changed again
                # But pui__X35jYm is consistent in the dump.
                # Let's try to reload or wait a bit more? 
                time.sleep(2)
                review_items = iframe.locator("li.pui__X35jYm").all()

            if not review_items:
                 # Fallback 2: Look for any list item with the review text class
                 review_items = iframe.locator("li").filter(has=iframe.locator(".pui__vn15t2")).all()

            print(f"DEBUG: Found {len(review_items)} review items")

            count = 0
            for item in review_items:
                if count >= limit:
                    break
                
                # Check for "Owner Reply" (사장님 답글)
                has_reply = False
                # The class .pui__QztK4Q was found to be visit info, not reply. 
                # Rely on text content "사장님 답글" or a more specific selector if found later.
                if "사장님 답글" in item.inner_text():
                    has_reply = True
                
                if not has_reply:
                    # Extract Review Text
                    # Class pui__vn15t2 is the review text 
                    text_element = item.locator(".pui__vn15t2")
                    if text_element.count() > 0:
                        text = text_element.inner_text()
                    else:
                        # Fallback
                        text = item.inner_text()
                    
                    text = text.replace("더보기", "").strip()
                    # Filter out purely photo reviews or empty texts
                    if len(text) > 5 and "개의 리뷰가 더 있습니다" not in text:
                        reviews.append(text)
                        count += 1
        except Exception as e:
            print(f"Error scraping: {e}")
        finally:
            browser.close()
    return reviews

async def fetch_naver_reviews(url: str, limit: int = 10):
    """
    Wrapper to run sync crawler in a thread pool.
    """
    loop = asyncio.get_running_loop()
    reviews = await loop.run_in_executor(executor, _fetch_reviews_sync, url, limit)
    return reviews
