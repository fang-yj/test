import contextlib
import uuid
from pathlib import Path
from typing import Any

import ipapi
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from constants import desktopUserAgent


class Browser:
    """WebDriver wrapper class."""

    def __init__(self, args: Any) -> None:
        self.headless = True
        self.localeLang, self.localeGeo = self.getCCodeLang(args.lang, args.geo)
        self.userAgent = desktopUserAgent()
        self.webdriver = self.browserSetup()

    def __enter__(self) -> "Browser":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.closeBrowser()

    def closeBrowser(self) -> None:
        """Perform actions to close the browser cleanly."""
        # close web browser
        with contextlib.suppress(Exception):
            self.webdriver.quit()

    def browserSetup(self) -> WebDriver:
        driver_path = ChromeDriverManager().install()
        print(driver_path)
        service = Service(driver_path)
        options = Options()
        options.add_argument(f"user-agent={self.userAgent}")
        options.add_argument(f"lang={self.localeLang}")
        if self.headless:
            options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_argument("log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(service=service, options=options)
        with open("stealth.min.js", "r") as f:
            js = f.read()
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js})
        return driver

    def getCCodeLang(self, lang: str, geo: str) -> tuple:
        if lang is None or geo is None:
            try:
                nfo = ipapi.location()
                if isinstance(nfo, dict):
                    if lang is None:
                        lang = nfo["languages"].split(",")[0].split("-")[0]
                    if geo is None:
                        geo = nfo["country"]
            except Exception:  # pylint: disable=broad-except
                return ("en", "US")
        return (lang, geo)
