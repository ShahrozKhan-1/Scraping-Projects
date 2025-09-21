from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

extracted_data = []
links = set()

def get_categories_link(driver):
    """Collect category links"""
    elements = driver.find_elements(By.CSS_SELECTOR, "ul#top-menu > li.category > a")
    for el in elements:
        href = el.get_attribute("href")
        if href:
            links.add(href)

    links.difference_update({
        'https://alvfrance.com/en/',
        'https://alvfrance.com/en/#',
        'https://alvfrance.com/en/78-new-equipment'
    })


def get_product_links(driver):
    """Scrape product links with pagination"""
    product_links = set()
    while True:
        products = driver.find_elements(By.CSS_SELECTOR, "article.product_item a.thumbnail.product-thumbnail")
        for p in products:
            href = p.get_attribute("href")
            if href:
                product_links.add(href)
        next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.next.js-search-link")
        if next_buttons:
            driver.get(next_buttons[0].get_attribute("href"))
        else:
            break
    return list(product_links)



def get_product_details(driver, product_link):
    """Extract product details"""
    driver.get(product_link)

    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.productpage_title").text.strip()
    except:
        title = "N/A"

    try:
        raw_price = driver.find_element(By.CSS_SELECTOR, "span.product-without-taxes").text
        ex_vat_price = raw_price.replace("€", "").replace("tax excl.", "").replace(",", "").strip()
    except:
        ex_vat_price = "N/A"

    try:
        raw_price = driver.find_element(By.CSS_SELECTOR, "small.price").text
        inc_vat_price = raw_price.replace("€", "").replace("tax incl.", "").replace(",", "").strip()
    except:
        inc_vat_price = "N/A"

    try:
        description_element = driver.find_element(By.CSS_SELECTOR, "div.product-description")
        description = description_element.text.strip()
        if not description:
            description = "N/A"
    except:
        description = "N/A"

    try:
        quantity_text = driver.find_element(By.CSS_SELECTOR, "span.message").text.strip()
        lines = [line.strip() for line in quantity_text.split("\n") if line.strip()]
        if len(lines) == 2:
            quantity = lines[1]
        elif len(lines) == 1:
            quantity = lines[0]
        else:
            quantity = "N/A"
        quantity = quantity.replace("In stock", "").strip()
    except:
        quantity = "N/A"

    try:
        images = driver.find_elements(By.CSS_SELECTOR, "div.owl-wrapper img.thumb")
        image_src = [img.get_attribute("src") for img in images if img.get_attribute("src")]
    except:
        image_src = []
    if not image_src:
        image_src = ["N/A"]

    try:
        brand = driver.find_element(By.CSS_SELECTOR, "div.brand-infos a").text.strip()
    except:
        brand = "N/A"

    try:
        breadcrumbs = driver.find_elements(By.CSS_SELECTOR, "ol[itemtype='http://schema.org/BreadcrumbList'] li span[itemprop='name']")
        breadcrumb_texts = [b.text.strip() for b in breadcrumbs]

        if len(breadcrumb_texts) == 3:
            category = breadcrumb_texts[1]
            subcategory = "N/A"
        elif len(breadcrumb_texts) >= 4:
            category = breadcrumb_texts[1]
            subcategory = breadcrumb_texts[2]
        else:
            category = "N/A"
            subcategory = "N/A"
    except:
        category = "N/A"
        subcategory = "N/A"

    product_data = {
        "product_url": product_link,
        "title": title,
        "brand": brand,
        "category": category,
        "subcategory": subcategory,
        "ex_vat_price": ex_vat_price,
        "inc_vat_price": inc_vat_price,
        "quantity": quantity,
        "condition": "N/A",
        "description": description,
        "image": image_src
    }

    print(product_data)
    return product_data


def extracting_detail(driver):
    get_categories_link(driver)
    for url in links:
        driver.get(url)
        product_links = get_product_links(driver)
        for link in product_links:
            data = get_product_details(driver, link)
            extracted_data.append(data)


def to_csv():
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("site4.csv", index=False)
        print("CSV saved: site4.csv")
    except:
        print("Error while creating CSV file")



chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--log-level=3") 
chrome_options.add_argument("--disable-images")
chrome_options.add_argument("--disable-javascript")
chrome_options.add_argument("--blink-settings=imagesEnabled=false")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(5)

driver.get('https://alvfrance.com/en/')

extracting_detail(driver)
to_csv()

driver.quit()
