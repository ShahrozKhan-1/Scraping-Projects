from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd

extracted_data = []

def get_products():
    search = driver.find_element(By.CSS_SELECTOR, "button.js-typeahead-enter-btn")
    search.click()
    time.sleep(3)


def get_product_links():
    product_page = driver.find_elements(By.CSS_SELECTOR, "div#ProductsContainer a[href*='/products/']")
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
        title = driver.find_element(By.CSS_SELECTOR, "div.product__title h1").text
    except:
        title = "N/A"
        
    try:
        product_ex_price = driver.find_element(By.CSS_SELECTOR, "div.price--product-page").text
        product_ex_price = product_ex_price.replace("€", "").replace(",", "").strip()
    except:
        product_ex_price = "N/A"

        
    try:
        inc_vat_price = driver.find_element(By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div[6]/div[1]/div[3]/span[2]").text
        inc_price = inc_vat_price.split()
        inc_price.pop(0)
        product_inc_price = str(inc_price[0])
    except:
        product_inc_price = "N/A"

    try:
        brand = driver.find_element(By.XPATH, "//th[contains(text(), 'NS Brands')]/following-sibling::td").text.strip()
    except:
        brand = "N/A"

    try:
        condition_text = driver.find_element(By.XPATH, "//th[contains(text(), 'Product use  condition')]/following-sibling::td").text.strip()
        condition = condition_text.split(",")[0]
    except:
        condition = "N/A"

    try:
        quantity_text = driver.find_element(By.CSS_SELECTOR, "div.product__stock-delivery span.u-margin-right--lg").text.strip()
        quantity = quantity_text.replace("In stock", "").replace("in stock", "").strip()
    except:
        quantity = "N/A"

    try:
        description = driver.find_element(By.CSS_SELECTOR, "table.table--no-top-border").text
    except:
        description = "N/A"
        
    try:
        src = driver.find_elements(By.CSS_SELECTOR, "img.modal--full__img")
        image_src = ["https://nordicsales.dk"+img.get_attribute("data-src") for img in src]
    except:
        image_src = "N/A"

    try:
        breadcrumbs = driver.find_elements(By.CSS_SELECTOR, "ul.breadcrumb li.breadcrumb__item a")
        breadcrumb_texts = [b.text.strip() for b in breadcrumbs if b.text.strip()]
        if len(breadcrumb_texts) >= 2:
            category = breadcrumb_texts[-2]
            subcategory = breadcrumb_texts[-1]
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
        "inc_vat_price" : product_inc_price,
        "brand" : brand,
        "condition" : condition,
        "description" : description,
        "image" : image_src
    }
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(product_data)
    return product_data

def extracting_detail():  
    get_products()
    while True:
        try:
            load_more = driver.find_element(By.ID, "LoadMoreButton")
            if load_more.is_displayed():
                load_more.click()
                time.sleep(3)
            else:   
                break
        except:
            break

    product_link = get_product_links()[:30]
    for link in product_link:
        data = get_product_details(link)
        extracted_data.append(data)


def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("site5.csv", index=False)
    except:
        print("Error while creating CSV file")
    
    

driver = webdriver.Chrome()
driver.get('https://nordicsales.dk/')
time.sleep(3)

extracting_detail()
to_csv()
driver.quit()