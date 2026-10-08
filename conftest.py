# -*- coding: utf-8 -*-
"""会话级浏览器：整场测试只打开一次站点、只登录一次。失败自动截图并写入 Allure。"""
from __future__ import annotations

import time
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import config as app_cfg
from pages.collection_page import CollectionPage
from pages.draft_page import DraftPage
from pages.listing_page import WbListingPage
from pages.ozon_listing_page import OzonListingPage
from pages.login_page import LoginPage
from pages.base_page import BasePage, logger as page_logger
from pages.pallet_page import PalletPage


def pytest_configure(config):
    app_cfg.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    app_cfg.ALLURE_RESULTS.mkdir(parents=True, exist_ok=True)
    app_cfg.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    app_cfg.LOG_DIR.mkdir(parents=True, exist_ok=True)


def _build_driver():
    options = Options()
    if app_cfg.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=zh-CN")
    w, h = (app_cfg.WINDOW_SIZE.split(",") + ["900"])[:2]
    options.add_argument(f"--window-size={w},{h}")
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(app_cfg.IMPLICIT_WAIT)
    return driver


@pytest.fixture(scope="session")
def driver():
    """全量用例共用一个 Chrome，避免重复打开网站。"""
    drv = _build_driver()
    drv.get(app_cfg.BASE_URL + "/" + app_cfg.HASH_COLLECT)
    LoginPage(drv).login()
    CollectionPage(drv).open_collect()
    yield drv
    if not app_cfg.KEEP_BROWSER:
        try:
            drv.quit()
        except Exception:
            pass


@pytest.fixture(scope="session")
def collect_page(driver):
    return CollectionPage(driver)


@pytest.fixture(scope="session")
def pallet_page(driver):
    return PalletPage(driver)


@pytest.fixture(scope="session")
def wb_listing_page(driver):
    return WbListingPage(driver)


@pytest.fixture(scope="session")
def ozon_listing_page(driver):
    return OzonListingPage(driver)


@pytest.fixture(scope="session")
def listing_page(wb_listing_page):
    """兼容旧名，等同 wb_listing_page。"""
    return wb_listing_page


@pytest.fixture(scope="session")
def draft_page(driver):
    return DraftPage(driver)


@pytest.fixture(autouse=True)
def _dismiss_popups_before_test(request):
    if request.node.get_closest_marker("no_browser"):
        return
    driver = request.getfixturevalue("driver")
    BasePage(driver).dismiss_popups()
    page_logger.info("用例开始，已尝试兜底关弹窗")


@pytest.fixture
def on_collect(collect_page):
    collect_page.open_collect()
    return collect_page


@pytest.fixture
def wb_listing_from_1688(collect_page, wb_listing_page):
    """每次从1688卡片重新进入 WB 刊登编辑页，避免上一例改过的脏表单。"""
    page_logger.info("重新从1688进入 WB 刊登页，避免复用脏表单")
    collect_page.ensure_card()
    collect_page.click_wb_listing()
    wb_listing_page.wait_open()
    return wb_listing_page


@pytest.fixture
def listing_from_1688(wb_listing_from_1688):
    """兼容旧名，等同 wb_listing_from_1688。"""
    return wb_listing_from_1688


@pytest.fixture
def ozon_listing_from_1688(collect_page, ozon_listing_page):
    """每次从1688卡片重新进入 Ozon 刊登编辑页。"""
    page_logger.info("重新从1688进入 Ozon 刊登页，避免复用脏表单")
    collect_page.ensure_card()
    collect_page.click_ozon_listing()
    try:
        ozon_listing_page.wait_open()
    except Exception:
        pytest.skip("未进入 Ozon 刊登页（需 OZON 店铺或平台入口）")
    return ozon_listing_page


def _attach_failure(item, when: str):
    driver = item.funcargs.get("driver")
    if driver is None:
        return
    name = f"{item.name}_{when}_{int(time.time())}"
    png_path = app_cfg.SCREENSHOT_DIR / f"{name}.png"
    try:
        driver.save_screenshot(str(png_path))
        allure.attach.file(
            str(png_path),
            name=f"失败截图-{when}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        try:
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"失败截图-{when}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
    try:
        allure.attach(
            driver.current_url or "",
            name="URL",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            driver.page_source or "",
            name="Page Source",
            attachment_type=allure.attachment_type.HTML,
        )
    except Exception:
        pass


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
    if rep.failed and rep.when in ("setup", "call", "teardown"):
        page_logger.error("用例失败 %s when=%s", item.name, rep.when)
        _attach_failure(item, rep.when)
