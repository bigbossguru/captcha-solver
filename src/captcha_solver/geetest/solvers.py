import re
from lxml import etree
from captcha_solver.geetest._identifier import GeeTestIdentifier


CAPTCHA_REGEX_URL_PATTERN = r'url\("(.+?)"\)'


def slider_solver(html_content: str = None, background_url: str = None, puzzle_url: str = None, x_offset=40) -> tuple[int, dict]:
    """For Linux os install additional packges: python-lxml python3-opencv python3-dev"""

    geetest_elemets_urls = {"background_url": background_url, "puzzle_url": puzzle_url}

    if html_content:
        geetest_elements_mapping = {
            "background": "//div[contains(@class, 'geetest_bg')]",
            "puzzle": "//div[contains(@class, 'geetest_slice_bg')]",
        }

        tree = etree.HTML(html_content)
        for name, xpath in geetest_elements_mapping.items():
            elements = tree.xpath(xpath)

            for item in elements:
                url_attr = item.get("style")
                url = re.search(CAPTCHA_REGEX_URL_PATTERN, url_attr)
                if url:
                    geetest_elemets_urls[f"{name}_url"] = url.group(1)

    if all(geetest_elemets_urls.values()):
        geetest_identifier = GeeTestIdentifier(**geetest_elemets_urls)
        res = geetest_identifier.find_puzzle_position()

        return res["position_from_left"] - x_offset, res
    return 0, {}
