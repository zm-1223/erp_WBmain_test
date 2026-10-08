# -*- coding: utf-8 -*-
from __future__ import annotations

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
