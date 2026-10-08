# -*- coding: utf-8 -*-
"""TC22-TC26 淘宝精选入口。"""
import allure
import pytest

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)


@allure.epic("如斯达ERP")
@allure.feature("WB商品刊登-淘宝精选")
class TestTaobaoPallet:
    @allure.story("入口/页面加载")
    @allure.title("TC22 淘宝精选 Tab 结构与1688/京东一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc22_tab_loaded(self, pallet_page):
        pallet_page.open("tb")
        assert "tab=taobao-pallet" in pallet_page.url()
        flags = pallet_page.ui_controls_present()
        assert flags["查询"] and flags["重置"]
        assert flags["批量生成草稿"]
        assert flags["一级类目"]

    @allure.story("入口/空列表")
    @allure.title("TC23 无数据展示暂无淘宝精选商品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc23_empty_or_list(self, pallet_page):
        pallet_page.open("tb").wait_loaded("tb")
        if pallet_page.has_goods():
            pytest.skip("当前环境淘宝精选有货，跳过空列表断言")
        assert pallet_page.empty_text("tb") in pallet_page.page_text()

    @allure.story("入口/未勾选批量")
    @allure.title("TC24 未勾选批量生成草稿应提示")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc24_batch_without_select(self, pallet_page):
        pallet_page.open("tb").wait_loaded("tb")
        tip = pallet_page.click_batch_draft()
        assert any(k in tip for k in ("勾选", "请先", "至少", "选择")), tip[:300]

    @allure.story("入口/一键刊登WB")
    @allure.title("TC25 有货时淘宝精选一键刊登 WB")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.need_goods
    def test_tc25_one_click_wb(self, pallet_page, listing_page):
        pallet_page.open("tb").wait_loaded("tb")
        if not pallet_page.has_goods():
            pytest.skip("淘宝精选无商品")
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        assert listing_page.is_open()
        assert listing_page.steps_present()
        assert listing_page.has_recommended_category(), (
            f"淘宝精选进入刊登页未带推荐类目: {listing_page.category_value()!r}"
        )

    @allure.story("入口/批量草稿")
    @allure.title("TC26 勾选淘宝商品批量生成草稿")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_tc26_batch_draft(self, pallet_page, draft_page, listing_page):
        pallet_page.open("tb").wait_loaded("tb")
        if not pallet_page.has_goods():
            pytest.skip("淘宝精选无商品")
        pallet_page.choose_wb_shop()
        pallet_page.select_first(1)
        pallet_page.click_batch_draft()
        draft_page.open()
        draft_page.wait_origin("淘宝精选")
        draft_page.click_edit_for_origin("淘宝精选")
        listing_page.wait_open()
        assert listing_page.has_recommended_category(), (
            f"淘宝精选草稿编辑页未带推荐类目: {listing_page.category_value()!r}"
        )
