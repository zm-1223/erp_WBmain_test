# -*- coding: utf-8 -*-
from __future__ import annotations

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

import config
from pages.base_page import BasePage
from utils.package_fields import parse_number, same_num


class ListingPage(BasePage):
    CN_TITLE = (By.CSS_SELECTOR, "textarea[placeholder='请输入中文标题'], input[placeholder='请输入中文标题']")
    RU_TITLE = (
        By.CSS_SELECTOR,
        "textarea[placeholder*='WILDBERRIES'], input[placeholder*='WILDBERRIES']",
    )
    BRAND = (By.CSS_SELECTOR, "input[placeholder='可选']")
    WEIGHT = (By.XPATH, "//*[normalize-space()='包装重量 kg']/following::input[1]")
    DIMS = (By.XPATH, "//*[contains(normalize-space(),'包装尺寸')]/following::input")
    PREFIX = (By.CSS_SELECTOR, "input[placeholder='请输入商品编码前缀']")
    DESC = (By.XPATH, "//*[normalize-space()='描述']/following::textarea[1]")
    SOURCE_URL = (By.CSS_SELECTOR, "input[placeholder*='货源商品链接'], textarea[placeholder*='货源商品链接']")
    SOURCE_NOTE = (By.CSS_SELECTOR, "input[placeholder='非必填'], textarea[placeholder='非必填']")
    RU_SIZE = (By.CSS_SELECTOR, "input[placeholder='俄罗斯尺码']")
    PRICE = (By.XPATH, "//input[@placeholder='' and ancestor::*[contains(., '刊登价')]] | //input[contains(@aria-label,'刊登价')]")
    PRICE_NAMED = (By.CSS_SELECTOR, "input[name='刊登价'], input[placeholder='刊登价']")
    BARCODE = (By.CSS_SELECTOR, "input[placeholder='自动生成']")
    STOCK = (By.CSS_SELECTOR, ".el-input-number input")
    CLUB_BTN = (By.XPATH, "//button[contains(., 'WB Club')]")
    SAVE_DRAFT = (By.XPATH, "//button[normalize-space()='生成刊登草稿']")
    PUBLISH = (By.XPATH, "//button[contains(@class,'el-button--success') and normalize-space()='一键刊登']")
    CANCEL = (By.XPATH, "//button[normalize-space()='取消']")
    EXPAND_ATTR = (By.XPATH, "//button[contains(., '展开更多属性')]")
    CATEGORY_INPUT = (
        By.CSS_SELECTOR,
        "input[placeholder*='产品类目'], input[placeholder*='subject']",
    )

    def is_open(self) -> bool:
        # 只认编辑页 URL。草稿箱面包屑也含「Wildberries 一键刊登」，不能当已打开。
        return "wb-one-click-listing" in self.url()

    def wait_open(self, timeout=None):
        timeout = timeout or config.PULL_WAIT
        WebDriverWait(self.driver, timeout).until(
            lambda d: "wb-one-click-listing" in (d.current_url or "")
        )
        time.sleep(0.8)
        return self

    def form_item(self, label: str):
        xp = (
            f"//label[normalize-space()={self.quote(label)}]"
            "/ancestor::div[contains(@class,'el-form-item')][1]"
        )
        items = self.driver.find_elements(By.XPATH, xp)
        return items[0] if items else None

    def is_required(self, label: str) -> bool:
        item = self.form_item(label)
        if item is None:
            return False
        return "is-required" in (item.get_attribute("class") or "")

    def category_value(self) -> str:
        els = self.finds(self.CATEGORY_INPUT)
        if not els:
            item = self.form_item("产品类目")
            if item is not None:
                els = item.find_elements(By.CSS_SELECTOR, "input")
        if not els:
            return ""
        return (els[0].get_attribute("value") or "").strip()

    def has_recommend_badge(self) -> bool:
        item = self.form_item("产品类目")
        blob = (item.text if item is not None else "") + self.page_text()
        return "荐" in blob

    def package_weight_raw(self) -> str:
        els = [e for e in self.finds(self.WEIGHT) if e.is_displayed()]
        if not els:
            els = self.driver.find_elements(
                By.XPATH, "//*[contains(normalize-space(),'包装重量')]/following::input[1]"
            )
            els = [e for e in els if e.is_displayed()]
        if not els:
            return ""
        return (els[0].get_attribute("value") or "").strip()

    def package_dim_raws(self) -> list[str]:
        els = [e for e in self.finds(self.DIMS) if e.is_displayed()]
        vals = []
        for el in els[:3]:
            vals.append((el.get_attribute("value") or "").strip())
        while len(vals) < 3:
            vals.append("")
        return vals[:3]

    def listing_package(self) -> dict:
        return {
            "weight": parse_number(self.package_weight_raw()),
            "dims": [parse_number(x) for x in self.package_dim_raws()],
        }

    def assert_package_matches_source(self, entry: str, source: dict):
        """刊登页带入值须与原商品一致：货源有则相等，货源无则刊登页留空。"""
        src_w = source.get("weight")
        src_d = list(source.get("dims") or [None, None, None])
        while len(src_d) < 3:
            src_d.append(None)
        got = self.listing_package()
        if not same_num(src_w, got["weight"]):
            raise AssertionError(
                f"{entry} 包装重量与原商品不一致: 货源={src_w!r} 刊登页={got['weight']!r}"
                f"（原文={self.package_weight_raw()!r}）"
            )
        names = ("长", "宽", "高")
        for i, name in enumerate(names):
            if not same_num(src_d[i], got["dims"][i]):
                raise AssertionError(
                    f"{entry} 包装尺寸{name}与原商品不一致: 货源={src_d[i]!r} "
                    f"刊登页={got['dims'][i]!r}（原文={self.package_dim_raws()!r}）"
                )
        return got

    def has_recommended_category(self) -> bool:
        """任一入口进入刊登/草稿编辑页后，类目应已预填且带「荐」。"""
        value = self.category_value()
        placeholder = "选择 Wildberries" in value or value in ("", "选择")
        if placeholder and "当前类目" in self.page_text():
            tail = self.page_text().split("当前类目", 1)[-1][:40]
            placeholder = not any(ch in tail for ch in ("/", "服装", "用品", "电子"))
        return (not placeholder) and self.has_recommend_badge()

    def required_labels(self) -> list[str]:
        items = self.driver.find_elements(By.CSS_SELECTOR, ".el-form-item.is-required")
        labels = []
        for it in items:
            lab = it.find_elements(By.CSS_SELECTOR, ".el-form-item__label")
            if lab:
                labels.append(lab[0].text.strip())
        return [x for x in labels if x]

    def title_counter(self, which="cn") -> str:
        text = self.page_text()
        if which == "cn":
            # 形如 31 / 60
            pass
        return text

    def fill_cn_title(self, value: str):
        loc = self.CN_TITLE
        if not self.finds(loc):
            loc = (By.XPATH, "//*[normalize-space()='标题（中文）']/following::textarea[1]")
        self.fill(loc, value)
        return self

    def fill_ru_title(self, value: str):
        loc = self.RU_TITLE
        if not self.finds(loc):
            loc = (By.XPATH, "//*[normalize-space()='标题（俄语）']/following::textarea[1]")
        self.fill(loc, value)
        return self

    def cn_title_value(self) -> str:
        els = self.finds(self.CN_TITLE) or self.driver.find_elements(
            By.XPATH, "//*[normalize-space()='标题（中文）']/following::textarea[1]"
        )
        return els[0].get_attribute("value") or "" if els else ""

    def ru_title_value(self) -> str:
        els = self.finds(self.RU_TITLE) or self.driver.find_elements(
            By.XPATH, "//*[normalize-space()='标题（俄语）']/following::textarea[1]"
        )
        return els[0].get_attribute("value") or "" if els else ""

    def clear_titles(self):
        self.fill_cn_title("")
        self.fill_ru_title("")
        return self

    def source_url_value(self) -> str:
        els = self.finds(self.SOURCE_URL)
        if not els:
            els = self.driver.find_elements(
                By.XPATH, "//*[normalize-space()='货源地址']/following::input[1]"
            )
        return (els[0].get_attribute("value") or "") if els else ""

    def barcode_readonly(self) -> bool:
        els = self.finds(self.BARCODE)
        if not els:
            return False
        el = els[0]
        return bool(el.get_attribute("disabled") or el.get_attribute("readonly"))

    def barcode_value(self) -> str:
        els = self.finds(self.BARCODE)
        return (els[0].get_attribute("value") or "") if els else ""

    def ru_size_empty(self) -> bool:
        els = self.finds(self.RU_SIZE)
        if not els:
            return True
        return not any((e.get_attribute("value") or "").strip() for e in els)

    def fill_all_ru_size(self, value="42"):
        self.dismiss_popups()
        for el in self.finds(self.RU_SIZE):
            self.js_click(el)
            el.send_keys(Keys.CONTROL, "a")
            el.send_keys(value)
        return self

    def listing_prices(self):
        locs = (
            (By.XPATH, "//input[@aria-label='刊登价']"),
            (By.XPATH, "//input[@placeholder='刊登价']"),
            (By.XPATH, "//*[@role='textbox' and (@name='刊登价' or @aria-label='刊登价')]"),
            (By.XPATH, "//*[normalize-space()='刊登价']/following::input[not(@type='hidden')][1]"),
            (
                By.XPATH,
                "//*[contains(@class,'el-table') or contains(@class,'variant')]"
                "//input[contains(@class,'el-input__inner')]",
            ),
        )

        def _visible(loc):
            return [e for e in self.driver.find_elements(*loc) if e.is_displayed()]

        try:
            WebDriverWait(self.driver, 8).until(lambda d: any(_visible(loc) for loc in locs))
        except Exception:
            pass
        for loc in locs:
            els = _visible(loc)
            if els:
                return els
        found = self.driver.execute_script(
            """
            const nodes = [...document.querySelectorAll('input.el-input__inner, input')];
            return nodes.filter((el) => {
              if (!el.offsetParent) return false;
              const label = (el.getAttribute('aria-label') || el.placeholder || el.name || '');
              if (label.includes('刊登价')) return true;
              const cell = el.closest('td, .el-form-item, .el-table__cell');
              return cell && (cell.innerText || '').includes('刊登价');
            });
            """
        )
        return found or []

    def clear_first_price(self):
        self.dismiss_popups()
        try:
            self.driver.execute_script(
                "const n=[...document.querySelectorAll('*')].find(e=>e.innerText&&e.innerText.trim()==='刊登价');"
                "if(n) n.scrollIntoView({block:'center'});"
            )
        except Exception:
            pass
        prices = self.listing_prices()
        if not prices:
            raise AssertionError("未找到刊登价输入框")
        el = prices[0]
        self.js_click(el)
        try:
            el.send_keys(Keys.CONTROL, "a")
            el.send_keys(Keys.DELETE)
        except Exception:
            pass
        self.driver.execute_script(
            """
            const el = arguments[0];
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(el, '');
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            """,
            el,
        )
        return self

    def set_first_stock(self, value: str):
        self.dismiss_popups()
        stocks = self.driver.find_elements(By.CSS_SELECTOR, ".el-input-number input")
        # skip weight/dimension spinbuttons at top: pick ones near 库存
        if len(stocks) < 5:
            target = stocks[-1] if stocks else None
        else:
            target = stocks[4]
        if target is None:
            raise AssertionError("未找到库存输入")
        self.driver.execute_script(
            """
            const el = arguments[0], val = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            """,
            target,
            value,
        )
        return self

    def delete_all_images(self):
        buttons = self.driver.find_elements(By.XPATH, "//button[normalize-space()='删除']")
        for b in buttons[:8]:
            if b.is_displayed():
                try:
                    self.js_click(b)
                    time.sleep(0.15)
                except Exception:
                    pass
        return self

    def brand_optional(self) -> bool:
        return self.has_text("可选") and not self.is_required("品牌")

    def note_optional(self) -> bool:
        return bool(self.finds(self.SOURCE_NOTE)) or self.has_text("非必填")

    def save_draft(self):
        btns = [b for b in self.finds(self.SAVE_DRAFT) if b.is_displayed()]
        if not btns:
            raise AssertionError("未找到「生成刊登草稿」")
        self.js_click(btns[0])
        time.sleep(1.2)
        return self.toast() or self.page_text()

    def click_publish(self):
        btns = [b for b in self.finds(self.PUBLISH) if b.is_displayed()]
        if not btns:
            self.button("一键刊登")
        else:
            self.js_click(btns[-1])
        time.sleep(1)
        return self.toast() or self.page_text()

    def click_cancel(self):
        self.button("取消")
        time.sleep(0.8)
        return self

    def steps_present(self) -> bool:
        text = self.page_text()
        return all(k in text for k in ("基本信息", "产品属性", "变体设置"))

    def select_first_warehouse(self) -> bool:
        item = self.form_item("选择仓库")
        if item is None:
            return False
        try:
            combo = item.find_element(By.CSS_SELECTOR, ".el-select, [role='combobox']")
            self.js_click(combo)
            time.sleep(0.5)
        except Exception:
            return False
        opts = [
            o
            for o in self.driver.find_elements(
                By.CSS_SELECTOR, ".el-select-dropdown__item, [role='option']"
            )
            if o.is_displayed() and (o.text or "").strip()
        ]
        if not opts:
            return False
        self.js_click(opts[0])
        time.sleep(0.3)
        return True

    def expand_attrs(self):
        btns = self.finds(self.EXPAND_ATTR)
        if btns:
            self.driver.execute_script("arguments[0].click();", btns[0])
            time.sleep(0.4)
        return self

    def open_club_discount(self):
        btns = [b for b in self.finds(self.CLUB_BTN) if b.is_displayed()]
        if not btns:
            return None
        self.js_click(btns[0])
        time.sleep(0.4)
        inputs = self.driver.find_elements(
            By.XPATH, "//*[contains(normalize-space(),'Club')]/following::input[1]"
        )
        return inputs[0] if inputs else None

    def blur_active(self):
        self.driver.execute_script("document.activeElement && document.activeElement.blur();")
        time.sleep(0.3)
