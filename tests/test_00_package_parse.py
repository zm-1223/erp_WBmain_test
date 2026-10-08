# -*- coding: utf-8 -*-
"""包装解析单测，不打开浏览器。"""
import pytest

pytestmark = pytest.mark.no_browser
from utils.package_fields import parse_package, package_visible, same_num
from utils.source_card import parse_source_card


def test_parse_weight_and_dims_x():
    pkg = parse_package("包装重量 kg：0.8 包装尺寸 cm：42x32x5")
    assert pkg["weight"] == 0.8
    assert pkg["dims"] == [42.0, 32.0, 5.0]
    assert package_visible(pkg)


def test_parse_chinese_lwh():
    pkg = parse_package("长42cm 宽32cm 高5")
    assert pkg["dims"] == [42.0, 32.0, 5.0]


def test_parse_empty_not_visible():
    pkg = parse_package("标题 货源价 ¥12 offerId：123")
    assert not package_visible(pkg)


def test_zero_not_carried():
    pkg = parse_package("重量：0 尺寸：0x0x0")
    assert pkg["weight"] is None
    assert not package_visible(pkg)


def test_same_num_tol():
    assert same_num(0.8, 0.82)
    assert not same_num(0.8, 1.0)
    assert same_num(None, None)


def test_parse_source_card_price_sku():
    card = parse_source_card("日式真空袋\nofferId：4172\n货源价 ¥192\nSKU数量 3\n图片张数 5")
    assert card["price"] == 192
    assert card["sku_n"] == 3
    assert card["img_n"] == 5
    assert "真空" in card["title"]
    assert "图片" not in card["title"]


def test_parse_source_card_skips_drawer_chrome():
    card = parse_source_card(
        "1688 寻源通商品详情\nOffer ID: 726638874254\n采购价\n26秋苎麻扎染宽松衬衫\n货源价 ¥19.9"
    )
    assert "苎麻" in card["title"]
    assert "寻源" not in card["title"]


def test_parse_source_card_skips_origin_link():
    card = parse_source_card("1688 原链接\n一键刊登\n26秋苎麻扎染宽松衬衫\n货源价 ¥19.9")
    assert "苎麻" in card["title"]
    assert "原链接" not in card["title"]
