import json
import os
import pickle
from pathlib import Path

from playwright.sync_api import sync_playwright

from .constants import HOME_PAGE, SESSION_FILE
from .datacamp_utils import Datacamp


class Session:
    def __init__(self) -> None:
        self.savefile = Path(SESSION_FILE)
        self.datacamp = self.load_datacamp()

    def save(self):
        self.datacamp.session = None
        pickled = pickle.dumps(self.datacamp)
        self.savefile.write_bytes(pickled)

    def load_datacamp(self):
        if self.savefile.exists():
            datacamp = pickle.load(self.savefile.open("rb"))
            datacamp.session = self
            return datacamp
        return Datacamp(self)

    def reset(self):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass

    def _setup_driver(self, headless=True):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        self._context = self._browser.new_context()
        self.driver = self._context.new_page()

    def start(self, headless=False):
        if hasattr(self, "driver"):
            return
        self._setup_driver(headless)
        self.driver.goto(HOME_PAGE)
        if self.datacamp.token:
            self.add_token(self.datacamp.token)

    def get(self, url):
        self.start()
        self.driver.goto(url)
        return self.driver.content()

    def get_json(self, url):
        page = self.get(url)
        page = self.driver.locator("pre").first.text_content()
        parsed_json = self.to_json(page)
        return parsed_json

    def to_json(self, page: str):
        return json.loads(page)

    def get_element_by_id(self, id: str):
        # TODO: Implements
        pass

    def get_element_by_xpath(self, xpath: str):
        # TODO: Implements
        pass

    def click_element(self, id: str):
        # TODO: Implements
        pass

    def wait_for_element_by_css_selector(self, *css: str, timeout: int = 10):
        # TODO: Implements
        pass

    def add_token(self, token: str):
        cookie = {
            "name": "_dct",
            "value": token,
            "domain": ".datacamp.com",
            "path": "/",
            "secure": True,
        }
        self._context.add_cookies([cookie])
        return self
