import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from captcha_solver.geetest._identifier import GeeTestIdentifier
from captcha_solver.geetest._slider import move_slider_smoothly


CAPTCHA_REGEX_URL_PATTERN = r'url\("(.+?)"\)'


def slider_solver(driver: Chrome | Firefox, **kwargs) -> None:
    X_OFFSET = 40
    geetest_elements_mapping = {
        "background": "div.geetest_bg",
        "puzzle": "div.geetest_slice_bg",
    }
    geetest_elemets_urls = {"background_url": "", "puzzle_url": ""}

    driver.set_page_load_timeout(10)
    driver.set_script_timeout(10)

    tries = 5
    count = 0
    while tries < count:
        element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.geetest_btn"))
        )
        if element.is_displayed():
            time.sleep(1.0)
            break
        else:
            time.sleep(1.0)
            count += 1
            continue

    for key, value in geetest_elements_mapping.items():
        element = driver.find_element(By.CSS_SELECTOR, value)
        style_attribute = element.get_attribute("style")
        url = re.search(CAPTCHA_REGEX_URL_PATTERN, style_attribute)
        if url:
            geetest_elemets_urls[f"{key}_url"] = url.group(1)

    geetest_identifier = GeeTestIdentifier(**geetest_elemets_urls)
    res = geetest_identifier.find_puzzle_position()

    slider_button = driver.find_element(By.CSS_SELECTOR, "div.geetest_btn")
    move_slider_smoothly(
        driver, slider_button, res["position_from_left"] - X_OFFSET, **kwargs
    )
