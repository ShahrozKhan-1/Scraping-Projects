from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re


extracted_data = []

def get_products():
    # search = driver.find_element(By.CSS_SELECTOR, "#search-toggle-main")
    # search.click()
    # get_product = driver.find_element(By.CSS_SELECTOR, "#search-container-main button.search-submit")
    # get_product.click()
    button = driver.find_element(By.CSS_SELECTOR, "a.wp-block-button__link.wp-element-button")
    button.click()
    time.sleep(3)


def get_product_links():
    product_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='product/']")
    product_link = []
    for link in product_page:
        url = link.get_attribute("href")
        if url and url not in product_link: 
            product_link.append(url)
    cookie = "https://www.cookieyes.com/product/cookie-consent/"
    if cookie in product_link:
        product_link.remove(cookie)
    return product_link

def get_product_details(product_link):
    driver.execute_script(f"window.open('{product_link}', '_blank');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])  
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.product_title").text.strip()
    except:
        title = "N/A"
    try:
        summary_element = driver.find_element(By.CSS_SELECTOR, ".summary")
        summary_text = summary_element.text.strip()

        lines = summary_text.split('\n')
        price_line = next((line for line in lines if '€' in line), "N/A")
        match = re.search(r'€\s*([\d.,]+)', price_line)
        if match:
            product_ex_price = match.group(1).replace(',', '')
        else:
            product_ex_price = "N/A"
    except:
        product_ex_price = "N/A"
    
    print("Ex Price:", product_ex_price)

    try:
        product_inc_price = "N/A"
    except:
        product_inc_price = "N/A"
    

    try:
        posted_in_span = driver.find_elements(By.CSS_SELECTOR, "div.product_meta span.posted_in")

        category = "N/A"
        brand = "N/A"

        for span in posted_in_span:
            text = span.text.lower()
            if "category:" in text or "categories:" in text:
                category = span.find_element(By.TAG_NAME, "a").text.strip()
            elif "brand:" in text:   
                brand = span.find_element(By.TAG_NAME, "a").text.strip()
    except:
        brand = "N/A"
        category = "N/A"

    try:
        condition = "N/A"
    except:
        condition = "N/A"
    try:
        description = driver.find_element(By.XPATH, '//*[@id="tab-description"]').text.replace('\n', ' ')
    except:
        description = "N/A"

    try:
        paragraphs  = driver.find_elements(By.CSS_SELECTOR , "#tab-description p")
        quantity = "N/A"
        for p in paragraphs:
            text = p.text.strip().lower()
            if "pieces available" or "piece available" in text:
                match = re.search(r"(\d+)\s+piece[s]?\s+available", text)
                if match:
                    quantity = int(match.group(1))
                    print("Quantity found:", quantity)
                else:   
                    quantity = "N/A"  
                break
    except:
        quantity = "N/A"

    
    try:
        links = driver.find_elements(By.CSS_SELECTOR, "div.woocommerce-product-gallery__wrapper a")
        image_src = [link.get_attribute("href") for link in links if link.get_attribute("href")]
    except:
        image_src = "N/A"
        
    product_data = {
        "product_url" : product_link,
        "title" : title,
        "quantity": quantity,
        "category": category,
        "ex_vat_price" : product_ex_price,
        "inc_vat_price" : product_inc_price,
        "brand" : brand,
        "condition" : condition,
        "description" : description,
        "image" : image_src
    }

    print(product_data)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return product_data

def extracting_detail():
    extracted_data = []
    get_products()
    while True:
        product_links = get_product_links()
        for link in product_links:
            data = get_product_details(link)
            extracted_data.append(data)
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.next.page-numbers")
            # next_button.click()
            if next_button:
                driver.get(next_button) 
                time.sleep(5) 
            else:
                break 
        except:
            break  

    return extracted_data


def format_data_for_sheet(data):
    formatted_data = []
    for item in data:
        row = {
            "Website Name": "proapplestar",
            "Product URL": item.get("product_url", ""),
            "Product Category": item.get("category", ""),
            "Title": item.get("title", ""),
            "Quantity": item.get("quantity", ""),
            "Ex VAT Price ": item.get("ex_vat_price", ""),
            "Inc VAT Price ": item.get("inc_vat_price", ""),
            "Currency": "EUR",
            "Brand": item.get("brand", ""),
            "Condition": item.get("condition", ""),
            "Product Description": item.get("description", "")
        }
        try:
            images = item["image"]
            for i in range(1, 8):
                try:
                    img = images[i-1]
                except:
                    img = "N/A"
                row[f"Image Src {i}"] = img
                row[f"Image Position {i}"] = i
        except:
            for i in range(1, 8):
                row[f"Image Src {i}"] = "N/A"
                row[f"Image Position {i}"] = i
        formatted_data.append(row)
    return pd.DataFrame(formatted_data)


driver = webdriver.Chrome()
driver.get('https://www.proapplestar.com/')
time.sleep(3)
extracted_data = extracting_detail()
df = format_data_for_sheet(extracted_data)
if not df.empty:
    # upload_to_google_sheets(df, SHEET_NAME, CRED_JSON, worksheet_name="nordicsales.dk")
    df.to_csv("export_Data.csv" , index=False)
else:
    print("No data to upload")

driver.quit()
