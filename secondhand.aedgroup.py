from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd

extracted_data = []

def get_products():
    modal_close_button_1 = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/form/div/div[3]/label")
    modal_close_button_1.click()
    try:
        modal_close_button_2 = driver.find_element(By.XPATH, "/html/body/main/div/div/div[1]/div/div/div/div[1]/div/label")
        if modal_close_button_2.is_displayed():
            modal_close_button_2.click()
    except:
            pass


    elem = driver.find_element(By.XPATH, "/html/body/main/header/nav/div/div[2]/div/ul/li[2]")
    elem.click()
    time.sleep(5)


def get_product_links():
    product_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='/product-detail-page/']")
    product_link = []
    for link in product_page:
        url = link.get_attribute("href")
        if url and url not in product_link: 
            product_link.append(url)
    return product_link

def get_product_details(product_link):
    driver.execute_script(f"window.open('{product_link}', '_blank');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])  
    try:
        title = driver.find_element(By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div[1]/div[1]/h1").text
    except:
        title = "N/A"
        
    try:
        ex_vat_price = driver.find_element(By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div[6]/div[1]/div[1]").text
        ex_price = ex_vat_price.split()
        ex_price.pop(0)
        product_ex_price = str(ex_price[0])
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
        brand = driver.find_element(By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div[4]/div/div/div/div/table/tbody/tr[2]/td").text
    except:
        brand = "N/A"

    try:
        condition = driver.find_element(By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div[5]/div/div/div[2]/button").text
    except:
        condition = "N/A"

    try:
        description = driver.find_element(By.CLASS_NAME, "introduction-text").text
    except:
        description = "N/A"
        
    try:
        src = driver.find_elements(By.CSS_SELECTOR, "img.modal--full__img")
        image_src = ["https://secondhand.aedgroup.com"+img.get_attribute("data-src") for img in src]
    except:
        image_src = "N/A"



        
    product_data = {
        "product_url" : product_link,
        "title" : title,
        "ex_vat_price" : product_ex_price,
        "inc_vat_price" : product_inc_price,
        "brand" : brand,
        "condition" : condition,
        "description" : description,
        "image" : image_src
    }
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return product_data

def extracting_detail():  
    get_products()
    index = 0
    while True:
        product_link = get_product_links()[index: ]
        for link in product_link:
            data = get_product_details(link)
            extracted_data.append(data)
        index += 30
        next_page = driver.find_element(By.ID, "LoadMoreButton")
        next_page.click()
        time.sleep(5)

def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("site1.csv", index=False)
    except:
        print("Error while creating CSV file")
    
    

driver = webdriver.Chrome()
driver.get('https://secondhand.aedgroup.com/home')
time.sleep(5)

extracting_detail()
to_csv()
driver.quit()