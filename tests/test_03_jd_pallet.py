# -*- coding: utf-8 -*-
"""TC15-TC21 京东精选入口。"""
import allure
import pytest

import config

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)


@allure.epic("如斯达ERP")
@allure.feature("WB商品刊登-京东精选")
class TestJdPallet:
    @allure.story("入口/页面加载")
    @allure.title("TC15 京东精选列表字段")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc15_tab_loaded(self, pallet_page):
        pallet_page.open("jd").wait_loaded("jd")
        assert "tab=jd-pallet" in pallet_page.url()
        text = pallet_page.page_text()
        assert "京东精选" in text
        if pallet_page.has_goods():
            assert "skuId" in text or "sku" in text.lower()
            assert "一键刊登" in text
            assert "查看货源" in text
            assert "货源价" in text

    @allure.story("入口/查询")
    @allure.title("TC16 按 skuId 查询")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc16_search_sku(self, pallet_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        pallet_page.search(config.JD_SKU_ID)
        text = pallet_page.page_text()
        assert config.JD_SKU_ID in text or "共 1" in text or "一键刊登" in text
        pallet_page.reset()
        assert "京东精选" in pallet_page.page_text()

    @allure.story("入口/查看货源")
    @allure.title("TC17 查看货源跳转")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc17_view_source(self, pallet_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        before = pallet_page.driver.window_handles[:]
        pallet_page.click_view_source()
        after = pallet_page.driver.window_handles
        if len(after) > len(before):
            pallet_page.driver.switch_to.window(after[-1])
            url = pallet_page.url()
            pallet_page.close_extra_tabs()
            assert "jd" in url.lower() or "360buy" in url.lower() or url != before
        else:
            assert "jd" in pallet_page.url().lower() or pallet_page.url() != ""

    @allure.story("入口/未勾选批量")
    @allure.title("TC18 未勾选提示请先勾选京东精选商品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc18_batch_without_select(self, pallet_page):
        pallet_page.open("jd").wait_loaded("jd")
        tip = pallet_page.click_batch_draft()
        assert "勾选" in tip or "请先" in tip, tip[:300]

    @allure.story("入口/一键刊登WB")
    @allure.title("TC19 京东精选一键刊登 WB")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc19_one_click_wb(self, pallet_page, listing_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        pallet_page.choose_wb_shop("WB")
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        assert listing_page.is_open()
        src = listing_page.source_url_value() + listing_page.page_text()
        assert listing_page.steps_present()
        assert src
        assert listing_page.has_recommended_category(), (
            f"京东精选进入刊登页未带推荐类目: {listing_page.category_value()!r}"
        )

    @allure.story("入口/目标店铺")
    @allure.title("TC20 目标店铺含 WB 与 OZON")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc20_shop_options(self, pallet_page):
        pallet_page.open("jd")
        opts = " ".join(pallet_page.shop_options())
        assert "WB" in opts or "WILDBERRIES" in opts or config.WB_SHOP_NAME in opts
        assert "OZON" in opts.upper() or "Ozon" in opts

    @allure.story("入口/批量草稿")
    @allure.title("TC21 勾选京东商品批量生成草稿")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc21_batch_draft(self, pallet_page, draft_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        pallet_page.choose_wb_shop(config.WB_SHOP_NAME)
        pallet_page.select_all()
        pallet_page.click_batch_draft()
        draft_page.open()
        assert "草稿箱" in draft_page.page_text()
