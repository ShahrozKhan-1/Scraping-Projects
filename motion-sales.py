from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

extracted_data = []


def get_categories():
    main_cat = []
    main = driver.find_elements(By.CSS_SELECTOR, "div.list-group.productnavi a")
    for link in main:
        link = link.get_attribute('href')
        main_cat.append(link)   
    category = []
    for link in main_cat[1:-2]:
        driver.get(link)
        sub = driver.find_elements(By.CSS_SELECTOR, "div.productcontentarea a")
        for li in sub:
            category.append(li.get_attribute("href"))
    return category

def get_product_links():
    links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.thumbnail.productbox a"))
    )
    product_link = []
    for link in links:
        try:
            url = link.get_attribute("href")
            if url and "cookieyes.com" not in url and url not in product_link:
                product_link.append(url)
        except:
            continue 
    print(product_link)
    return product_link


def get_product_details(product_link):

    driver.execute_script(f"window.open('{product_link}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])  

    try:
        title = driver.find_element(By.CSS_SELECTOR, "h2").text.strip()
    except:
        title= "N/A"

    try:
        brand_text = driver.find_element(By.CSS_SELECTOR, "p small").text
        if "Hersteller:" in brand_text:
            brand = brand_text.split("Hersteller:")[-1].strip()
        else:
            brand = "N/A"
    except:
        brand= "N/A"
        

    try:
        product_ex_price = "N/A"
        ex_vat_price_text = driver.find_element(By.XPATH, "//p/b[contains(text(), 'Verkaufspreis')]/..").text
        for word in ex_vat_price_text.split():
            cleaned_word = word.replace(".", "", 1).replace(",", ".", 1)
            if cleaned_word.replace(".", "", 1).isdigit():
                product_ex_price = word
                break
        else:
            product_ex_price = "N/A"
    except:
        product_ex_price = "N/A"


    try:
        quantity = driver.find_element(By.XPATH, "//p/b[contains(text(), 'Aktueller Bestand')]/..").text
    except:
        quantity = "N/A"

    try:
        description = driver.find_element(By.CSS_SELECTOR, "div.col-xs-12.col-sm-8").text
    except:
        description = "N/A"
        
    try:
        thumbs = driver.find_elements(By.CSS_SELECTOR, "div.productimgsquare")
        image_src = []
        for t in thumbs:
            style = t.get_attribute("style")
            if "url(" in style:
                url = style.split("url(")[1].split(")")[0]
                url = f"https://motion-sales.de{url}"
                image_src.append(url)
        image_src = image_src if image_src else "N/A"
    except:
        image_src = "N/A"


    try:
        breadcrumb = driver.find_element(By.CSS_SELECTOR, "div.productheader.hidden-xs")
        links = breadcrumb.find_elements(By.TAG_NAME, "a")
        category = links[0].text.strip() if len(links) > 0 else "N/A"
        subcategory = links[1].text.strip() if len(links) > 1 else "N/A"
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
        "inc_vat_price" : "N/A",
        "brand" : brand,
        "condition" : "N/A",
        "description" : description,
        "image" : image_src
    }

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(product_data)
    return product_data


def extracting_detail():  
    category = get_categories()
    for url in category[:2]:
        driver.get(url)
        product_links = get_product_links()[:4]
        for link in product_links:
            data = get_product_details(link)
            if data:
                extracted_data.append(data)


def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("site9.csv", index=False)
        print("CSV saved: site9.csv")
    except:
        print("Error while creating CSV file")


chrome_options = Options()
chrome_options.page_load_strategy = "eager"
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--log-level=3")
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://motion-sales.de/second-hand.html')

extracting_detail()
to_csv()

driver.quit()
