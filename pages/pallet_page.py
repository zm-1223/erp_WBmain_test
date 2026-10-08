# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

import config
from pages.base_page import BasePage
from utils.package_fields import parse_package


class PalletPage(BasePage):
    SEARCH = (By.CSS_SELECTOR, "input[placeholder*='标题'], input[placeholder*='skuId']")
    QUERY = (By.XPATH, "//button[normalize-space()='查询']")
    RESET = (By.XPATH, "//button[normalize-space()='重置']")
    BATCH_DRAFT = (By.XPATH, "//button[normalize-space()='批量生成草稿']")
    SELECT_ALL = (By.XPATH, "//*[normalize-space()='本页全选']")
    ONE_CLICK = (By.XPATH, "//button[normalize-space()='一键刊登']")
    ONE_CLICK_BTN = (By.XPATH, "//button[contains(normalize-space(), '一键刊登')]")
    ONE_CLICK_LOCS = (
        (By.XPATH, "//button[contains(normalize-space(), '一键刊登')]"),
        (By.XPATH, "//*[contains(@class,'el-dropdown') and contains(., '一键刊登')]"),
        (
            By.XPATH,
            "//*[self::button or self::span or self::a or self::div]"
            "[contains(normalize-space(), '一键刊登')]",
        ),
    )
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

    def one_click_elements(self):
        found = []
        seen = set()
        for loc in self.ONE_CLICK_LOCS:
            for el in self.finds(loc):
                try:
                    if not el.is_displayed():
                        continue
                    ident = el.id
                    if ident in seen:
                        continue
                    seen.add(ident)
                    found.append(el)
                except Exception:
                    continue
        return found

    def has_goods(self) -> bool:
        if self.one_click_elements():
            return True
        text = self.page_text() or ""
        if re.search(r"offerId\s*[：:]\s*\d+", text, re.I):
            return True
        if re.search(r"skuId\s*[：:]\s*\d+", text, re.I):
            return True
        return False

    def wait_loaded(self, which: str, timeout=20):
        empty = self.empty_text(which)
        end = time.time() + timeout
        while time.time() < end:
            if self.has_goods():
                self._wait_one_click_clickable(timeout=8)
                return self
            if empty in self.page_text() and not self.one_click_elements():
                time.sleep(0.8)
                if self.has_goods():
                    self._wait_one_click_clickable(timeout=8)
                    return self
                if empty in self.page_text():
                    return self
            time.sleep(0.4)
        return self

    def _wait_one_click_clickable(self, timeout=15):
        try:
            return self.clickable(self.ONE_CLICK_BTN, timeout)
        except TimeoutException:
            els = [b for b in self.one_click_elements() if b.is_displayed()]
            if els:
                return els[0]
            raise AssertionError("一键刊登按钮未出现或不可点击")

    def click_batch_draft(self, confirm: bool = True):
        self.button("批量生成草稿")
        tip = self.popup_text(timeout=2) or self.toast()
        if confirm:
            self.confirm_popups()
        else:
            self.cancel_popups()
        time.sleep(0.8)
        return tip or self.toast() or self.page_text()

    def select_first(self, n: int = 1) -> int:
        self.dismiss_popups()
        css_list = (
            ".el-table__body .el-checkbox",
            ".el-table__row .el-checkbox",
            ".el-card .el-checkbox",
            "[class*='card'] .el-checkbox",
            "[class*='goods'] .el-checkbox",
        )
        boxes = []
        for css in css_list:
            boxes.extend(self.driver.find_elements(By.CSS_SELECTOR, css))
        if not boxes:
            boxes = self.driver.find_elements(By.CSS_SELECTOR, ".el-checkbox")
        clicked = 0
        for box in boxes:
            try:
                if not box.is_displayed():
                    continue
                cls = box.get_attribute("class") or ""
                if "is-disabled" in cls:
                    continue
                parent_txt = (box.text or "") + (box.get_attribute("innerText") or "")
                wrap = box.find_element(By.XPATH, "./ancestor::*[self::label or self::div][1]")
                wrap_txt = (wrap.text or "") if wrap is not None else ""
                if "全选" in parent_txt or "全选" in wrap_txt:
                    continue
                self.driver.execute_script("arguments[0].click();", box)
                clicked += 1
                if clicked >= n:
                    break
            except Exception:
                continue
        if clicked == 0:
            self.select_all()
        time.sleep(0.3)
        return clicked

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

    def first_item_text(self) -> str:
        btns = self.one_click_elements()
        if not btns:
            return self.page_text()
        el = btns[0]
        xps = (
            "./ancestor::*[contains(@class,'el-card')][1]",
            "./ancestor::tr[1]",
            "./ancestor::*[contains(@class,'el-table__row')][1]",
            "./ancestor::div[contains(@class,'item') or contains(@class,'goods')][1]",
            "./ancestor::div[5]",
        )
        for xp in xps:
            try:
                node = el.find_element(By.XPATH, xp)
                txt = (node.text or "").strip()
                if txt:
                    return txt
            except Exception:
                continue
        return self.page_text()

    def detail_text(self) -> str:
        btns = [
            b
            for b in self.driver.find_elements(
                By.XPATH, "//button[contains(normalize-space(), '查看详情')]"
            )
            if b.is_displayed()
        ]
        if not btns:
            return ""
        self.js_click(btns[0])
        time.sleep(0.8)
        blob = ""
        for css in (".el-drawer", ".el-dialog"):
            for el in self.driver.find_elements(By.CSS_SELECTOR, css):
                if el.is_displayed() and (el.text or "").strip():
                    blob = el.text
                    break
            if blob:
                break
        self.dismiss_popups()
        time.sleep(0.2)
        return blob

    def source_package(self) -> dict:
        return parse_package(f"{self.first_item_text()}\n{self.detail_text()}")

    def _visible_dropdown_items(self):
        items = []
        locators = (
            (By.CSS_SELECTOR, ".el-popper[aria-hidden='false'] li"),
            (By.CSS_SELECTOR, ".el-popper[aria-hidden='false'] .el-dropdown-menu__item"),
            (By.XPATH, "//li[@role='menuitem']"),
            (By.CSS_SELECTOR, ".el-dropdown-menu__item"),
        )
        seen = set()
        for loc in locators:
            for el in self.driver.find_elements(*loc):
                try:
                    if not el.is_displayed():
                        continue
                    ident = el.id
                    if ident in seen:
                        continue
                    seen.add(ident)
                    if (el.text or "").strip():
                        items.append(el)
                except Exception:
                    continue
        return items

    def _dropdown_open(self) -> bool:
        if self._visible_dropdown_items():
            return True
        return bool(
            self.driver.execute_script(
                """
                const nodes = [...document.querySelectorAll(
                  '.el-popper, .el-dropdown-menu, [role=menu], li[role=menuitem], .el-dropdown-menu__item'
                )];
                return nodes.some((n) => {
                  if (n.getAttribute('aria-hidden') === 'true') return false;
                  const st = getComputedStyle(n);
                  if (st.display === 'none' || st.visibility === 'hidden') return false;
                  const r = n.getBoundingClientRect();
                  if (r.width < 8 || r.height < 8) return false;
                  return /WB|Wildberries|Ozon|OZON|平台/.test(n.innerText || '');
                });
                """
            )
        )

    def _wait_dropdown(self, timeout=5):
        end = time.time() + timeout
        while time.time() < end:
            if self._dropdown_open():
                return self._visible_dropdown_items()
            time.sleep(0.12)
        return []

    def _one_click_trigger_el(self):
        el = self.driver.execute_script(
            """
            const btns = [...document.querySelectorAll('button')].filter((b) =>
              b.offsetParent && (b.innerText || '').includes('一键刊登')
            );
            if (!btns.length) return null;
            btns.sort((a, b) =>
              (a.offsetWidth * a.offsetHeight) - (b.offsetWidth * b.offsetHeight)
            );
            return btns[0];
            """
        )
        if el is not None:
            return el
        return self._wait_one_click_clickable(timeout=15)

    def _trigger_one_click(self, el, mode: str):
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.12)
        if mode == "hover":
            ActionChains(self.driver).move_to_element(el).pause(0.4).perform()
            return
        if mode == "caret":
            try:
                caret = el.find_element(
                    By.XPATH,
                    "./ancestor::div[contains(@class,'el-dropdown')][1]"
                    "//button[contains(@class,'el-dropdown__caret-button')]",
                )
                ActionChains(self.driver).move_to_element(caret).pause(0.1).click().perform()
                return
            except Exception:
                pass
        try:
            ActionChains(self.driver).move_to_element(el).pause(0.15).click().perform()
        except Exception:
            self.raw_click(el)

    def open_one_click_menu(self):
        """等按钮可点后依次 click / hover / 箭头，再等下拉出现。"""
        self.dismiss_popups()
        time.sleep(0.15)
        for mode in ("click", "hover", "caret"):
            el = self._one_click_trigger_el()
            self._trigger_one_click(el, mode)
            if self._wait_dropdown(4):
                return self
        return self

    def _click_one_click_trigger(self):
        return self.open_one_click_menu()

    def _pick_menu(self, keywords: tuple[str, ...]) -> bool:
        for el in self._visible_dropdown_items():
            text = el.text or ""
            if any(k in text for k in keywords):
                self.driver.execute_script("arguments[0].click();", el)
                time.sleep(0.25)
                return True
        return self.click_menu_item(keywords, timeout=6)

    def click_wb_listing(self):
        keywords = ("WB 平台", "WB平台", "Wildberries")
        self.open_one_click_menu()
        if not self._pick_menu(keywords):
            raise AssertionError("未出现 WB 平台菜单")
        self.wait.until(
            lambda d: config.WB_LISTING_URL_MARK in (d.current_url or "")
        )
        time.sleep(0.6)
        return self

    def click_ozon_listing(self):
        self.open_one_click_menu()
        if not self._pick_menu(("Ozon 平台", "Ozon", "OZON")):
            raise AssertionError("未出现 Ozon 平台菜单")
        from pages.ozon_listing_page import OzonListingPage

        page = OzonListingPage(self.driver)
        try:
            page.wait_open()
        except Exception:
            time.sleep(1.2)
        return self.toast() or self.page_text() or self.url()

    def choose_ozon_shop(self):
        self.shop_options()
        items = self.driver.find_elements(
            By.CSS_SELECTOR, ".el-select-dropdown__item, [role='option']"
        )
        for o in items:
            t = (o.text or "").strip()
            if o.is_displayed() and t and "OZON" in t.upper():
                self.js_click(o)
                time.sleep(0.3)
                return t
        return ""

    def source_snapshot(self) -> dict:
        from utils.source_card import parse_source_card

        return parse_source_card(self.first_item_text())

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
