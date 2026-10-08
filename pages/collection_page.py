# -*- coding: utf-8 -*-
from __future__ import annotations

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import config
from pages.base_page import BasePage


class CollectionPage(BasePage):
    LINK_INPUT = (
        By.CSS_SELECTOR,
        "textarea[placeholder*='1688'], input[placeholder*='1688']",
    )
    PULL = (By.XPATH, "//button[normalize-space()='拉取商品']")
    ONE_CLICK = (By.XPATH, "//button[normalize-space()='一键刊登']")
    DETAIL = (By.XPATH, "//button[normalize-space()='查看详情']")
    ORIGIN = (By.XPATH, "//a[contains(., '1688 原链接')]")
    TAB_MANUAL = (By.XPATH, "//button[normalize-space()='手动采集']")
    TAB_LINK = (By.XPATH, "//button[normalize-space()='1688商品链接采集']")
    TAB_1688 = (By.XPATH, "//button[normalize-space()='1688精选']")
    TAB_JD = (By.XPATH, "//button[normalize-space()='京东精选']")
    TAB_TB = (By.XPATH, "//button[normalize-space()='淘宝精选']")
    MENU_WB = (By.XPATH, "//li[@role='menuitem' and contains(., 'WB')]")
    MENU_OZON = (By.XPATH, "//li[@role='menuitem' and contains(., 'Ozon')]")

    def open_collect(self):
        self.goto_hash(config.HASH_COLLECT, "1688商品链接采集")
        if self.finds(self.TAB_MANUAL):
            try:
                self.js_click(self.finds(self.TAB_MANUAL)[0])
            except Exception:
                pass
        if self.finds(self.TAB_LINK):
            try:
                self.js_click(self.finds(self.TAB_LINK)[0])
            except Exception:
                pass
        return self

    def fill_links(self, text: str):
        self.fill(self.LINK_INPUT, text)
        return self

    def pull(self):
        self.js_click(self.clickable(self.PULL))
        return self

    def pull_and_wait_offer(self, offer_id: str = None, timeout=None):
        offer_id = offer_id or config.OFFER_ID
        timeout = timeout or config.PULL_WAIT
        self.pull()
        WebDriverWait(self.driver, timeout).until(
            lambda d: offer_id in self.page_text() or self.toast(0.1)
        )
        return self

    def ensure_card(self, link: str | None = None, offer_id: str | None = None):
        offer_id = offer_id or config.OFFER_ID
        self.open_collect()
        if offer_id in self.page_text() and self.finds(self.ONE_CLICK):
            return self
        self.fill_links(link or config.LINK_1688_SHORT)
        self.pull_and_wait_offer(offer_id)
        return self

    def card_visible(self, offer_id: str | None = None) -> bool:
        offer_id = offer_id or config.OFFER_ID
        return offer_id in self.page_text() and bool(self.finds(self.ONE_CLICK))

    def open_one_click_menu(self):
        btns = [b for b in self.finds(self.ONE_CLICK) if b.is_displayed()]
        if not btns:
            raise AssertionError("未找到「一键刊登」")
        self.js_click(btns[0])
        time.sleep(0.35)
        return self

    def listing_menu_texts(self) -> list[str]:
        self.open_one_click_menu()
        items = self.driver.find_elements(By.XPATH, "//li[@role='menuitem']")
        return [i.text.strip() for i in items if i.is_displayed() and i.text.strip()]

    def click_wb_listing(self):
        self.open_one_click_menu()
        items = [i for i in self.finds(self.MENU_WB) if i.is_displayed()]
        if not items:
            raise AssertionError("一键刊登下拉未出现「WB 平台」")
        self.js_click(items[0])
        WebDriverWait(self.driver, config.PULL_WAIT).until(
            lambda d: "wb-one-click-listing" in (d.current_url or "")
            or "Wildberries 一键刊登" in self.page_text()
        )
        time.sleep(0.6)
        return self

    def click_origin_link(self):
        links = [a for a in self.finds(self.ORIGIN) if a.is_displayed()]
        if not links:
            raise AssertionError("未找到「1688 原链接」")
        self.js_click(links[0])
        time.sleep(1.2)
        return self
