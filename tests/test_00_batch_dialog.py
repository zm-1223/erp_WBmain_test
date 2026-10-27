# -*- coding: utf-8 -*-
"""弹窗行判定，不打开浏览器。文字取自「选择目标平台和店铺」失败截图。"""
import pytest
from selenium.common.exceptions import StaleElementReferenceException

from utils.batch_dialog import is_platform_row, is_shop_row, join_flash, readable_texts, row_blobs

pytestmark = pytest.mark.no_browser


def test_left_platform_row_is_wildberries():
    blobs = row_blobs(
        {
            "own": "Wildberries",
            "next": "WB · 0/2 家店",
            "prev": "",
            "ancestors": ["全选\nWildberries\nWB · 0/2 家店\nOzon\nOZ · 0/2 家店"],
        }
    )
    assert is_platform_row(blobs, "Wildberries")
    assert not is_platform_row(blobs, "Ozon")


def test_right_group_title_is_not_a_platform_row():
    blobs = row_blobs(
        {
            "own": "Wildberries",
            "next": "全选",
            "prev": "",
            "ancestors": ["Wildberries\n全选\n天津智云电子商务有限公司\nWB\n同江市同智跨境电子商务有限公司\nWB"],
        }
    )
    assert not is_platform_row(blobs, "Wildberries")


def test_named_shop_row():
    blobs = row_blobs(
        {
            "own": "同江市同智跨境电子商务有限公司",
            "next": "WB",
            "prev": "天津智云电子商务有限公司\nWB",
            "ancestors": [
                "Wildberries\n全选\n天津智云电子商务有限公司\nWB\n同江市同智跨境电子商务有限公司\nWB"
            ],
        }
    )
    assert is_shop_row(blobs, "同江")
    assert not is_shop_row(blobs, "Minjin")
    assert not is_platform_row(blobs, "Wildberries")


def test_minjin_shop_row():
    blobs = row_blobs({"own": "Minjin", "next": "OZ", "prev": "", "ancestors": []})
    assert is_shop_row(blobs, "Minjin")
    assert not is_shop_row(blobs, "同江")


def test_unselected_toast_is_kept():
    assert join_flash(["请先选择目标平台和店铺"]) == "请先选择目标平台和店铺"


def test_readable_texts_skips_stale_node():
    class Gone:
        @property
        def text(self):
            raise StaleElementReferenceException("stale")

    class Kept:
        text = "已保存"

    assert readable_texts([Gone(), Kept()]) == ["已保存"]
