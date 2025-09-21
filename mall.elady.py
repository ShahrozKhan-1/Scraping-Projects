from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd

extracted_data = []

def get_watches():
    watches = driver.find_element(By.XPATH, "/html/body/header/div[2]/div/nav/div[4]")
    all_watches = driver.find_element(By.XPATH, "/html/body/header/div[2]/div/nav/div[4]/div/a[18]")

    action_1 = ActionChains(driver).move_to_element(watches)
    action_1.click(all_watches)
    action_1.perform()
    time.sleep(2)
    gucci = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div/div[1]/div/a[4]")
    gucci.click()
    time.sleep(2)

def get_product_link():
    product_link = []
    product = driver.find_elements(By.CSS_SELECTOR, "a[href*='/item/']")
    for link in product:
        url = link.get_attribute("href")
        if url and url not in product_link:
            product_link.append(url)
    return product_link
        
def get_details(product_link):
    driver.execute_script(f"window.open('{product_link}', '_blank');")  
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    try:
        title = driver.find_element(By.CSS_SELECTOR, "div.detail__name").text
    except:
        title = "N/A"
        
    try:
        price = driver.find_element(By.CSS_SELECTOR, "div.price-box").text
    except:
        price = "N/A"
    
    try:
        information = driver.find_element(By.CSS_SELECTOR, "div#info1_content").text
    except:
        information = "N/A"
    
    hidden = driver.find_element(By.CSS_SELECTOR, "div#info2_content")
    driver.execute_script("arguments[0].style.display = 'block';", hidden)      
    
    try:  
        additional_info = driver.find_element(By.CSS_SELECTOR, "div#info2_content").text
    except:
        additional_info = "N/A"
    
    data = {
        "title" : title,
        "price" : price,
        "information" : information,
        "additional information" : additional_info
    }
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return data

def extract():
    get_watches()
    for page in range(1, 11):
        product_link = get_product_link()
        for link in product_link:
            data = get_details(link)
            # print(data)
            extracted_data.append(data)
        next_page = driver.find_element(By.CSS_SELECTOR, "a.item_pager__list[title='Next']")
        next_page_link = next_page.get_attribute("href")
        driver.get(next_page_link)
        time.sleep(2)
        
def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("elady_data.csv", index=False)
        print("Successfully Saved to CSV")
    except Exception as e:
        print("Error: ", e)


driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://mall.elady.com")
time.sleep(2)
extract()

try:
    to_csv()
    print("CSV generated successfully")
except:
    print("Error while creating CSV file")
    