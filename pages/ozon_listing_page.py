# -*- coding: utf-8 -*-
"""Ozon 一键刊登编辑页。打开判定只认 Ozon 路由，不用 WB 页 URL。"""
from __future__ import annotations

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import config
from pages.listing_page import WbListingPage


class OzonListingPage(WbListingPage):
    CN_TITLE = (
        By.CSS_SELECTOR,
        "textarea[placeholder*='标题'], input[placeholder*='标题'], "
        "textarea[placeholder*='中文'], input[placeholder*='中文']",
    )
    RU_TITLE = (
        By.CSS_SELECTOR,
        "textarea[placeholder*='俄'], input[placeholder*='俄'], "
        "textarea[placeholder*='OZON'], input[placeholder*='OZON']",
    )

    def is_open(self) -> bool:
        url = (self.url() or "").lower()
        if config.WB_LISTING_URL_MARK in url:
            return False
        if "collection" in url and "ozon" not in url:
            return False
        if any(m in url for m in config.OZON_LISTING_URL_MARKS):
            return True
        if "ozon" in url and any(k in url for k in ("listing", "publish", "one-click", "card")):
            return True
        text = self.page_text() or ""
        heads = ("Ozon 一键刊登", "OZON 一键刊登", "Ozon商品刊登", "OZON商品刊登")
        return any(h in text for h in heads) and config.WB_LISTING_URL_MARK not in url

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

    def _title_loc(self):
        if self.finds(self.CN_TITLE):
            return self.CN_TITLE
        for xp in (
            "//*[normalize-space()='标题（中文）']/following::textarea[1]",
            "//*[contains(normalize-space(),'标题')]/following::textarea[1]",
            "//*[contains(normalize-space(),'标题')]/following::input[not(@type='hidden')][1]",
        ):
            loc = (By.XPATH, xp)
            if self.finds(loc):
                return loc
        return self.CN_TITLE

    def fill_cn_title(self, value: str):
        loc = self._title_loc()
        if self.finds(loc):
            self.fill(loc, value)
        return self

    def fill_ru_title(self, value: str):
        loc = self.RU_TITLE
        if not self.finds(loc):
            loc = (By.XPATH, "//*[contains(normalize-space(),'俄')]/following::textarea[1]")
        if self.finds(loc):
            self.fill(loc, value)
        return self

    def cn_title_value(self) -> str:
        loc = self._title_loc()
        els = self.finds(loc)
        return (els[0].get_attribute("value") or "") if els else ""

    def listing_prices(self):
        els = super().listing_prices()
        if els:
            return els
        extra = (
            (By.XPATH, "//input[@aria-label='售价']"),
            (By.XPATH, "//input[@placeholder='售价']"),
            (By.XPATH, "//*[normalize-space()='售价']/following::input[not(@type='hidden')][1]"),
            (By.XPATH, "//*[contains(normalize-space(),'价格')]/following::input[not(@type='hidden')][1]"),
        )
        for loc in extra:
            vis = [e for e in self.driver.find_elements(*loc) if e.is_displayed()]
            if vis:
                return vis
        return []

    def sku_row_count(self) -> int:
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".el-table__body tr")
        n = len([r for r in rows if r.is_displayed() and (r.text or "").strip()])
        return n if n else super().sku_row_count()

    def _blank(self, el):
        self.driver.execute_script(
            """
            const el = arguments[0];
            const proto = el.tagName === 'TEXTAREA'
                ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
            const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
            setter.call(el, '');
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            """,
            el,
        )

    def _set_input(self, el, value: str):
        self.driver.execute_script(
            """
            const el = arguments[0], val = arguments[1];
            const proto = el.tagName === 'TEXTAREA'
                ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
            const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            """,
            el,
            value,
        )

    def clear_category(self):
        item = self.form_item("产品类目")
        if item is not None:
            for css in (".el-input__clear", ".el-icon-circle-close", "[class*='circle-close']"):
                for ic in item.find_elements(By.CSS_SELECTOR, css):
                    try:
                        if ic.is_displayed():
                            self.driver.execute_script("arguments[0].click();", ic)
                    except Exception:
                        pass
        els = self.finds(self.CATEGORY_INPUT)
        if not els and item is not None:
            els = item.find_elements(By.CSS_SELECTOR, "input, textarea")
        if not els:
            raise AssertionError("未找到产品类目输入")
        self._blank(els[0])
        return self

    def _weight_el(self):
        els = [e for e in self.finds(self.WEIGHT) if e.is_displayed()]
        if not els:
            els = [
                e
                for e in self.driver.find_elements(
                    By.XPATH, "//*[contains(normalize-space(),'包装重量')]/following::input[1]"
                )
                if e.is_displayed()
            ]
        return els[0] if els else None

    def set_weight(self, value: str):
        el = self._weight_el()
        if el is None:
            raise AssertionError("未找到包装重量")
        self._set_input(el, value)
        return self

    def clear_weight(self):
        return self.set_weight("")

    def _dim_els(self):
        return [e for e in self.finds(self.DIMS) if e.is_displayed()][:3]

    def clear_dims(self):
        els = self._dim_els()
        if not els:
            raise AssertionError("未找到包装尺寸")
        for el in els:
            self._blank(el)
        return self

    def title_cap(self) -> int | None:
        import re

        els = self.finds(self._title_loc())
        if els:
            raw = els[0].get_attribute("maxlength") or ""
            if raw.isdigit() and int(raw) > 0:
                return int(raw)
        nums = [int(n) for n in re.findall(r"/\s*(\d{2,4})", self.page_text() or "")]
        return min(nums) if nums else None
