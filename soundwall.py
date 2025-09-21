from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium.webdriver.chrome.options import Options



extracted_data = []
visited_products = set() 

def get_products():
    menu_items = driver.find_elements(By.CSS_SELECTOR, "nav.elementor-nav-menu--main > ul > li")
    selected_items = menu_items[1:4:2]
    results = []
    exclude_links = [
        "https://www.soundwall.info/gebrauchte-produkte/",
        "https://www.soundwall.info/gebrauchte-produkte/audio/ton-anlagen/",
        "https://www.soundwall.info/gebrauchte-produkte/audio/mischpulte/",
        "https://www.soundwall.info/gebrauchte-produkte/audio/mikrofone/",
        "https://www.soundwall.info/gebrauchte-produkte/audio/sonstiges/",
        "https://www.soundwall.info/shop-small-stuff/shop-ton/",  
        "https://www.soundwall.info/shop-small-stuff/shop-licht/",
        "https://www.soundwall.info/shop-small-stuff/shop-cases/"
    ]
    for li in selected_items:
        a = li.find_element(By.TAG_NAME, "a")
        href = a.get_attribute("href")
        if href not in exclude_links:
            results.append(href)
        try:
            sub_links = li.find_elements(By.CSS_SELECTOR, "ul.sub-menu a")
            for s in sub_links:
                sub_href = s.get_attribute("href")
                if sub_href not in exclude_links:
                    results.append(sub_href)
        except:
            pass
    print(results)
    return results


def get_product_links():
    product_page = driver.find_elements(By.CSS_SELECTOR, "div.uael-woo-products-thumbnail-wrap a[href*='/produkt/']")
    product_link = []
    for link in product_page:
        url = link.get_attribute("href")
        if url and url not in product_link:
            product_link.append(url)
    return product_link


def get_product_details(product_link):
    if product_link in visited_products:
        return None
    visited_products.add(product_link)

    driver.execute_script(f"window.open('{product_link}', '_blank');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])  

    try:
        title = driver.find_element(By.CSS_SELECTOR, "div.elementor-widget-woocommerce-product-title").text
        parts = title.split()
        brand = parts[2] if len(parts) >= 3 else "N/A"
    except:
        title, brand = "N/A", "N/A"
        
    try:
        product_ex_price = driver.find_element(By.CSS_SELECTOR, "p.price").text
        product_ex_price = product_ex_price.replace("€", "").replace("exkl. MwSt.", "").strip()
        product_ex_price = product_ex_price.replace(".", "").replace(",", ".")
    except:
        product_ex_price = None

    quantity = "N/A"
    try:
        stock_text = driver.find_element(By.CSS_SELECTOR, "p.in-stock").text.lower()
        stock_text = stock_text.replace("vorrätig", "").strip()
        if stock_text.isdigit():
            quantity = int(stock_text)
    except:
        pass
    if not quantity:
        try:
            desc_text = driver.find_element(By.ID, "tab-description").text.lower()

            if "pieces" in desc_text:
                for word in desc_text.split():
                    if word.isdigit():
                        quantity = int(word)
                        break
            elif "pairs" in desc_text:
                quantity = 2
        except:
            pass


    try:
        description = driver.find_element(By.ID, "tab-description").text
    except:
        description = "N/A"
        
    try:
        src = driver.find_elements(By.CSS_SELECTOR, ".elementor-image-carousel .swiper-slide img")
        image_src = [img.get_attribute('src') for img in src]
    except:
        image_src = "N/A"

    try:
        breadcrumbs = driver.find_elements(By.CSS_SELECTOR, "span.posted_in.detail-container span.detail-content a")
        breadcrumb_texts = [b.text.strip() for b in breadcrumbs if b.text.strip()]
        
        if len(breadcrumb_texts) >= 3:
            category = breadcrumb_texts[0]
            subcategory = breadcrumb_texts[2]
        elif len(breadcrumb_texts) == 2:
            category = breadcrumb_texts[0]
            subcategory = breadcrumb_texts[1]
        elif len(breadcrumb_texts) == 1:
            category = breadcrumb_texts[0]
            subcategory = "N/A"
        else:
            category = "N/A"
            subcategory = "N/A"
            
    except Exception as e:
        print(f"Error extracting breadcrumbs: {e}")
        category, subcategory = "N/A", "N/A"

    product_data = {
        "product_url" : product_link,
        "title" : title,
        "quantity": quantity,
        "category": category,
        "subcategory": subcategory,
        "ex_vat_price" : product_ex_price,
        "inc_vat_price" : "N/A",
        "brand" : brand,
        "condition" : "N/A",
        "description" : description,
        "image" : image_src
    }

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(product_data)
    return product_data


def extracting_detail():  
    results = get_products()
    for url in results:
        driver.get(url)
        product_links = get_product_links()
        for link in product_links:
            data = get_product_details(link)
            if data:
                extracted_data.append(data)
        time.sleep(3)


def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("site6.csv", index=False)
    except:
        print("Error while creating CSV file")
    


chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--log-level=3") 
chrome_options.add_argument("--disable-images")
chrome_options.add_argument("--disable-javascript")
chrome_options.add_argument("--blink-settings=imagesEnabled=false")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.soundwall.info")
time.sleep(3)

extracting_detail()
to_csv()
driver.quit()
