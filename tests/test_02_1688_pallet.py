# -*- coding: utf-8 -*-
"""TC09-TC14 1688精选入口。"""
import allure
import pytest

import config

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)


@allure.epic("如斯达ERP")
@allure.feature("WB商品刊登-1688精选")
class Test1688Pallet:
    @allure.story("入口/页面加载")
    @allure.title("TC09 1688精选 Tab 与筛选项")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc09_tab_loaded(self, pallet_page):
        pallet_page.open("1688")
        assert "tab=pallet" in pallet_page.url()
        flags = pallet_page.ui_controls_present()
        assert flags["查询"] and flags["重置"]
        assert flags["批量生成草稿"]
        assert flags["一级类目"]

    @allure.story("入口/空列表")
    @allure.title("TC10 无数据时展示暂无1688精选商品")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc10_empty_or_list(self, pallet_page):
        pallet_page.open("1688").wait_loaded("1688")
        if pallet_page.has_goods():
            pytest.skip("当前环境1688精选有货，跳过空列表断言")
        assert pallet_page.empty_text("1688") in pallet_page.page_text()

    @allure.story("入口/未勾选批量")
    @allure.title("TC11 未勾选点批量生成草稿应提示")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc11_batch_without_select(self, pallet_page):
        pallet_page.open("1688").wait_loaded("1688")
        tip = pallet_page.click_batch_draft()
        assert any(k in tip for k in ("勾选", "请先", "至少", "选择")), tip[:300]

    @allure.story("入口/一键刊登WB")
    @allure.title("TC12 有货时一键刊登进入WB编辑页")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    @pytest.mark.need_goods
    def test_tc12_one_click_wb(self, pallet_page, listing_page):
        pallet_page.open("1688").wait_loaded("1688")
        if not pallet_page.has_goods():
            pytest.skip("1688精选无商品")
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        assert listing_page.is_open()
        assert listing_page.steps_present()
        assert listing_page.has_recommended_category(), (
            f"1688精选进入刊登页未带推荐类目: {listing_page.category_value()!r}"
        )

    @allure.story("入口/批量草稿")
    @allure.title("TC13 勾选后批量生成草稿")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_tc13_batch_draft(self, pallet_page, draft_page):
        pallet_page.open("1688").wait_loaded("1688")
        if not pallet_page.has_goods():
            pytest.skip("1688精选无商品")
        pallet_page.choose_wb_shop("WILDBERRIES")
        pallet_page.select_all()
        pallet_page.click_batch_draft()
        draft_page.open()
        assert "草稿" in draft_page.page_text()

    @allure.story("入口/筛选排序")
    @allure.title("TC14 类目与排序控件可用")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_tc14_filters(self, pallet_page):
        pallet_page.open("1688")
        flags = pallet_page.ui_controls_present()
        assert flags["同步时间"] or flags["货源价"]
        pallet_page.button("重置")
        assert "1688精选" in pallet_page.page_text()
