# -*- coding: utf-8 -*-
from __future__ import annotations

import time

from selenium.webdriver.common.by import By

import config
from pages.base_page import BasePage


class PalletPage(BasePage):
    SEARCH = (By.CSS_SELECTOR, "input[placeholder*='标题'], input[placeholder*='skuId']")
    QUERY = (By.XPATH, "//button[normalize-space()='查询']")
    RESET = (By.XPATH, "//button[normalize-space()='重置']")
    BATCH_DRAFT = (By.XPATH, "//button[normalize-space()='批量生成草稿']")
    SELECT_ALL = (By.XPATH, "//*[normalize-space()='本页全选']")
    ONE_CLICK = (By.XPATH, "//button[normalize-space()='一键刊登']")
    VIEW_SOURCE = (By.XPATH, "//a[contains(., '查看货源')]")
    MENU_WB = (By.XPATH, "//li[@role='menuitem' and contains(., 'WB')]")
    CAT1 = (By.XPATH, "//*[normalize-space()='一级类目']")
    SORT_TIME = (By.XPATH, "//*[normalize-space()='同步时间']")
    SORT_PRICE = (By.XPATH, "//*[normalize-space()='货源价']")

    TABS = {
        "1688": (config.HASH_1688_PALLET, "1688精选"),
        "jd": (config.HASH_JD_PALLET, "京东精选"),
        "tb": (config.HASH_TB_PALLET, "淘宝精选"),
    }

    def open(self, which: str):
        hash_path, keyword = self.TABS[which]
        self.goto_hash(hash_path, keyword)
        time.sleep(1.2)
        return self

    def empty_text(self, which: str) -> str:
        mapping = {
            "1688": "暂无1688精选商品",
            "jd": "暂无京东精选商品",
            "tb": "暂无淘宝精选商品",
        }
        return mapping[which]

    def has_goods(self) -> bool:
        return any(b.is_displayed() for b in self.finds(self.ONE_CLICK))

    def wait_loaded(self, which: str, timeout=12):
        empty = self.empty_text(which)
        end = time.time() + timeout
        while time.time() < end:
            if self.has_goods() or empty in self.page_text():
                return self
            time.sleep(0.4)
        return self

    def click_batch_draft(self):
        self.button("批量生成草稿")
        time.sleep(0.6)
        return self.toast() or self.page_text()

    def search(self, keyword: str):
        self.fill(self.SEARCH, keyword)
        self.button("查询")
        time.sleep(1)
        return self

    def reset(self):
        self.button("重置")
        time.sleep(1)
        return self

    def select_all(self):
        nodes = self.finds(self.SELECT_ALL)
        if nodes:
            self.js_click(nodes[0])
        time.sleep(0.3)
        return self

    def shop_options(self) -> list[str]:
        combos = self.driver.find_elements(By.CSS_SELECTOR, ".el-select, [role='combobox']")
        for c in combos:
            txt = (c.text or "") + (c.get_attribute("textContent") or "")
            if "WB" in txt or "店铺" in txt or "WILDBERRIES" in txt or "OZON" in txt:
                self.js_click(c)
                time.sleep(0.4)
                break
        opts = self.driver.find_elements(By.CSS_SELECTOR, ".el-select-dropdown__item, [role='option']")
        return [o.text.strip() for o in opts if o.is_displayed() and o.text.strip()]

    def choose_wb_shop(self, name_part: str | None = None):
        self.shop_options()
        items = self.driver.find_elements(
            By.CSS_SELECTOR, ".el-select-dropdown__item, [role='option']"
        )
        preferred = []
        for o in items:
            t = (o.text or "").strip()
            if not o.is_displayed() or not t or "OZON" in t.upper():
                continue
            if "WB" in t or "WILDBERRIES" in t or config.WB_SHOP_NAME in t:
                preferred.append(o)
        if name_part:
            for o in preferred:
                if name_part in o.text:
                    self.js_click(o)
                    time.sleep(0.3)
                    return o.text
        if preferred:
            self.js_click(preferred[0])
            time.sleep(0.3)
            return preferred[0].text
        return ""

    def click_wb_listing(self):
        btns = [b for b in self.finds(self.ONE_CLICK) if b.is_displayed()]
        if not btns:
            raise AssertionError("精选列表没有「一键刊登」")
        self.js_click(btns[0])
        time.sleep(0.35)
        items = [i for i in self.finds(self.MENU_WB) if i.is_displayed()]
        if not items:
            raise AssertionError("未出现 WB 平台菜单")
        self.js_click(items[0])
        self.wait.until(
            lambda d: "wb-one-click-listing" in (d.current_url or "")
            or "Wildberries 一键刊登" in self.page_text()
        )
        time.sleep(0.6)
        return self

    def click_view_source(self):
        links = [a for a in self.finds(self.VIEW_SOURCE) if a.is_displayed()]
        if not links:
            raise AssertionError("未找到「查看货源」")
        self.js_click(links[0])
        time.sleep(1.2)
        return self

    def ui_controls_present(self) -> dict:
        text = self.page_text()
        return {
            "一级类目": "一级类目" in text,
            "二级类目": "二级类目" in text,
            "三级类目": "三级类目" in text,
            "查询": "查询" in text,
            "重置": "重置" in text,
            "同步时间": "同步时间" in text,
            "货源价": "货源价" in text,
            "目标店铺": "目标店铺" in text or "店铺" in text,
            "本页全选": "本页全选" in text,
            "批量生成草稿": "批量生成草稿" in text,
        }
