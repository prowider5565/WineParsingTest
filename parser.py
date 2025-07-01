from typing import List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def fetch_image_urls(images: List[WebElement]) -> List[str]:
    links = []
    for image in images:
        img = image.find_element(By.TAG_NAME, "img")
        if img:
            img_link = img.get_attribute("src")
            if img_link not in links:
                links.append(img_link)
    return links


def check_availability(element: WebElement):
    status = element.find_element(By.CSS_SELECTOR, "span[data-flow-stock-count]")
    print(status.text)


def parse_drinks(url: str) -> Tuple[List[WebElement], List[WebElement]]:
    with webdriver.Chrome() as driver:
        driver.get(url)
        isAvailable = driver.find_element(By.CLASS_NAME, "level-indicator-message")
        print(check_availability(isAvailable))
        # print(isAvailable)
        prices = driver.find_elements(By.CLASS_NAME, "money")
        images = driver.find_elements(By.CSS_SELECTOR, "a[data-main-media-link]")
        return prices, fetch_image_urls(images)


print(
    parse_drinks(
        "https://drinkstore.ie/products/mos-lager-330ml?variant=48986387546446"
    )[-1]
)
