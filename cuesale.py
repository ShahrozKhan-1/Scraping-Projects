from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

extracted_data = []


def get_product_links():
    links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/product/']"))
    )
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
        brand = driver.find_element(By.CSS_SELECTOR, "tr.woocommerce-product-attributes-item--attribute_pa_brand td").text
    except:
        brand = "N/A"

    try:
        condition = driver.find_element(By.CSS_SELECTOR,"tr.woocommerce-product-attributes-item--attribute_pa_condition td p").text.strip()
    except:
        condition = "N/A"

    try:
        product_ex_price = driver.find_element(By.CSS_SELECTOR, "p.price span.woocommerce-Price-amount").text.strip("€")
    except:
        product_ex_price = "N/A"

    try:
        quantity = driver.find_element(By.CSS_SELECTOR, "p.in-stock").text.strip("in stock")
    except:
        quantity = "N/A"

    try:
        description = driver.find_element(By.ID, "tab-description").text
    except:
        description = "N/A"

    try:
        images = driver.find_elements(By.CSS_SELECTOR, ".woocommerce-product-gallery__wrapper img")
        image_src = []
        for img in images:
            srcset = img.get_attribute("srcset")
            if srcset:
                largest = srcset.split(",")[-1].strip().split(" ")[0]
                image_src.append(largest)
            else:
                src = img.get_attribute("src")
                if src:
                    image_src.append(src)
        image_src = list(dict.fromkeys(image_src))
        if not image_src:
            image_src = "N/A"
    except:
        image_src = "N/A"



    try:
        category_block = driver.find_element(By.CSS_SELECTOR, "span.posted_in")
        links = category_block.find_elements(By.TAG_NAME, "a")
        category = links[0].text if len(links) > 0 else "N/A"
        subcategory = links[1].text if len(links) > 1 else "N/A"
    except:
        category, subcategory = "N/A", "N/A"

    product_data = {
        "product_url": product_link,
        "title": title,
        "quantity": quantity,
        "category": category,
        "subcategory": subcategory,
        "ex_vat_price": product_ex_price,
        "inc_vat_price": "N/A",
        "brand": brand,
        "condition": condition,
        "description": description,
        "image": image_src
    }

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(product_data)
    return product_data


def extracting_detail():
    try:
        cookie = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cky-btn-accept"))
        )
        cookie.click()
    except:
        pass
    shop = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "ul li a[href*='/shop']"))
    )
    shop.click()

    while True:
        product_links = get_product_links()[:2]
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
        df.to_csv("site8.csv", index=False)
        print("CSV saved: site8.csv")
    except:
        print("Error while creating CSV file")


chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--log-level=3")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-images")
chrome_options.add_argument("--disable-javascript")

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://cuesale.com/')

extracting_detail()
to_csv()

driver.quit()
