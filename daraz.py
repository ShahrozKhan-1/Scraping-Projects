from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd

extracted_data = []

def get_bags():
    elem = driver.find_element(By.ID, "q")
    elem.send_keys("Women bags")
    elem.send_keys(Keys.RETURN)
    
def get_product_link():
    time.sleep(3)
    product_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
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
        title = driver.find_element(By.CLASS_NAME, "pdp-mod-product-badge-title").text
    except:
        title = "N/A"
    try:
        price = driver.find_element(By.CLASS_NAME, "pdp-product-price").text
    except:
        price = "N/A"
    try:
        rating = driver.find_element(By.CLASS_NAME, "seller-info-value").text
    except:
        rating = "N/A"
        
    time.sleep(3)
    driver.execute_script("window.scrollBy(0, 1000);") 
    time.sleep(5)
    try:
        detail = driver.find_element(By.CLASS_NAME, "pdp-product-highlights").text
    except:
        detail = "N/A"

        
    product_data = {
        "title" : title,
        "price" : price,
        "rating" : rating,
        "detail" : detail
    }
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return product_data

def extracting_detail():
    get_bags()
    for page in range(1, 6):
        # print("pageeeeeeeeeeeeee" , page)
        product_link = get_product_link()
        for link in product_link:
            data = get_product_details(link)
            print(data)
            extracted_data.append(data)
        next_page = driver.find_element(By.CSS_SELECTOR, "li.ant-pagination-next")
        next_page.click()
        time.sleep(5)

def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("Daraz_Extracted_Data.csv", index=False)
    except:
        print("Error while creating CSV file")
    
    

driver = webdriver.Chrome()
driver.get('https://www.daraz.pk')
extracting_detail()
to_csv()
driver.quit()