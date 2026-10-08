# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import time

from selenium.webdriver.common.by import By

import config
from pages.base_page import BasePage


class DraftPage(BasePage):
    TAB_DRAFT = (By.XPATH, "//*[@role='tab' and contains(., '草稿箱')]")
    TAB_NEED_FIX = (By.XPATH, "//*[@role='tab' and contains(., '待完善')]")
    TAB_READY = (By.XPATH, "//*[@role='tab' and contains(., '可刊登')]")
    BATCH_SUBMIT = (By.XPATH, "//button[normalize-space()='提交刊登']")
    ROW_SUBMIT = (By.XPATH, "//button[normalize-space()='提交刊登']")
    EDIT = (By.XPATH, "//button[normalize-space()='编辑']")
    VALIDATE = (By.XPATH, "//button[normalize-space()='批量校验']")

    def open(self):
        self.goto_hash(config.HASH_DRAFT, "草稿箱")
        time.sleep(0.8)
        return self

    def all_count(self) -> int:
        m = re.search(r"全部\s*(\d+)", self.page_text())
        return int(m.group(1)) if m else 0

    def first_row_text(self) -> str:
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".el-table__body tr, tbody tr")
        for r in rows:
            if r.is_displayed() and r.text.strip():
                return r.text
        return self.page_text()

    def wait_origin(self, keyword: str, timeout: int = 20) -> str:
        end = time.time() + timeout
        last = ""
        while time.time() < end:
            last = self.page_text()
            if keyword in last:
                return last
            time.sleep(0.8)
            self.open()
        raise AssertionError(f"草稿箱未出现来源「{keyword}」: {last[:500]}")

    def click_edit_for_origin(self, keyword: str):
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".el-table__body tr, tbody tr")
        for r in rows:
            if not r.is_displayed() or keyword not in (r.text or ""):
                continue
            btns = [
                b
                for b in r.find_elements(By.XPATH, ".//button[normalize-space()='编辑']")
                if b.is_displayed()
            ]
            if not btns:
                continue
            self.driver.execute_script("arguments[0].click();", btns[0])
            time.sleep(1)
            return self
        raise AssertionError(f"草稿箱没有来源含「{keyword}」的「编辑」")

    def click_edit(self):
        btns = [b for b in self.finds(self.EDIT) if b.is_displayed()]
        if not btns:
            raise AssertionError("草稿箱没有「编辑」")
        self.js_click(btns[0])
        time.sleep(1)
        return self

    def click_row_submit(self):
        btns = [b for b in self.finds(self.ROW_SUBMIT) if b.is_displayed()]
        # 第一个可能是顶部批量（disabled），取行内
        target = btns[-1] if btns else None
        if target is None:
            raise AssertionError("没有提交刊登按钮")
        self.js_click(target)
        time.sleep(0.8)
        return self.toast() or self.page_text()

    def batch_submit_disabled(self) -> bool:
        tops = self.driver.find_elements(
            By.XPATH, "//button[normalize-space()='提交刊登']"
        )
        if not tops:
            return True
        first = tops[0]
        return (not first.is_enabled()) or ("is-disabled" in (first.get_attribute("class") or ""))

    def tab_counts(self) -> dict:
        text = self.page_text()
        result = {}
        for name in ("待完善", "可刊登", "全部"):
            result[name] = name in text
        return result
