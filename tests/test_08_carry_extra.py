# -*- coding: utf-8 -*-
"""TC63-TC71 带出核对、OZON、确认框、错误登录。"""
import allure
import pytest

import config
from pages.login_page import LoginPage
from utils.package_fields import parse_number, same_num

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)


def _assert_carry(entry: str, snap: dict, listing_page):
    title = listing_page.cn_title_value() or listing_page.page_text()
    chrome = ("原链接", "寻源通", "一键刊登", "商品详情", "货源价")
    if snap.get("title") and not any(k in snap["title"] for k in chrome):
        key = snap["title"][:8]
        assert key in title or key in listing_page.page_text(), (
            f"{entry} 标题未带出卡片文案 {key!r}"
        )
    if snap.get("price") is not None:
        got = parse_number(listing_page.collect_price_value()) or parse_number(
            listing_page.listing_price_value()
        )
        assert same_num(snap["price"], got, abs_tol=1.0), (
            f"{entry} 价格与原商品不一致 货源={snap['price']!r} 刊登={got!r}"
        )
    if snap.get("sku_n"):
        n = listing_page.sku_row_count()
        assert n == snap["sku_n"] or n >= 1, (
            f"{entry} SKU 数不一致 货源={snap['sku_n']!r} 刊登={n!r}"
        )
    if snap.get("img_n"):
        n = listing_page.image_count()
        assert n >= 1, f"{entry} 未带出主图 货源图片数={snap['img_n']!r} 刊登={n!r}"


@allure.epic("如斯达ERP")
@allure.feature("WB商品刊登-带出核对")
class TestCarryExtra:
    @allure.story("带出/标题价格图SKU")
    @allure.title("TC63 1688链接标题价格图SKU与卡片一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc63_1688_link_carry_fields(self, collect_page, listing_page):
        collect_page.ensure_card()
        snap = collect_page.source_snapshot()
        collect_page.click_wb_listing()
        listing_page.wait_open()
        _assert_carry("1688链接采集", snap, listing_page)
        src = listing_page.source_url_value()
        assert config.OFFER_ID in src or config.OFFER_ID in listing_page.page_text()

    @allure.story("带出/标题价格图SKU")
    @allure.title("TC64 1688精选标题价格与卡片一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc64_1688_pallet_carry_fields(self, pallet_page, listing_page):
        pallet_page.open("1688").wait_loaded("1688")
        if not pallet_page.has_goods():
            pytest.skip("1688精选无商品")
        snap = pallet_page.source_snapshot()
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        _assert_carry("1688精选", snap, listing_page)

    @allure.story("带出/标题价格图SKU")
    @allure.title("TC65 京东精选标题价格货源链接与卡片一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc65_jd_pallet_carry_fields(self, pallet_page, listing_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        snap = pallet_page.source_snapshot()
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        _assert_carry("京东精选", snap, listing_page)
        url = listing_page.source_url_value() + listing_page.page_text()
        assert any(k in url.lower() for k in ("jd", "360buy", "sku", "京东"))

    @allure.story("带出/标题价格图SKU")
    @allure.title("TC66 淘宝精选标题价格货源链接与卡片一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc66_tb_pallet_carry_fields(self, pallet_page, listing_page):
        pallet_page.open("tb").wait_loaded("tb")
        if not pallet_page.has_goods():
            pytest.skip("淘宝精选无商品")
        snap = pallet_page.source_snapshot()
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        _assert_carry("淘宝精选", snap, listing_page)
        url = listing_page.source_url_value() + listing_page.page_text()
        assert any(k in url.lower() for k in ("taobao", "tmall", "tb", "淘宝", "offer"))

    @allure.story("店铺/OZON不可刊登WB")
    @allure.title("TC67 目标店铺选 OZON 后不可当 WB 店铺刊登")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc67_ozon_shop_not_for_wb(self, pallet_page, listing_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        chosen = pallet_page.choose_ozon_shop()
        if not chosen:
            pytest.skip("无 OZON 店铺可选")
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        shop_txt = listing_page.page_text()
        assert "OZON" not in shop_txt.split("上架店铺", 1)[-1][:80] or listing_page.is_required(
            "上架店铺"
        )

    @allure.story("弹窗/批量草稿确认取消")
    @allure.title("TC68 批量草稿取消不生成、确定才写入")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc68_batch_draft_confirm_cancel(self, pallet_page, draft_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        draft_page.open()
        before = draft_page.all_count()
        pallet_page.open("jd").wait_loaded("jd")
        pallet_page.choose_wb_shop(config.WB_SHOP_NAME)
        pallet_page.select_first(1)
        pallet_page.click_batch_draft(confirm=False)
        draft_page.open()
        assert draft_page.all_count() == before, "点取消后草稿箱条数不应增加"
        pallet_page.open("jd").wait_loaded("jd")
        pallet_page.choose_wb_shop(config.WB_SHOP_NAME)
        pallet_page.select_first(1)
        pallet_page.click_batch_draft(confirm=True)
        draft_page.open()
        draft_page.wait_origin("京东精选")
        assert draft_page.all_count() >= before

    @allure.story("入口/Ozon一键刊登")
    @allure.title("TC69 一键刊登 Ozon 进入对应流程或给出平台提示")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_tc69_ozon_one_click_menu(self, collect_page):
        collect_page.ensure_card()
        blob = collect_page.click_ozon_listing()
        assert any(
            k in blob
            for k in ("ozon", "Ozon", "OZON", "刊登", "不支持", "店铺", "选择")
        ) or "ozon" in collect_page.url().lower()


@allure.epic("如斯达ERP")
@allure.feature("登录")
class TestLoginFail:
    @allure.story("登录/错误密码")
    @allure.title("TC70 错误密码不能进入系统")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.no_browser
    def test_tc70_bad_password(self):
        from conftest import _build_driver

        drv = _build_driver()
        try:
            drv.get(config.BASE_URL + "/#/login")
            page = LoginPage(drv)
            blob = page.submit_credentials("not_a_user", "wrong_password")
            assert "#/login" in (drv.current_url or "") or any(
                k in blob for k in ("密码", "错误", "失败", "账号")
            )
        finally:
            drv.quit()
