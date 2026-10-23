# -*- coding: utf-8 -*-
import time

from selenium.webdriver.common.by import By

import config
from pages.base_page import BasePage


class LoginPage(BasePage):
    USER = (By.CSS_SELECTOR, "input[placeholder='请输入登录账号']")
    PWD = (By.CSS_SELECTOR, "input[placeholder='请输入密码']")
    SUBMIT = (By.XPATH, "//button[normalize-space()='登录系统']")

    def need_login(self) -> bool:
        return "#/login" in self.url() or self.has_text("请输入登录账号")

    def submit_credentials(self, username: str, password: str):
        self.fill(self.USER, username)
        self.fill(self.PWD, password)
        self.js_click(self.clickable(self.SUBMIT))
        time.sleep(1.2)
        return self.toast() or self.page_text() or self.url()

    def login(self, username=None, password=None):
        # 首屏可能先是空白再跳到登录。等到登录框或已进后台再决定，避免没填账号就往下走。
        deadline = time.time() + config.EXPLICIT_WAIT
        while time.time() < deadline:
            if self.need_login():
                break
            if self.has_text("商品采集") or self.has_text("1688商品链接采集"):
                return
            time.sleep(0.3)
        if not self.need_login():
            return
        self.submit_credentials(username or config.USERNAME, password or config.PASSWORD)
        self.wait.until(lambda d: "#/login" not in (d.current_url or ""))
        self.wait_text("商品采集")
