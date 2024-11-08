import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from geetest_slider_solver.identifier import GeeTestIdentifier
from geetest_slider_solver.utils import CAPTCHA_REGEX_URL_PATTERN, move_slider_smoothly


def captcha_solver(driver: Chrome | Firefox, **kwargs) -> None:
    geetest_elements_mapping = {
        "background": "div.geetest_bg",
        "slice": "div.geetest_slice_bg",
    }
    geetest_elemets_urls = {"background_url": "", "slice_url": ""}

    driver.set_page_load_timeout(10)  # Set a longer page load timeout
    driver.set_script_timeout(10)  # Set a longer script timeout
    while True:
        element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.geetest_btn"))
        )
        if element.is_displayed():
            time.sleep(1.0)
            break
        else:
            time.sleep(1.0)
            continue

    for key, value in geetest_elements_mapping.items():
        element = driver.find_element(By.CSS_SELECTOR, value)
        style_attribute = element.get_attribute("style")
        url = re.search(CAPTCHA_REGEX_URL_PATTERN, style_attribute)
        if url:
            geetest_elemets_urls[f"{key}_url"] = url.group(1)

    res = GeeTestIdentifier.test(**geetest_elemets_urls)
    slider_button = driver.find_element(By.CSS_SELECTOR, "div.geetest_btn")
    move_slider_smoothly(
        driver, slider_button, res["position_from_left"] - 40, **kwargs
    )
