from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

extracted_data = []


def get_product_links():
    time.sleep(2)
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='product/']")
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
    WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)
    driver.switch_to.window(driver.window_handles[-1])

    try:
        title = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product_title"))
        ).text
    except:
        title = "N/A"

    try:
        product_ex_price = driver.find_element(By.CSS_SELECTOR, "p.price span.woocommerce-Price-amount").text.strip("€")
    except:
        product_ex_price = "N/A"

    try:
        quantity = driver.find_element(By.CSS_SELECTOR, "p.stock.in-stock").text.strip("in stock")
    except:
        quantity = "N/A"
                
    try:
        brand, category = "N/A", "N/A"

        try:
            desc_el = driver.find_element(By.ID, "elementor-tab-content-8381")
        except:
            desc_el = driver.find_element(By.ID, "elementor-tab-content-1191")
        driver.execute_script("arguments[0].style.display='block';", desc_el)
        desc = desc_el.text.strip() if desc_el.text.strip() else "N/A"

        try:
            detail_el = driver.find_element(By.ID, "elementor-tab-content-8383")
        except:
            detail_el = driver.find_element(By.ID, "elementor-tab-content-1193")
        driver.execute_script("arguments[0].style.display='block';", detail_el)
        detail = detail_el.text.strip() if detail_el.text.strip() else "N/A"

        try:
            included_el = driver.find_element(By.ID, "elementor-tab-content-8382")
        except:
            included_el = driver.find_element(By.ID, "elementor-tab-content-1192")
        driver.execute_script("arguments[0].style.display='block';", included_el)
        included = included_el.text.strip() if included_el.text.strip() else "N/A"

        try:
            brand = driver.find_element(By.CSS_SELECTOR,"tr.woocommerce-product-attributes-item--attribute_pa_brand td").text.strip()

            category = driver.find_element(By.CSS_SELECTOR,"tr.woocommerce-product-attributes-item--attribute_pa_product-category td").text.strip()
        except:
            pass

        description = (
            "PRODUCT DESCRIPTION\n" + desc + "\n\n"
            "WHAT'S INCLUDED?\n" + included + "\n\n"
            "PRODUCT DETAILS\n" + detail
        )

    except:
        description = "N/A"


    try:
        images = driver.find_elements(By.CSS_SELECTOR, "ol.flex-control-nav.flex-control-thumbs li img")
        image_src = [img.get_attribute("src") for img in images]
        if not image_src:
            main_img = driver.find_element(By.CSS_SELECTOR, "div.woocommerce-product-gallery__image a")
            src = main_img.get_attribute("href")
            if src:
                image_src.append(src)
    except:
        image_src = "N/A"



    product_data = {
        "product_url": product_link,
        "title": title,
        "quantity": quantity,
        "category": category,
        "subcategory": "N/A",
        "ex_vat_price": product_ex_price,
        "inc_vat_price": "N/A",
        "brand": brand,
        "condition": "N/A",
        "description": description,
        "image": image_src
    }

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(product_data["product_url"])
    return product_data


def extracting_detail():
    product = driver.find_element(By.CSS_SELECTOR, "a[href*='shop']").get_attribute("href")
    driver.get(product)
    while True:
        product_links = get_product_links()
        for link in product_links:
            data = get_product_details(link)
            extracted_data.append(data)

        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next.page-numbers"))
            )
            driver.execute_script("arguments[0].click();", next_btn)
        except:
            break


def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("site11.csv", index=False)
        print("CSV saved: site11.csv")
    except:
        print("Error while creating CSV file")

chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-images")

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://soundsale.nl/')

extracting_detail()
to_csv()

driver.quit()
