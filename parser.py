from typing import List, Dict, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait


def fetch_image_urls(images: List[WebElement]) -> List[str]:
    links = []
    for image in images:
        img = image.find_element(By.TAG_NAME, "img")
        if img:
            img_link = img.get_attribute("src")
            if img_link not in links:
                links.append(img_link)
    return links


def check_availability(driver) -> Tuple[bool | str, str | int]:
    try:
        is_available = driver.find_element(By.CLASS_NAME, "level-indicator-message")
        status = is_available.find_element(
            By.CSS_SELECTOR, "span[data-flow-stock-count]"
        )
        if status.text.isdigit():
            return int(status) > 0, status
        else:
            status, "Unkown"
    except NoSuchElementException:
        return False, "Unknown"


def parse_money(driver: webdriver.Chrome) -> List[Dict[str, str]]:
    prices = []
    wait = WebDriverWait(driver, 5)
    variants_count = len(
        driver.find_elements(By.CSS_SELECTOR, ".swatch-element.variant-swatch")
    )
    if variants_count == 0:
        # If there is only one variant, we can just get the price directly
        price = driver.find_element(By.CLASS_NAME, "money").text.strip()
        return [{"variantName": "Default", "price": price}]

    for i in range(variants_count):
        # We need to re-find the variants each time because when we click on a variant,
        # the DOM updates the old list of variants with the new one, so
        # thats why we cant access to the old variants list.
        variants = driver.find_elements(
            By.CSS_SELECTOR, ".swatch-element.variant-swatch"
        )
        v = variants[i]
        variant_name = v.text.strip()
        # I realized that here I should track the old price because when clicking
        # on variants one by one, the price changes and DOM updates
        # if I dont track the old price, then I wont get the price because
        # DOM invalidates the old variant web element.
        old_price = driver.find_element(By.CLASS_NAME, "money").text.strip()

        try:
            v.click()
            # here after clicking, we shold wait for the price to change
            wait.until(
                lambda d: d.find_element(By.CLASS_NAME, "money").text.strip()
                != old_price
            )
        except:
            continue

        new_price = driver.find_element(By.CLASS_NAME, "money").text.strip()
        prices.append({"variantName": variant_name, "price": new_price})

    return prices


def parse_drinks(url: str) -> Dict:
    with webdriver.Chrome() as driver:
        driver.get(url)
        images = driver.find_elements(By.CSS_SELECTOR, "a[data-main-media-link]")
        extracted_images = fetch_image_urls(images)
        available, in_stock = check_availability(driver)
        final_result = {
            "images": extracted_images,
            "isAvailable": available,
            "inStock": in_stock,
            "prices": parse_money(driver),
        }
        return final_result


print(parse_drinks("https://drinkstore.ie/collections/cocktails-mix/products/1770"))
