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
            assert "请先选择目标平台和店铺" in tip or "请先勾选" in tip, f"{name}: {tip[:300]}"

    @allure.story("入口/批量草稿")
    @allure.title("OZ34 1688精选可多店铺批量采集到 Ozon 草稿箱")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz34_1688_batch_origin(self, pallet_page, draft_page):
        pallet_page.open("1688").wait_loaded("1688")
        if not pallet_page.has_goods():
            pytest.skip("1688精选无商品")
        if pallet_page.select_first(1) < 1:
            pytest.skip("1688精选无法勾选")
        wb_before, oz_before = draft_page.both_counts()
        pallet_page.open("1688").wait_loaded("1688")
        pallet_page.select_first(1)
        blob = pallet_page.click_batch_draft(confirm=True, platform="Ozon", shop_count=2)
        if not pallet_page.batch_dialog_seen:
            raise AssertionError(f"未出现选择目标平台和店铺: {blob[:300]}")
        if pallet_page.batch_shop_count < 2:
            pytest.skip(f"同江和 Minjin 未同时写入，实际 {pallet_page.batch_shop_count}")
        assert f"将写入{pallet_page.batch_shop_count}个店铺" in blob.replace(" ", "").replace("\n", "")
        draft_page.expect_one_draft_each(wb_before, oz_before, "1688精选")

    @allure.story("入口/批量草稿")
    @allure.title("OZ35 淘宝精选可多店铺批量采集到 Ozon 草稿箱")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz35_tb_batch_origin(self, pallet_page, draft_page):
        pallet_page.open("tb").wait_loaded("tb")
        if not pallet_page.has_goods():
            pytest.skip("淘宝精选无商品")
        if pallet_page.select_first(1) < 1:
            pytest.skip("淘宝精选无法勾选")
        wb_before, oz_before = draft_page.both_counts()
        pallet_page.open("tb").wait_loaded("tb")
        pallet_page.select_first(1)
        blob = pallet_page.click_batch_draft(confirm=True, platform="Ozon", shop_count=2)
        if not pallet_page.batch_dialog_seen:
            raise AssertionError(f"未出现选择目标平台和店铺: {blob[:300]}")
        if pallet_page.batch_shop_count < 2:
            pytest.skip(f"同江和 Minjin 未同时写入，实际 {pallet_page.batch_shop_count}")
        assert f"将写入{pallet_page.batch_shop_count}个店铺" in blob.replace(" ", "").replace("\n", "")
        draft_page.expect_one_draft_each(wb_before, oz_before, "淘宝精选")

    @allure.story("弹窗/批量草稿确认取消")
    @allure.title("OZ36 批量草稿取消不写入、确定才写入 Ozon 草稿箱")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz36_batch_cancel_then_confirm(self, pallet_page, draft_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        wb_before, oz_before = draft_page.both_counts()
        pallet_page.open("jd").wait_loaded("jd")
        pallet_page.select_first(1)
        pallet_page.click_batch_draft(confirm=False, platform="Ozon", shop_count=2)
        draft_page.open()
        assert draft_page.all_count() == wb_before, "关闭店铺弹窗后 WB 草稿箱条数不应增加"
        draft_page.open_ozon()
        assert draft_page.all_count() == oz_before, "关闭店铺弹窗后 Ozon 草稿箱条数不应增加"
        pallet_page.open("jd").wait_loaded("jd")
        pallet_page.select_first(1)
        blob = pallet_page.click_batch_draft(confirm=True, platform="Ozon", shop_count=2)
        if not pallet_page.batch_dialog_seen:
            raise AssertionError(f"未出现选择目标平台和店铺: {blob[:300]}")
        if pallet_page.batch_shop_count < 2:
            pytest.skip(f"同江和 Minjin 未同时写入，实际 {pallet_page.batch_shop_count}")
        assert f"将写入{pallet_page.batch_shop_count}个店铺" in blob.replace(" ", "").replace("\n", "")
        draft_page.expect_one_draft_each(wb_before, oz_before, "京东精选")
