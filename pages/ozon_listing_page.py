# -*- coding: utf-8 -*-
"""Ozon 一键刊登编辑页。与 WB 刊登页字段相近，打开判定只认 Ozon 路由。"""
from __future__ import annotations

import time

from selenium.webdriver.support.ui import WebDriverWait

import config
from pages.listing_page import WbListingPage


class OzonListingPage(WbListingPage):
    def is_open(self) -> bool:
        url = (self.url() or "").lower()
        if config.WB_LISTING_URL_MARK in url:
            return False
        if any(m in url for m in config.OZON_LISTING_URL_MARKS):
            return True
        if "ozon" in url and "listing" in url:
            return True
        text = self.page_text() or ""
        return ("Ozon 一键刊登" in text or "OZON 一键刊登" in text) and "wb-one-click-listing" not in url

    def wait_open(self, timeout=None):
        timeout = timeout or config.PULL_WAIT
        WebDriverWait(self.driver, timeout).until(lambda d: self.is_open())
        time.sleep(0.8)
        return self

    def steps_present(self) -> bool:
        text = self.page_text()
        if all(k in text for k in ("基本信息", "产品属性", "变体设置")):
            return True
        return any(k in text for k in ("Ozon 一键刊登", "OZON 一键刊登", "商品信息", "基本信息"))
