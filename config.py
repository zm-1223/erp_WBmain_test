# -*- coding: utf-8 -*-
"""测试环境配置。账号密码可通过环境变量覆盖。"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS_DIR = ROOT / "reports"
ALLURE_RESULTS = REPORTS_DIR / "allure-results"
SCREENSHOT_DIR = REPORTS_DIR / "screenshots"
LOG_DIR = REPORTS_DIR / "logs"

BASE_URL = os.getenv("ERP_BASE_URL", "https://russtar.wildberries.center")
USERNAME = os.getenv("ERP_USERNAME", "luojiaxing1")
PASSWORD = os.getenv("ERP_PASSWORD", "ZYJK123456")

WB_SHOP_NAME = os.getenv("ERP_WB_SHOP", "天津智云电子商务有限公司")
WB_SHOP_OPTION = os.getenv("ERP_WB_SHOP_OPTION", "[WB] 天津智云电子商务有限公司")
WB_SHOP_PALLET_1688 = os.getenv(
    "ERP_WB_SHOP_PALLET_1688",
    "[WILDBERRIES] 天津智云电子商务有限公司",
)

OFFER_ID = "726638874254"
# 该 offer 货源实测包装（刊登页带出应与此一致）
SAMPLE_WEIGHT_KG = 0.8
SAMPLE_DIMS_CM = (42.0, 32.0, 5.0)
LINK_1688_SHORT = f"https://detail.1688.com/offer/{OFFER_ID}.html"
LINK_1688_FULL = (
    "https://detail.1688.com/offer/726638874254.html?src=zhanwai&pid=301011_0000"
    "&ptid=01770000000c8ba254ee13092cfbc8c0&exp=enquiry%3AB%3BqueryMobilePhone%3AA%3Bxlyx%3AB"
)
INVALID_LINK = "https://item.taobao.com/item.htm?id=123456"
JD_SKU_ID = os.getenv("ERP_JD_SKU", "100406854234")

HASH_COLLECT = "#/goods/collection?tab=collect"
HASH_1688_PALLET = "#/goods/collection?tab=pallet"
HASH_JD_PALLET = "#/goods/collection?tab=jd-pallet"
HASH_TB_PALLET = "#/goods/collection?tab=taobao-pallet"
HASH_DRAFT = "#/goods/publish?tab=draft"

# 默认不向 WB 真实提交刊登
SUBMIT_LIVE = os.getenv("ERP_SUBMIT_LIVE", "0") == "1"

IMPLICIT_WAIT = 0
EXPLICIT_WAIT = 20
PULL_WAIT = 30
HEADLESS = os.getenv("ERP_HEADLESS", "0") == "1"
KEEP_BROWSER = os.getenv("ERP_KEEP_BROWSER", "0") == "1"
WINDOW_SIZE = os.getenv("ERP_WINDOW_SIZE", "1600,900")
