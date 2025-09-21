from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
import pandas as pd

extracted_data = []




def get_categories():
    try:
        categories = driver.find_element(By.XPATH, "/html/body/main/div[4]/div/aside/div/facet-filters-form[1]/form/div/details[1]/div/fieldset/ul[1]")
        return categories
    except:
        print("Can not get categories")
        

def get_product_links():
    try:  
        product_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
        product_link = []
        for link in product_page:
            url = link.get_attribute("href")
            if url and url not in product_link: 
                product_link.append(url)
        return product_link
    except:
        print("Error getting product link")

def get_product_details(product_link, category_name):
    driver.execute_script(f"window.open('{product_link}', '_blank');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])  
    try:
        title = driver.find_element(By.CSS_SELECTOR, "div.product__title").text
    except:
        title = "N/A"
        

    try:
        brand = driver.find_element(By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div[4]/div/div/div/div/table/tbody/tr[2]/td").text
    except:
        brand = "N/A"

    try:
        condition = "Used"
    except:
        print("An error occur while geting condition")

    try:
        button = driver.find_element(By.XPATH, "/html/body/main/div[2]/section")
        button.click()
        block = driver.find_element(By.XPATH, "/html/body/main/div[2]/section/div").text
        lines = block.split("\n")
        raw_price = lines[0]
        price_part = raw_price.split(" ")[0]
        ex_vat_price = price_part.replace("£", "").replace(",", "")

        description = "\n".join(lines[1:]).strip()
    except:
        ex_vat_price = "N/A"
        description = "N/A"

        
    try:
        src = driver.find_elements(By.CSS_SELECTOR, "#Slider-Thumbnails-template--18060392202434__main img")
        image_src = [img.get_attribute("src") for img in src]
        if not image_src:
            try:
                image_container = driver.find_element(By.XPATH, "/html/body/main/section[2]/section/div/div/product-info/div[2]/div[1]/media-gallery/slider-component/div[1]/div/div/modal-opener//img")
                image = image_container.get_attribute("src")
                image_src.append(image)
            except:
                pass
    except:
        image_src = "N/A"
        
    
    try:
        inc_vat_price = driver.find_element(By.XPATH, "/html/body/main/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div[6]/div[1]/div[3]/span[2]").text
        inc_price = inc_vat_price.split()
        inc_price.pop(0)
        product_inc_price = str(inc_price[0])
    except:
        product_inc_price = "N/A"

        
    product_data = {
        "product_url" : product_link,
        "title" : title,
        "category" : category_name,
        "ex_vat_price" : ex_vat_price,
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


def clean_category_name(raw_category: str) -> str:
    category_no_count = raw_category.split("(")[0].strip()
    parts = category_no_count.split()
    mid = len(parts) // 2
    if parts[:mid] == parts[mid:]:  
        return " ".join(parts[:mid])
    return category_no_count


def extracting_detail():  
    categories_ul = get_categories()
    li_category = categories_ul.find_elements(By.TAG_NAME, "li")
    
    for i in range(len(li_category)):
        categories_ul = get_categories()
        li_category = categories_ul.find_elements(By.TAG_NAME, "li")
        category_li = li_category[i]

        raw_category = category_li.text.strip()
        category_name = clean_category_name(raw_category)

        try:
            label = category_li.find_element(By.TAG_NAME, "label")
            label.click()
            time.sleep(5)
            product_links = get_product_links()
            print(f"Category: {category_name}, Products: {len(product_links)}")

            for link in product_links:
                data = get_product_details(link, category_name)
                extracted_data.append(data)
            try:
                time.sleep(3)
                reset = driver.find_element(By.CSS_SELECTOR, "facet-remove a")
                reset.click()
                time.sleep(5)
            except:
                print("Can not locate reset button")

        except Exception as e:
            print(f"Error with category {category_name}: {e}")



def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("site2.csv", index=False)
    except:
        print("Error while creating CSV file")
    
    

chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--log-level=3")  

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://shop.solotech.com/en-uk/collections/used-equipment-in-the-uk')
time.sleep(2)



extracting_detail()
to_csv()
driver.quit()