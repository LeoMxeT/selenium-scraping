
import csv
import os
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def get_pages(driver, url):
    #masivi linkebistvis
    page_urls = []

    driver.get(url)
    WebDriverWait(driver, 10)
    
    page = 0
    try:
        while page < 7:
            page += 1
            url = f"https://veli.store/category/teqnika/mobilurebi-aqsesuarebi/mobiluri-telefonebi/60/?page={page}"    
            page_urls.append(url)
            # print(page_urls)
    except Exception as e:
        print("error generating page")

    return page_urls   


def get_product_urls(driver, page):

    product_urls = []
    
    for url in page:
    
        driver.get(url)

        # wait for page to load
        wait = WebDriverWait(driver, 10)

        try:
            products = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".styled__CardWrapper-sc-1gjp82p-0.eknzBd")
            ))
        except Exception as e:
            print("Error waiting for product elements:", e)
            return None
        
        if products:
            for product in products:
                try:
                    anchor = product.find_element(By.TAG_NAME, "a")
                    prd_url = anchor.get_attribute("href")
                    print(prd_url)
                    product_urls.append(prd_url)
                except Exception as e:
                    print("error extracting url from product.")
    return product_urls
   


def get_product_details(driver, urls):
    product_details = []
    for url in tqdm(urls):

        driver.get(url)

        # wait for page to load
        wait = WebDriverWait(driver, 10)
        details = {}


        try:
            image = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".styled__PictureSlide-sc-1arg8l9-12.iSoEUK img")))
            image_url = image.get_attribute("src")
            details["image_url"] = image_url

            title = driver.find_element("css selector", "h1.title")
            details["title"] = title.text

            productid = driver.find_element(By.CLASS_NAME, 'product-id')
            details["productid"] = productid.text

            price = driver.find_element(By.CLASS_NAME, "price")
            newprice = driver.execute_script("return arguments[0].childNodes[0].textContent;", price)
            details["price"] = float(newprice)


            description = driver.find_elements(By.CSS_SELECTOR, ".server_html li")
            details["description"] = [element.text for element in description]

            product_details.append(details)

        except Exception as e:
            print(e)
            continue

    return product_details


def save_to_csv(file_name, field_names,product_details):
    for product in product_details:
            with open(file_name, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=field_names)
                writer.writeheader()
                for product in product_details:
                    writer.writerow(product)


if __name__ == '__main__':

    options = Options()
    options.add_argument("--headless") 
    driver = webdriver.Chrome(options=options)

    url = f"https://veli.store/category/teqnika/mobilurebi-aqsesuarebi/mobiluri-telefonebi/60/?page=1"
    page = get_pages(driver, url)
    urls = get_product_urls(driver, page)
    file_name = "products.csv"
    field_names = ["image_url", "title", "productid", "price", "description"]

    if urls:
        # get product details
        product_details = get_product_details(driver, urls)
        save_to_csv(file_name, field_names,product_details)
    else:
        print("no product found.")

    
    
    
    
    driver.quit()
