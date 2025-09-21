from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd

extracted_data = []
results = []


def get_categories_link():
    shop = driver.find_element(By.XPATH, "/html/body/div[2]/header/div[3]/div/div[2]/nav/ul/li/a")
    ActionChains(driver).move_to_element(shop).perform()
    time.sleep(1)
    left_cats = driver.find_elements(By.CSS_SELECTOR, "ul.subchildmenu.col-md-10.mega-columns.columns4 > li.level1")
    for cat in left_cats:
        main_link = cat.find_element(By.TAG_NAME, "a")
        category_name = main_link.text.strip()

        ActionChains(driver).move_to_element(main_link).perform()
        time.sleep(1)

        subcats = cat.find_elements(By.CSS_SELECTOR, "ul.subchildmenu li.level2 a")
        for sub in subcats:
            sub_name = sub.text.strip()
            sub_url = sub.get_attribute("href")
            results.append({
                "category": category_name,
                "subcategory": sub_name,
                "url": sub_url
            })
    right_cats = driver.find_elements(By.CSS_SELECTOR, ".menu-right-block li.level1 a")
    for rc in right_cats:
        rc_name = rc.text.strip()
        rc_url = rc.get_attribute("href")
        results.append({
            "category": rc_name,
            "subcategory": None,
            "url": rc_url
        })
                   

def get_product_links():
    product_links = []
    for i in range(1):
    # while True:
        time.sleep(3)
        product_page = driver.find_elements(By.CSS_SELECTOR, "li.product-item a")
        for link in product_page:
            url = link.get_attribute("href")
            if url and url not in product_links:
                product_links.append(url)
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.pages-item-next a")
            driver.execute_script("arguments[0].click();", next_button)
        except:
            print("No more pages.")
            break
    print(product_links)
    return product_links



def get_product_details(product_link, category, subcategory):
    driver.execute_script(f"window.open('{product_link}', '_blank');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])  
    condition, brand, title = "Used", "N/A", "N/A"
    try:
        title_text = driver.find_element(By.CSS_SELECTOR, "h1.page-title").text
        if title_text and title_text != "N/A":
            parts = [p.strip() for p in title_text.split("|")]

            if len(parts) >= 3: 
                condition, brand, title = parts[0], parts[1], parts[2]

            elif len(parts) == 2:  
                condition, title = parts[0], parts[1]
                brand = "N/A"

            elif len(parts) == 1:  
                if "used" in parts[0].lower():
                    condition = parts[0]
                    title = "N/A"
                else:
                    title = parts[0]
                    condition = "Used"
                    brand = "N/A"
    except:
        pass


    try:
        ex_vat_price = driver.find_element(By.CSS_SELECTOR, "span[data-price-type='finalPrice']").get_attribute("data-price-amount")
    except:
        ex_vat_price = "N/A"

    try:
        description = driver.find_element(By.XPATH, "/html/body/div[2]/main/div[3]/div/div[4]/div/div[2]").text
    except:
        description = "N/A"

    try:
        quantity = driver.find_element(By.XPATH, "/html/body/div[2]/main/div[3]/div/div[2]/div[2]/div[2]/div[1]/span/b").text
    except:
        quantity = "N/A"
        
    try:
        images = driver.find_elements(By.CSS_SELECTOR, ".MagicToolboxContainer .mcs-item a")
        image_src = [img.get_attribute("href") for img in images] if images else ["N/A"]
    except:
        image_src = "N/A"
        
    
    try:
        inc_vat_price = driver.find_element(By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div[6]/div[1]/div[3]/span[2]").text
    except:
        inc_vat_price = "N/A"

        
    product_data = {
        "product_url" : product_link,
        "title" : title,
        "condition" : condition,
        "brand" : brand,
        "quantity" : quantity,
        "description" : description,
        "category": category,
        "subcategory": subcategory if subcategory else "N/A",
        "ex_vat_price" : ex_vat_price,
        "inc_vat_price" : inc_vat_price,
        "image" : image_src
    }
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(product_data)
    return product_data


def extracting_detail():  
    get_categories_link()
    for entry in results:
        url = entry["url"]
        driver.get(url)
        product_link = get_product_links()
        for link in product_link:
            data = get_product_details(link, entry["category"], entry["subcategory"])
            extracted_data.append(data)
        time.sleep(5)



def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("site3.csv", index=False)
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
driver.get('https://www.salesall.eu/')
time.sleep(2)



extracting_detail()
to_csv()
driver.quit()