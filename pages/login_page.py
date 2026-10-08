# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By

import config
from pages.base_page import BasePage


class LoginPage(BasePage):
    USER = (By.CSS_SELECTOR, "input[placeholder='请输入登录账号']")
    PWD = (By.CSS_SELECTOR, "input[placeholder='请输入密码']")
    SUBMIT = (By.XPATH, "//button[normalize-space()='登录系统']")

    def need_login(self) -> bool:
        return "#/login" in self.url() or self.has_text("请输入登录账号")

    def login(self, username=None, password=None):
        if not self.need_login():
            return
        self.fill(self.USER, username or config.USERNAME)
        self.fill(self.PWD, password or config.PASSWORD)
        self.js_click(self.clickable(self.SUBMIT))
        self.wait.until(lambda d: "#/login" not in (d.current_url or ""))
        self.wait_text("商品采集")
