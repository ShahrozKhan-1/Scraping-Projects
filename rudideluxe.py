from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

extracted_data = []

def get_products():
    results = []
    nav = driver.find_elements(By.CSS_SELECTOR, "nav.elementor-nav-menu--main ul li")
    for li in nav:
            a = li.find_element(By.TAG_NAME, "a")
            href = a.get_attribute("href")
            if href and href not in results:
                results.append(href)
    results.remove('https://rudideluxe.de/product-category/shop/offers/')
    # print(results)
    return results


def get_product_links():
    product_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='/produkt/']")
    product_link = []
    for link in product_page:
        url = link.get_attribute("href")
        if url and url not in product_link: 
            product_link.append(url)
    print(product_link)
    return product_link

def get_product_details(product_link):

    driver.execute_script(f"window.open('{product_link}', '_blank');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])  

    try:
        title = driver.find_element(By.CSS_SELECTOR, "div.elementor-widget-woocommerce-product-title").text
    except:
        title= "N/A"
        

    try:
        try:
            product_ex_price = driver.find_element(By.CSS_SELECTOR, "p.price ins .woocommerce-Price-amount").text
        except:
            product_ex_price = driver.find_element(By.CSS_SELECTOR, "p.price").text
        if "VB" in product_ex_price.upper():
            product_ex_price = "N/A"
        else:
            product_ex_price = (
                product_ex_price.replace("€", "")
                .replace("exkl. MwSt.", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
    except:
        product_ex_price = "N/A"


    try:
       quantity = driver.find_element(By.CSS_SELECTOR, "p.in-stock").text
       quantity = quantity.replace("vorrätig", "")
    except:
        quantity = "N/A"

    try:
        description = driver.find_element(By.ID, "tab-description").text
    except:
        description = "N/A"
        
    try:
        images = driver.find_elements(By.CSS_SELECTOR, "ol.flex-control-nav.flex-control-thumbs img")
        image_src = [img.get_attribute("src") for img in images if img.get_attribute("src")]
        if not image_src:
            main_img = driver.find_element(By.CSS_SELECTOR, "img.wp-post-image")
            image_src = main_img.get_attribute("src")
    except:
        image_src = "N/A"

    try:
        breadcrumbs = driver.find_elements(By.CSS_SELECTOR, "nav.product-category-breadcrumb a")
        breadcrumb_texts = [b.text.strip() for b in breadcrumbs if b.text.strip()]
        
        if len(breadcrumb_texts) >= 2:
            category = breadcrumb_texts[0]
            subcategory = breadcrumb_texts[1]
        elif len(breadcrumb_texts) == 1:
            category = breadcrumb_texts[0]
            subcategory = "N/A"
        else:
            category = "N/A"
            subcategory = "N/A"
    except:
        category = "N/A"
        subcategory = "N/A"


    product_data = {
        "product_url" : product_link,
        "title" : title,
        "quantity": quantity,
        "category": category,
        "subcategory": subcategory,
        "ex_vat_price" : product_ex_price,
        "inc_vat_price" : "N/A",
        "brand" : "N/A",
        "condition" : "N/A",
        "description" : description,
        "image" : image_src
    }

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(product_data)
    return product_data

def extracting_detail():  
    results = get_products()[1:-2]
    print("links to fetch data", results)
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
        df.to_csv("site7.csv", index=False)
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
driver.get('https://rudideluxe.de/')
time.sleep(3)

extracting_detail()
to_csv()
driver.quit()