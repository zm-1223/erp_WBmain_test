# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoAlertPresentException,
    StaleElementReferenceException,
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from utils.logger import get_logger

logger = get_logger("erp_wb.page")


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

    @staticmethod
    def quote(text: str) -> str:
        if "'" not in text:
            return f"'{text}'"
        if '"' not in text:
            return f'"{text}"'
        return "concat(" + ", \"'\", ".join(f"'{p}'" for p in text.split("'")) + ")"

    def find(self, locator, timeout=None):
        timeout = timeout or config.EXPLICIT_WAIT
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def finds(self, locator):
        return self.driver.find_elements(*locator)

    def visible(self, locator, timeout=None):
        timeout = timeout or config.EXPLICIT_WAIT
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def clickable(self, locator, timeout=None):
        timeout = timeout or config.EXPLICIT_WAIT
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def dismiss_popups(self):
        """兜底关弹窗：没有则静默返回；有则关闭并把原文写入日志。"""
        closed = []
        try:
            alert = self.driver.switch_to.alert
            text = (alert.text or "").strip()
            if text:
                closed.append(f"Alert:{text}")
            alert.dismiss()
        except (NoAlertPresentException, UnexpectedAlertPresentException, Exception):
            pass

        close_xpaths = [
            "//div[contains(@class,'el-message-box')]//button[contains(@class,'el-message-box__headerbtn')]",
            "//div[contains(@class,'el-dialog')]//button[contains(@class,'el-dialog__headerbtn')]",
            "//div[contains(@class,'el-message-box')]//button[normalize-space()='取消']",
            "//div[contains(@class,'el-dialog')]//button[normalize-space()='取消']",
            "//div[contains(@class,'el-message-box')]//button[normalize-space()='关闭']",
            "//div[contains(@class,'el-dialog')]//button[normalize-space()='关闭']",
            "//i[contains(@class,'el-message-box__close')]/ancestor::button[1]",
            "//button[contains(@class,'el-dialog__headerbtn')]",
            "//div[contains(@class,'el-message-box__btns')]//button[last()]",
        ]
        for xp in close_xpaths:
            try:
                btns = [
                    b
                    for b in self.driver.find_elements(By.XPATH, xp)
                    if b.is_displayed()
                ]
                if not btns:
                    continue
                box = None
                try:
                    box = btns[0].find_element(
                        By.XPATH,
                        "./ancestor::div[contains(@class,'el-message-box') or contains(@class,'el-dialog')][1]",
                    )
                except Exception:
                    pass
                text = ((box.text if box is not None else btns[0].text) or "").strip()
                self.driver.execute_script("arguments[0].click();", btns[0])
                if text:
                    closed.append(text.replace("\n", " | ")[:500])
                time.sleep(0.15)
                break
            except Exception:
                continue

        for msg in closed:
            logger.warning("关闭弹窗: %s", msg)
        return closed

    def confirm_popups(self, timeout=4):
        """业务确认框点「确定/确认」，不点取消。无框则静默返回 False。"""
        end = time.time() + timeout
        xp = (
            "//div[contains(@class,'el-message-box') or contains(@class,'el-dialog')]"
            "//button[normalize-space()='确定' or normalize-space()='确认' or normalize-space()='是']"
        )
        while time.time() < end:
            try:
                btns = [b for b in self.driver.find_elements(By.XPATH, xp) if b.is_displayed()]
                if btns:
                    box = None
                    try:
                        box = btns[0].find_element(
                            By.XPATH,
                            "./ancestor::div[contains(@class,'el-message-box') or contains(@class,'el-dialog')][1]",
                        )
                    except Exception:
                        pass
                    text = ((box.text if box is not None else btns[0].text) or "").strip()
                    self.driver.execute_script("arguments[0].click();", btns[0])
                    if text:
                        logger.info("确认弹窗: %s", text.replace("\n", " | ")[:500])
                    time.sleep(0.25)
                    return True
            except Exception:
                pass
            time.sleep(0.2)
        return False

    def cancel_popups(self, timeout=3):
        """业务确认框点「取消」，无框返回 False。"""
        end = time.time() + timeout
        xp = (
            "//div[contains(@class,'el-message-box') or contains(@class,'el-dialog')]"
            "//button[normalize-space()='取消' or normalize-space()='否']"
        )
        while time.time() < end:
            try:
                btns = [b for b in self.driver.find_elements(By.XPATH, xp) if b.is_displayed()]
                if btns:
                    self.driver.execute_script("arguments[0].click();", btns[0])
                    logger.info("取消弹窗")
                    time.sleep(0.2)
                    return True
            except Exception:
                pass
            time.sleep(0.15)
        return False

    def raw_click(self, el):
        """点击且不先 dismiss，避免关掉刚打开的下拉菜单。"""
        logger.info("点击元素")
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(0.1)
            el.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.driver.execute_script("arguments[0].click();", el)

    def click_menu_item(self, keywords: tuple[str, ...], timeout=5):
        xps = []
        for kw in keywords:
            xps.append(f"//li[@role='menuitem' and contains(., {self.quote(kw)})]")
            xps.append(
                f"//*[contains(@class,'el-dropdown-menu__item') and contains(., {self.quote(kw)})]"
            )
            xps.append(
                "//div[contains(@class,'el-dropdown-menu') or contains(@class,'el-popper')]"
                f"//*[contains(normalize-space(), {self.quote(kw)})]"
            )
        end = time.time() + timeout
        while time.time() < end:
            for xp in xps:
                items = [i for i in self.driver.find_elements(By.XPATH, xp) if i.is_displayed()]
                if items:
                    self.driver.execute_script("arguments[0].click();", items[0])
                    time.sleep(0.25)
                    return True
            time.sleep(0.15)
        return False

    def js_click(self, el):
        self.dismiss_popups()
        logger.info("点击元素")
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(0.12)
            el.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.driver.execute_script("arguments[0].click();", el)

    def click_xpath(self, xpath, timeout=None):
        el = self.clickable((By.XPATH, xpath), timeout)
        self.js_click(el)
        return el

    def button(self, text: str, timeout=None):
        return self.click_xpath(
            f"//button[normalize-space()={self.quote(text)}]", timeout
        )

    def button_contains(self, text: str, timeout=None):
        return self.click_xpath(
            f"//button[contains(normalize-space(), {self.quote(text)})]", timeout
        )

    def page_text(self) -> str:
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text or ""
        except Exception:
            return ""

    def has_text(self, text: str) -> bool:
        return text in self.page_text()

    def wait_text(self, text: str, timeout=None) -> bool:
        timeout = timeout or config.EXPLICIT_WAIT
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: text in self.page_text())
            return True
        except TimeoutException:
            return False

    def toast(self, timeout=5) -> str:
        end = time.time() + timeout
        last = ""
        while time.time() < end:
            nodes = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".el-message, .el-notification, .el-message-box, "
                ".el-message__content, .el-notification__content, "
                ".el-message-box__message",
            )
            texts = [n.text.strip() for n in nodes if n.text and n.text.strip()]
            if texts:
                last = "\n".join(texts)
                return last
            time.sleep(0.2)
        return last

    def popup_text(self, timeout=3) -> str:
        """读取当前确认框/提示框原文，不点击。"""
        end = time.time() + timeout
        css = (
            ".el-message-box__message, .el-message-box, .el-dialog__body, "
            ".el-form-item__error, .el-message__content"
        )
        while time.time() < end:
            parts = []
            for el in self.driver.find_elements(By.CSS_SELECTOR, css):
                try:
                    if el.is_displayed() and (el.text or "").strip():
                        parts.append(el.text.strip())
                except Exception:
                    continue
            if parts:
                return "\n".join(parts)
            time.sleep(0.15)
        return ""

    def goto_hash(self, hash_path: str, keyword: str | None = None):
        """同域只改 hash，不重新打开站点。"""
        self.dismiss_popups()
        logger.info("跳转 hash=%s", hash_path)
        if not hash_path.startswith("#"):
            hash_path = "#" + hash_path
        current = self.driver.current_url or ""
        if config.BASE_URL not in current:
            self.driver.get(config.BASE_URL + "/" + hash_path)
        else:
            self.driver.execute_script(
                "window.location.hash = arguments[0]", hash_path.lstrip("#")
            )
            time.sleep(0.35)
        WebDriverWait(self.driver, config.EXPLICIT_WAIT).until(
            lambda d: hash_path.split("?")[0] in (d.current_url or "")
            or hash_path in (d.current_url or "")
        )
        if keyword:
            self.wait_text(keyword, config.EXPLICIT_WAIT)
        time.sleep(0.4)

    def fill(self, locator, value: str):
        self.dismiss_popups()
        logger.info("填写 %s", locator)
        el = self.visible(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        try:
            el.click()
            el.send_keys(Keys.CONTROL, "a")
            el.send_keys(Keys.DELETE)
            el.clear()
        except Exception:
            self.driver.execute_script(
                "arguments[0].value='';"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
                el,
            )
        if value:
            el.send_keys(value)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
            el,
        )
        return el

    def set_value(self, locator, value: str):
        self.dismiss_popups()
        logger.info("设置值 %s", locator)
        el = self.visible(locator)
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
        return el

    def click_first_button(self, labels: tuple[str, ...], timeout=12):
        """点第一个可见按钮。优先长文案，避免「采集到草稿箱」点到别的按钮。"""
        end = time.time() + timeout
        while time.time() < end:
            for label in labels:
                xp = f"//button[contains(normalize-space(), {self.quote(label)})]"
                els = [b for b in self.driver.find_elements(By.XPATH, xp) if b.is_displayed()]
                if els:
                    self.js_click(els[0])
                    return label
            time.sleep(0.3)
        raise AssertionError(f"未找到按钮 {labels}")

    def selected_goods_count(self) -> int:
        """列表里已勾选的商品。弹窗里的平台、店铺勾选不算。"""
        try:
            n = self.driver.execute_script(
                """
                const nodes = document.querySelectorAll(
                    '.el-checkbox.is-checked, .el-checkbox__input.is-checked'
                );
                const seen = new Set();
                let count = 0;
                nodes.forEach((node) => {
                    const box = node.closest('.el-checkbox') || node;
                    if (seen.has(box)) return;
                    seen.add(box);
                    if (box.closest('.el-dialog, .el-message-box')) return;
                    const style = window.getComputedStyle(box);
                    if (style.display === 'none' || style.visibility === 'hidden') return;
                    const text = box.innerText || '';
                    if (text.indexOf('全选') >= 0) return;
                    count += 1;
                });
                return count;
                """
            )
        except Exception:
            return 0
        return int(n or 0)

    def unselected_batch_tip(self, dialog=None) -> str:
        """未勾选商品时只取页面提示。店铺弹窗说明里的「勾选」不算这条提示。"""
        tip = self.toast(2) or ""
        if dialog is not None:
            self.close_target_shop_dialog(dialog)
        if "选择目标平台" in tip or "将写入" in tip:
            messages = []
            for node in self.driver.find_elements(
                By.CSS_SELECTOR, ".el-message__content, .el-notification__content"
            ):
                text = (node.text or "").strip()
                if text and "选择目标平台" not in text:
                    messages.append(text)
            tip = "\n".join(messages)
        logger.info("未勾选商品，不写入草稿: %s", (tip or "")[:200])
        return tip

    def close_target_shop_dialog(self, dialog=None):
        dialog = dialog or self.target_shop_dialog()
        if dialog is None:
            return self
        for css in (".el-dialog__headerbtn", ".el-dialog__close"):
            icons = [i for i in dialog.find_elements(By.CSS_SELECTOR, css) if i.is_displayed()]
            if icons:
                self.driver.execute_script("arguments[0].click();", icons[0])
                time.sleep(0.3)
                return self
        return self

    def target_shop_dialog(self):
        for el in self.driver.find_elements(By.CSS_SELECTOR, ".el-dialog"):
            try:
                if el.is_displayed() and "选择目标平台和店铺" in (el.text or ""):
                    return el
            except Exception:
                continue
        return None

    def _check_box(self, el):
        cls = el.get_attribute("class") or ""
        try:
            inner = el.find_element(By.CSS_SELECTOR, ".el-checkbox__input")
            cls += " " + (inner.get_attribute("class") or "")
        except Exception:
            pass
        if "is-checked" in cls:
            return
        self.driver.execute_script("arguments[0].click();", el)
        time.sleep(0.15)

    def _platform_checkbox(self, dialog, platform: str):
        """平台名写在复选框旁边。只认带「家店」且只有这一家平台的那一行。"""
        return self.driver.execute_script(
            """
            const dialog = arguments[0], platform = arguments[1];
            const nodes = dialog.querySelectorAll('div,span,p,label');
            for (const el of nodes) {
              const own = (el.innerText || '').trim();
              if (own !== platform) continue;
              let node = el;
              for (let i = 0; i < 6; i++) {
                if (!node) break;
                const t = (node.innerText || '').trim();
                if (t.includes('选择目标平台') || t.length > 90) break;
                const lines = t.split(/\\n/).map(s => s.trim()).filter(Boolean);
                const plats = lines.filter(ln => ln === 'Wildberries' || ln === 'Ozon');
                const boxes = [...node.querySelectorAll('.el-checkbox')].filter(
                  b => !/全选|清空/.test(b.innerText || '')
                );
                if (boxes.length === 1 && t.includes('家') && plats.length === 1 && plats[0] === platform) {
                  return boxes[0];
                }
                node = node.parentElement;
              }
            }
            return null;
            """,
            dialog,
            platform,
        )

    def _shop_checkbox(self, dialog, keyword: str):
        """按店铺名找右侧具体店铺，不点平台行和全选。"""
        return self.driver.execute_script(
            """
            const dialog = arguments[0], keyword = (arguments[1] || '').toLowerCase();
            const nodes = dialog.querySelectorAll('div,span,p,label');
            for (const el of nodes) {
              const own = (el.innerText || '').trim();
              if (!own || own.length > 40 || !own.toLowerCase().includes(keyword)) continue;
              if (own === 'WB' || own === 'OZ' || own.includes('家') || own.includes('全选')) continue;
              let node = el;
              for (let i = 0; i < 6; i++) {
                if (!node) break;
                const t = (node.innerText || '').trim();
                if (t.includes('选择目标平台') || t.length > 90) break;
                const lines = t.split(/\\n/).map(s => s.trim()).filter(Boolean);
                const boxes = [...node.querySelectorAll('.el-checkbox')].filter(
                  b => !/全选|清空/.test(b.innerText || '')
                );
                if (boxes.length === 1 && (lines.includes('WB') || lines.includes('OZ')) && !t.includes('家')) {
                  return boxes[0];
                }
                node = node.parentElement;
              }
            }
            return null;
            """,
            dialog,
            keyword,
        )

    def _dialog_checkboxes(self, dialog):
        boxes = []
        for box in dialog.find_elements(By.CSS_SELECTOR, ".el-checkbox"):
            try:
                if box.is_displayed():
                    boxes.append(box)
            except Exception:
                continue
        return boxes

    def _row_text(self, box) -> str:
        try:
            text = self.driver.execute_script(
                """
                const el = arguments[0];
                let node = el;
                for (let i = 0; i < 5; i++) {
                  const t = (node.innerText || '').trim();
                  if (t.includes('选择目标平台') || t.length > 160) break;
                  const lines = t.split(/\\n/).map(s => s.trim()).filter(Boolean);
                  if (lines.includes('WB') || lines.includes('OZ') || t.includes('家')) return t;
                  if (!node.parentElement) break;
                  node = node.parentElement;
                }
                const extra = el.nextElementSibling ? (el.nextElementSibling.innerText || '').trim() : '';
                const own = (el.innerText || '').trim();
                if (extra === 'WB' || extra === 'OZ') return own + '\\n' + extra;
                return own;
                """,
                box,
            )
            return (text or "").strip()
        except Exception:
            return (box.text or "").strip()

    def _is_specific_shop(self, box, mark: str) -> bool:
        """右侧具体店铺。只勾平台、全选、家店计数都不算店铺。"""
        own = (box.text or "").strip()
        first = own.splitlines()[0].strip() if own else ""
        if "全选" in own or "清空" in own or "搜索" in own:
            return False
        if first.lower() in ("wildberries", "ozon", "wb", "oz"):
            return False
        blob = self._row_text(box)
        if "家" in blob or "全选" in blob:
            return False
        lines = [ln.strip() for ln in blob.splitlines() if ln.strip()]
        if mark not in lines:
            return False
        names = [ln for ln in lines if ln not in ("WB", "OZ", "Wildberries", "Ozon")]
        return any(len(name) > 1 for name in names)

    def complete_target_shops(self, platform: str = "Wildberries", shop_count: int = 2, confirm: bool = True) -> str:
        """先勾平台，再勾右侧具体店铺。只勾平台时「将写入 0 个店铺」，不算选完。"""
        self.batch_dialog_seen = True
        self.batch_shop_count = 0
        self.batch_shop_names = []
        end = time.time() + 8
        dialog = self.target_shop_dialog()
        while dialog is None and time.time() < end:
            time.sleep(0.3)
            dialog = self.target_shop_dialog()
        if dialog is None:
            raise AssertionError("未出现「选择目标平台和店铺」")
        # 仍先核对本次要测的平台在，再点名勾同江和 Minjin。找不到就失败，不改去勾别的店，也不改断言。
        needed_platforms = ["Wildberries", "Ozon"]
        if platform not in needed_platforms and platform.lower() != "ozon":
            needed_platforms.insert(0, platform)
        for name in needed_platforms:
            box = self._platform_checkbox(dialog, name)
            if box is None and name == platform:
                raise AssertionError(f"弹窗左侧没有平台「{platform}」: {(dialog.text or '')[:400]}")
            if box is not None:
                self._check_box(box)
        time.sleep(0.35)
        dialog = self.target_shop_dialog() or dialog
        wanted = [config.BATCH_WB_SHOP, config.BATCH_OZON_SHOP]
        shops = []
        names = []
        missing = []
        for keyword in wanted:
            box = self._shop_checkbox(dialog, keyword)
            if box is None:
                missing.append(keyword)
                continue
            self._check_box(box)
            shops.append(box)
            names.append(self._row_text(box).splitlines()[0].strip() or keyword)
        if missing or len(shops) < shop_count:
            raise AssertionError(
                f"要勾的店铺是{wanted}，没有找到{missing or wanted}。"
                f"不改勾其他店铺。弹窗: {(dialog.text or '')[:400]}"
            )
        self.batch_shop_names = names
        time.sleep(0.3)
        dialog = self.target_shop_dialog() or dialog
        blob = dialog.text or ""
        found = re.search(r"将写入\s*(\d+)\s*个店铺", blob)
        written = int(found.group(1)) if found else 0
        if written < shop_count:
            raise AssertionError(
                f"已勾具体店铺{names}，将写入只有 {written} 个。只勾平台不算选完: {blob[:300]}"
            )
        self.batch_shop_count = written
        self.batch_dialog_text = blob
        if confirm:
            btns = [
                b
                for b in dialog.find_elements(
                    By.XPATH, ".//button[normalize-space()='完成' or normalize-space()='确定']"
                )
                if b.is_displayed()
            ]
            if not btns:
                raise AssertionError(f"店铺弹窗没有「完成」: {blob[:300]}")
            if "is-disabled" in (btns[0].get_attribute("class") or ""):
                raise AssertionError(f"已选具体店铺但「完成」不可用: {blob[:300]}")
            self.driver.execute_script("arguments[0].click();", btns[0])
            logger.info("确认多店铺草稿: 店铺=%s 将写入 %s 个", names, self.batch_shop_count)
        else:
            closed = False
            for css in (".el-dialog__headerbtn", ".el-dialog__close"):
                icons = [i for i in dialog.find_elements(By.CSS_SELECTOR, css) if i.is_displayed()]
                if icons:
                    self.driver.execute_script("arguments[0].click();", icons[0])
                    closed = True
                    break
            if not closed:
                self.cancel_popups(timeout=1)
            logger.info("关闭多店铺草稿弹窗，未确定")
        time.sleep(0.6)
        return blob

    def open_batch_draft_dialog(self, labels: tuple[str, ...] | None = None):
        labels = labels or ("批量采集到草稿箱", "采集到草稿箱", "批量生成草稿")
        self.batch_dialog_seen = False
        self.batch_shop_count = 0
        self.batch_dialog_text = ""
        self.click_first_button(labels)
        time.sleep(0.5)
        return self.target_shop_dialog()

    def close_extra_tabs(self):
        handles = self.driver.window_handles
        if len(handles) <= 1:
            return
        main = handles[0]
        for h in handles[1:]:
            self.driver.switch_to.window(h)
            self.driver.close()
        self.driver.switch_to.window(main)

    def url(self) -> str:
        return self.driver.current_url or ""
