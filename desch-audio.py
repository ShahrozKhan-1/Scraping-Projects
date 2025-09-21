# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import pandas as pd
# import time


# driver = webdriver.Chrome()
# driver.get('https://www.desch-audio.de/')
# time.sleep(3)
# search = driver.find_element(By.CSS_SELECTOR, "input.dmStoreSearchInput")
# search.send_keys(Keys.ENTER)
# time.sleep(100)


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
    links = driver.find_elements(By.CSS_SELECTOR, "div.ec-filters__products a[href*='trading/']")
    product_link = []
    for link in links:
        try:
            url = link.get_attribute("href")
            if url and "cookieyes.com" not in url and url not in product_link:
                product_link.append(url)
        except:
            continue 
    # print(product_link)
    return product_link


def get_product_details(product_link):
    driver.execute_script(f"window.open('{product_link}', '_blank');")
    WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.product-details__product-title.ec-header-h3").text
    except:
        title = "N/A"

    # try:
    #     condition = "N/A"
    #     desc_el = driver.find_element(By.ID, "productDescription")
    #     text = desc_el.text.strip()
    #     lines = text.split("\n")
    #     if lines:
    #         last_line = lines[-1].strip()
    #         if "second hand" in last_line.lower():
    #             condition = last_line
    #         else:
    #             for line in lines:
    #                 if "second hand" in line.lower():
    #                     condition = line
    #                     break
    #         if "(" in condition:
    #             condition = condition.split("(")[0].strip()
    # except:
    #     condition = "N/A"


    try:
        product_ex_price = driver.find_element(By.CSS_SELECTOR, "span.details-product-price__value.ec-price-item").text.strip("€")
    except:
        product_ex_price = "N/A"

    try:
        quantity_raw = driver.find_element(By.CSS_SELECTOR, "div.product-details-module__title.ec-header-h6.details-product-purchase__place").text
        quantity = quantity_raw.replace("In stock:", "").replace("available", "").strip()
        if quantity == "In stock":
            quantity = "N/A"
    except:
        quantity = "N/A"


    try:
        description = driver.find_element(By.CSS_SELECTOR, "div.product-details-module.product-details__general-info").text
        cond = description.split("\n")
        for i in cond:
            if "condition" in i.lower() or "new" in i.lower():
                condition = i
                break
        # print(cond)
        # condition = cond[-1]
    except:
        description, condition = "N/A", "N/A"
        

    try:
        thumbs = driver.find_elements(By.CSS_SELECTOR, ".details-gallery__thumbs .details-gallery__thumb-bg")
        image_urls = []
        for t in thumbs:
            style = t.get_attribute("style")
            if "url(" in style:
                url = style.split("url(")[1].split(")")[0].replace('"', '').replace("'", "")
                image_urls.append(url)
    except:
        image_urls = "N/A"


    try:
        category = "N/A"
        subcategory = "N/A"
        breadcrumb = driver.find_element(By.CSS_SELECTOR, "div.ec-breadcrumbs")
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
        "quantity": quantity,
        "category": category,
        "subcategory": subcategory,
        "ex_vat_price": product_ex_price,
        "inc_vat_price": "N/A",
        "brand": "N/A",
        "condition": condition,
        "description": description,
        "image": image_urls
    }

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    # print(product_data)
    print(product_data['product_url'])
    print(product_data['description'])
    print(product_data['condition'])
    print("--------------------------------")
    return product_data


def extracting_detail():
    time.sleep(3)
    search = driver.find_element(By.CSS_SELECTOR, "input.dmStoreSearchInput")
    search.send_keys(Keys.ENTER)
    while True:
        product_links = get_product_links()[:2]
        for link in product_links:
            data = get_product_details(link)
            extracted_data.append(data)

        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[aria-label='Next']"))
            )
            driver.execute_script("arguments[0].click();", next_btn)
        except:
            break


def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("site12.csv", index=False)
        print("CSV saved: site12.csv")
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
driver.get('https://www.desch-audio.de/')

extracting_detail()
to_csv()

driver.quit()
