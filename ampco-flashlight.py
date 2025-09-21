from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re



def get_product_links(driver):
    product_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='/product/']")
    product_link = []
    for link in product_page:
        url = link.get_attribute("href")
        if url and url not in product_link:
            product_link.append(url)
    return product_link


def get_product_details(driver, product_link):
    driver.execute_script(f"window.open('{product_link}', '_blank');")
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[-1])

    try:
        title = driver.find_element(By.TAG_NAME, "h1").text
    except:
        title = "N/A"

    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "p.price")

        ins = price_element.find_elements(By.TAG_NAME, "ins")
        if ins:
            current_price = ins[0].text.strip().replace("€", "")
        else:
            current_price = price_element.text.strip().replace("€", "")
    except:
        current_price = "N/A"


    condition = "N/A"
    try:
        block_condition = driver.find_element(By.XPATH, "//th[contains(text(),'Condition')]/following-sibling::td").text
        if block_condition:
            condition = block_condition
        else:
            hidden_block = driver.find_element(By.CSS_SELECTOR, "div.et_pb_tab.clearfix.et-pb-active-slide")
            driver.execute_script("arguments[0].style.display = 'block';", hidden_block)
            temp_condition = driver.find_element(By.XPATH, "//th[contains(text(),'Condition')]/following-sibling::td").text
            if temp_condition:
                condition = temp_condition
    except:
        pass

    try:
        raw_category = driver.find_element(By.CSS_SELECTOR, ".product_meta .posted_in").text
        category = re.sub(r'^Categories:\s*', '', raw_category, flags=re.IGNORECASE).strip()
    except:
        category = "N/A"


    # Description
    try:
        description_element = driver.find_element(By.ID, "tab-description")
        description = description_element.text.strip()
    except Exception:
        try:
            divi_description = driver.find_element(By.CSS_SELECTOR, ".et_pb_wc_tabs .et_pb_tab_content")
            description = divi_description.text.strip()
        except Exception:
            description = ""

    # Additional Info
    try:
        add_info_element = driver.find_element(By.ID, "tab-additional_information")
        additional_info = add_info_element.text.strip()
    except Exception:
        try:
            divi_tabs = driver.find_elements(By.CSS_SELECTOR, ".et_pb_tab_content")
            if len(divi_tabs) > 1:
                additional_info = divi_tabs[1].text.strip()
            else:
                additional_info = ""
        except Exception:
            additional_info = ""

    try:
        image_element = driver.find_elements(By.CSS_SELECTOR, ".woocommerce-product-gallery__image img")
        images_src = []
        for img in image_element:
            src = img.get_attribute("data-large_image") or img.get_attribute("src")
            if src and src not in images_src:
                images_src.append(src)
        if not images_src:
            images_src = ["N/A"]
    except Exception:
        images_src = ["N/A"]

    full_description = (description if description else "N/A")
    if additional_info:
        full_description += "\n" + additional_info

    product_data = {
        "product_url": product_link,
        "title": title,
        "inc_vat_price": "N/A",
        "ex_vat_price": current_price,
        "condition": condition,
        "category": category,
        "description": full_description,
        "images": images_src
    }
    print("ampco flight" ,product_data)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return product_data


def extracting_detail(driver, extracted_data):
    scraped_url = set()

    while True:
        time.sleep(3)
        all_links = get_product_links(driver)[:5]
        new_links = [link for link in all_links if link not in scraped_url]

        if not new_links:
            print("No new links found. Exiting.")
            break

        for link in new_links:
            try:
                data = get_product_details(driver, link)
                extracted_data.append(data)
                scraped_url.add(link)
                print(f"Scraped: {link}")
            except Exception as e:
                print(f"Error scraping {link}: {e}")

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, ".page-numbers.next")
            next_page_url = next_button.get_attribute("href")
            if not next_page_url:
                print("No next page URL found. Exiting.")
                break
            driver.get(next_page_url)
            print("Navigated to next page.")
            time.sleep(3)
        except:
            print("No more pages.")
            break


def format_data_for_sheet(data):
    formatted_data = []
    for item in data:
        row = {
            "Website Name": "Ampco Flashlight",
            "Product URL": item.get("product_url", ""),
            "Product Category": item.get("category", ""),
            "Title": item.get("title", ""),
            "Quantity": "N/A",
            "Ex VAT Price": item.get("ex_vat_price", ""),
            "Inc VAT Price": "N/A",
            "Currency": "EUR",
            "Brand": "N/A",
            "Condition": item.get("condition", ""),
            "Product Description": item.get("description", "")
        }
        for i in range(1, 8):
            try:
                img = item["images"][i - 1]
            except Exception:
                img = "N/A"
            row[f"Image Src {i}"] = img
            row[f"Image Position {i}"] = i

        formatted_data.append(row)
    return pd.DataFrame(formatted_data)

def to_csv(extracted_data):
    df = pd.DataFrame(extracted_data)
    try:
        df.to_csv("final15.csv", index=False)
        print("CSV saved: 3.csv")
    except:
        print("Error while creating CSV file")


def scrape():
    extracted_data = []

    try:
        driver = webdriver.Chrome()
        driver.get('https://www.ampco-flashlight.com/en/store/')
        time.sleep(3)

        extracting_detail(driver, extracted_data)

        to_csv(extracted_data)
        df = format_data_for_sheet(extracted_data)
        # if not df.empty:
        #     upload_to_google_sheets(df, SHEET_NAME, CRED_JSON, worksheet_name="ampco-flashlight.com")
        # else:
        #     print(" No data extracted.")
    except Exception as e:
        print(f"Scraping failed: {e}")
    finally:
        driver.quit()
        print("Scraping completed and browser closed.")


scrape()
