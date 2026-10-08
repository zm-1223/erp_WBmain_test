# -*- coding: utf-8 -*-
"""OZ01-OZ05 各入口一键刊登 Ozon。"""
import allure
import pytest

import config

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)


def _assert_ozon_open(page, entry: str):
    assert page.is_open(), f"{entry} 未进入 Ozon 刊登页 url={page.url()!r}"
    text = page.page_text()
    assert page.steps_present() or "Ozon" in text or "OZON" in text
    assert page.has_recommended_category(), (
        f"{entry} 进入 Ozon 刊登页未带推荐类目: {page.category_value()!r}"
    )


@allure.epic("如斯达ERP")
@allure.feature("Ozon商品刊登-入口")
class TestOzonEntries:
    @allure.story("入口/1688链接")
    @allure.title("OZ01 一键刊登 Ozon 进入编辑页并预填")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz01_1688_link_enter(self, collect_page, ozon_listing_page):
        collect_page.ensure_card()
        collect_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        _assert_ozon_open(ozon_listing_page, "1688链接")
        assert config.OFFER_ID in ozon_listing_page.page_text() or config.OFFER_ID in (
            ozon_listing_page.source_url_value() or ""
        )

    @allure.story("入口/1688精选")
    @allure.title("OZ02 1688精选一键刊登 Ozon")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.need_goods
    def test_oz02_1688_pallet_enter(self, pallet_page, ozon_listing_page):
        pallet_page.open("1688").wait_loaded("1688")
        if not pallet_page.has_goods():
            pytest.skip("1688精选无商品")
        pallet_page.choose_ozon_shop()
        pallet_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        _assert_ozon_open(ozon_listing_page, "1688精选")

    @allure.story("入口/京东精选")
    @allure.title("OZ03 京东精选一键刊登 Ozon")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.need_goods
    def test_oz03_jd_pallet_enter(self, pallet_page, ozon_listing_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        pallet_page.choose_ozon_shop()
        pallet_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        _assert_ozon_open(ozon_listing_page, "京东精选")

    @allure.story("入口/淘宝精选")
    @allure.title("OZ04 淘宝精选一键刊登 Ozon")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.need_goods
    def test_oz04_tb_pallet_enter(self, pallet_page, ozon_listing_page):
        pallet_page.open("tb").wait_loaded("tb")
        if not pallet_page.has_goods():
            pytest.skip("淘宝精选无商品")
        pallet_page.choose_ozon_shop()
        pallet_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        _assert_ozon_open(ozon_listing_page, "淘宝精选")

    @allure.story("入口/目标店铺")
    @allure.title("OZ05 目标店铺含 OZON，刊登 Ozon 须选 OZON 店")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz05_shop_options(self, pallet_page):
        pallet_page.open("jd").wait_loaded("jd")
        opts = " ".join(pallet_page.shop_options())
        assert "OZON" in opts.upper() or "Ozon" in opts
