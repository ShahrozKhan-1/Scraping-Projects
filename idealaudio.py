from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

extracted_data = []


def get_product_links():
    time.sleep(2)
    links = driver.find_elements(By.CSS_SELECTOR, "div#js-product-list a.thumbnail.product-thumbnail")
    product_link = []
    for link in links:
        try:
            url = link.get_attribute("href")
            if url and "cookieyes.com" not in url and url not in product_link:
                product_link.append(url)
        except:
            continue 
    return product_link


def get_product_details(product_link):
    driver.execute_script(f"window.open('{product_link}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)
    try:
        text = driver.find_element(By.CSS_SELECTOR, "h1.h1").text.strip()
        parts = text.split(" - ")

        title = parts[0].strip()
        condition = parts[1].strip() if len(parts) > 1 else "N/A"
        if "Rupture de stock" in condition:
            condition.strip("Rupture de stock")
        elif condition == "Rupture de stock":
            condition = "N/A"
    except:
        title, condition = "N/A", "N/A"
        
    
    try:
        desc_el = driver.find_element(By.CSS_SELECTOR, "div.product-description")
        text = desc_el.text.strip()
        lines = text.split("\n")
        ex_vat_price = next((line for line in lines if "€" in line), "N/A")
        if ex_vat_price != "N/A":
            ex_vat_price = (
                ex_vat_price.replace("€", "")
                .replace("HT", "")
                .replace("l'unité", "")
                .replace("\u202f", "")
                .replace(",", "")
                .strip()
            )
        else:
            ex_vat_price = "N/A"
    except:
        ex_vat_price = "N/A"      


    try:
        incl_vat_price = driver.find_element(By.CSS_SELECTOR, "div.current-price").text
        incl_vat_price = incl_vat_price.replace("€", "").replace("\u202f", "").strip()
        incl_vat_price = incl_vat_price.replace(",", ".")
    except:
        incl_vat_price = "N/A"

    try:
        description = driver.find_element(By.CSS_SELECTOR, "div#description div.product-description").text
    except:
        description = "N/A"

    try:
        thumbs = driver.find_elements(By.CSS_SELECTOR, "ul.product-images.js-qv-product-images li img")
        image_urls = [img.get_attribute("data-image-large-src") for img in thumbs]
    except:
        image_urls = "N/A"


    try:
        category = "N/A"
        subcategory = "N/A"
        breadcrumb = driver.find_element(By.CSS_SELECTOR, "nav.breadcrumb.hidden-sm-down")
        links = breadcrumb.find_elements(By.TAG_NAME, "a")
        if len(links) > 1:
            category = links[1].text.strip()
        if len(links) > 2:
            subcategory = links[2].text.strip()
    except:
        category = "N/A"
        subcategory = "N/A"

    product_data = {
        "product_url": product_link,
        "title": title,
        "quantity": "N/A",
        "category": category,
        "subcategory": subcategory,
        "ex_vat_price": ex_vat_price,
        "inc_vat_price": incl_vat_price,
        "brand": "N/A",
        "condition": condition,
        "description": description,
        "image": image_urls
    }

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(product_data)
    return product_data


def extracting_detail():
    time.sleep(3)
    btn = driver.find_element(By.CSS_SELECTOR, "a.all-product-link.h4")
    btn.click()
    while True:
        product_links = get_product_links()
        for link in product_links:
            data = get_product_details(link)
            extracted_data.append(data)
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next.js-search-link"))
            )
            driver.execute_script("arguments[0].click();", next_btn)
        except:
            break


def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("final13.csv", index=False)
        print("CSV saved: 3.csv")
    except:
        print("Error while creating CSV file")

chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--log-level=3")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-images")

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://idealaudio.biz/')

extracting_detail()
to_csv()

driver.quit()
