# -*- coding: utf-8 -*-
"""OZ32-OZ36 精选页在 OZON 店铺下的结构、未勾选、批量来源与取消。"""
import allure
import pytest

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)

_PALLETS = (
    ("1688", "1688精选"),
    ("jd", "京东精选"),
    ("tb", "淘宝精选"),
)


def _need_ozon_shop(pallet_page):
    chosen = pallet_page.choose_ozon_shop()
    if not chosen:
        pytest.skip("无 OZON 店铺可选")
    return chosen


@allure.epic("如斯达ERP")
@allure.feature("Ozon商品刊登-精选入口")
class TestOzonPallet:
    @allure.story("入口/页面结构")
    @allure.title("OZ32 三精选在 OZON 店下仍有筛选与一键刊登")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz32_pallet_shell_with_ozon_shop(self, pallet_page):
        for key, name in _PALLETS:
            pallet_page.open(key).wait_loaded(key)
            flags = pallet_page.ui_controls_present()
            assert flags["查询"] and flags["重置"], f"{name} 缺少查询/重置"
            assert flags["批量生成草稿"], f"{name} 缺少批量生成草稿"
            assert flags["同步时间"] or flags["货源价"], f"{name} 缺少排序"
            _need_ozon_shop(pallet_page)
            if pallet_page.has_goods():
                assert pallet_page.one_click_elements(), f"{name} 有货但无一键刊登"
            else:
                blob = pallet_page.page_text()
                assert pallet_page.empty_text(key) in blob or "暂无" in blob, name

    @allure.story("入口/未勾选批量")
    @allure.title("OZ33 目标店为 OZON 时未勾选批量应提示")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz33_batch_without_select(self, pallet_page):
        for key, name in _PALLETS:
            pallet_page.open(key).wait_loaded(key)
            _need_ozon_shop(pallet_page)
            tip = pallet_page.click_batch_draft()
            assert any(k in tip for k in ("勾选", "请先", "至少", "选择")), f"{name}: {tip[:300]}"

    @allure.story("入口/批量草稿")
    @allure.title("OZ34 1688精选批量生成 Ozon 草稿核对来源")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz34_1688_batch_origin(self, pallet_page, draft_page):
        pallet_page.open("1688").wait_loaded("1688")
        if not pallet_page.has_goods():
            pytest.skip("1688精选无商品")
        _need_ozon_shop(pallet_page)
        if pallet_page.select_first(1) < 1:
            pytest.skip("1688精选无法勾选")
        pallet_page.click_batch_draft(confirm=True)
        draft_page.open_ozon()
        blob = draft_page.wait_origin("1688精选", ozon=True)
        assert "1688精选" in blob

    @allure.story("入口/批量草稿")
    @allure.title("OZ35 淘宝精选批量生成 Ozon 草稿核对来源")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz35_tb_batch_origin(self, pallet_page, draft_page):
        pallet_page.open("tb").wait_loaded("tb")
        if not pallet_page.has_goods():
            pytest.skip("淘宝精选无商品")
        _need_ozon_shop(pallet_page)
        if pallet_page.select_first(1) < 1:
            pytest.skip("淘宝精选无法勾选")
        pallet_page.click_batch_draft(confirm=True)
        draft_page.open_ozon()
        blob = draft_page.wait_origin("淘宝精选", ozon=True)
        assert "淘宝精选" in blob

    @allure.story("弹窗/批量草稿确认取消")
    @allure.title("OZ36 批量草稿取消不写入、确定才写入 Ozon 草稿箱")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz36_batch_cancel_then_confirm(self, pallet_page, draft_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        draft_page.open_ozon()
        before = draft_page.all_count()
        pallet_page.open("jd").wait_loaded("jd")
        _need_ozon_shop(pallet_page)
        pallet_page.select_first(1)
        pallet_page.click_batch_draft(confirm=False)
        draft_page.open_ozon()
        assert draft_page.all_count() == before, "点取消后 Ozon 草稿箱条数不应增加"
        pallet_page.open("jd").wait_loaded("jd")
        _need_ozon_shop(pallet_page)
        pallet_page.select_first(1)
        pallet_page.click_batch_draft(confirm=True)
        draft_page.open_ozon()
        draft_page.wait_origin("京东精选", ozon=True)
        assert draft_page.all_count() >= before
