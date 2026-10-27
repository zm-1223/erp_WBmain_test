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
        return self.open_wb()

    def open_wb(self):
        self.goto_hash(config.HASH_DRAFT, "草稿箱")
        time.sleep(0.8)
        return self

    def open_ozon(self):
        for hash_path in (
            config.HASH_OZON_DRAFT,
            "#/goods/publish?tab=ozon/draft",
            "#/goods/publish?tab=ozon-draft",
        ):
            self.goto_hash(hash_path, "草稿")
            if "ozon" in (self.url() or "").lower():
                time.sleep(0.8)
                return self
        raise AssertionError(f"未打开 Ozon 草稿箱: {self.url()}")

    def all_count(self) -> int:
        m = re.search(r"全部\s*(\d+)", self.page_text())
        return int(m.group(1)) if m else 0

    def ready_count(self) -> int:
        m = re.search(r"可刊登\s*(\d+)", self.page_text())
        return int(m.group(1)) if m else 0

    def click_validate(self):
        btns = [b for b in self.finds(self.VALIDATE) if b.is_displayed()]
        if not btns:
            raise AssertionError("没有「批量校验」")
        self.js_click(btns[0])
        self.confirm_popups()
        time.sleep(2.2)
        return self.toast() or self.page_text()

    def first_row_text(self) -> str:
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".el-table__body tr, tbody tr")
        for r in rows:
            if r.is_displayed() and r.text.strip():
                return r.text
        return self.page_text()

    def wait_origin(self, keyword: str, timeout: int = 30, ozon: bool = False) -> str:
        end = time.time() + timeout
        last = ""
        while time.time() < end:
            last = self.page_text()
            if keyword in last:
                return last
            time.sleep(0.8)
            if ozon:
                self.open_ozon()
            else:
                self.open()
        raise AssertionError(f"草稿箱未出现来源「{keyword}」: {last[:500]}")

    def both_counts(self) -> tuple[int, int]:
        self.open()
        wb = self.all_count()
        self.open_ozon()
        return wb, self.all_count()

    def expect_one_draft_each(self, wb_before: int, oz_before: int, origin: str | None = None):
        """同江写入 WB 草稿箱一条，Minjin 写入 Ozon 草稿箱一条。不把「将写入 2」加在同一个箱子上。"""
        self.open()
        wb = self.wait_all_count_at_least(wb_before + 1)
        if origin:
            self.wait_origin(origin)
        self.open_ozon()
        oz = self.wait_all_count_at_least(oz_before + 1, ozon=True)
        if origin:
            self.wait_origin(origin, ozon=True)
        return wb, oz

    def wait_all_count_at_least(self, n: int, timeout: int = 25, ozon: bool = False) -> int:
        end = time.time() + timeout
        last = 0
        while time.time() < end:
            last = self.all_count()
            if last >= n:
                return last
            time.sleep(0.8)
            if ozon:
                self.open_ozon()
            else:
                self.open()
        raise AssertionError(f"草稿箱条数未增加，当前全部={last} 期望>={n}")

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

    def search_keyword(self, keyword: str):
        boxes = [
            e
            for e in self.driver.find_elements(
                By.CSS_SELECTOR, "input[placeholder*='标题'], input[placeholder*='货源']"
            )
            if e.is_displayed()
        ]
        if not boxes:
            return self
        self.driver.execute_script(
            """
            const el = arguments[0], val = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            """,
            boxes[0],
            keyword,
        )
        btns = [
            b
            for b in self.driver.find_elements(By.XPATH, "//button[normalize-space()='搜索']")
            if b.is_displayed()
        ]
        if btns:
            self.driver.execute_script("arguments[0].click();", btns[0])
            time.sleep(1)
        return self

    def reopen_edit(self, marker: str):
        """按标题搜这条草稿再点编辑。列表标题没换成修改值时，重置后点最新一条。"""
        self.search_keyword(marker[:12])
        time.sleep(0.6)
        if marker[:4] in self.page_text() and "编辑" in self.page_text():
            try:
                return self.click_edit_for_origin(marker[:4])
            except AssertionError:
                return self.click_edit()
        resets = [
            b
            for b in self.driver.find_elements(By.XPATH, "//button[normalize-space()='重置']")
            if b.is_displayed()
        ]
        if resets:
            self.driver.execute_script("arguments[0].click();", resets[0])
            time.sleep(1)
        return self.click_edit()

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
