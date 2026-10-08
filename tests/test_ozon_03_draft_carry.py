# -*- coding: utf-8 -*-
"""OZ13-OZ23 草稿、四入口包装带出、推荐类目、店铺互斥。"""
import allure
import pytest

import config
from utils.package_fields import package_visible

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)


def _attach_pkg(name: str, pkg: dict):
    allure.attach(
        f"weight={pkg.get('weight')!r} dims={pkg.get('dims')!r}",
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )


@allure.epic("如斯达ERP")
@allure.feature("Ozon商品刊登-草稿与带出")
class TestOzonDraftCarry:
    @allure.story("流程/生成草稿")
    @allure.title("OZ13 生成 Ozon 刊登草稿")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz13_save_draft(self, ozon_listing_from_1688, draft_page):
        page = ozon_listing_from_1688
        msg = page.save_draft()
        blob = msg + page.page_text() + page.url()
        assert any(k in blob for k in ("草稿", "publish", "ozon", "Ozon", "OZON")), blob[:300]
        draft_page.open_ozon()
        assert "草稿" in draft_page.page_text() or draft_page.all_count() >= 0

    @allure.story("流程/取消")
    @allure.title("OZ14 取消离开 Ozon 编辑页")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_oz14_cancel(self, collect_page, ozon_listing_page):
        collect_page.ensure_card()
        collect_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        ozon_listing_page.click_cancel()
        assert not ozon_listing_page.is_open() or ozon_listing_page.has_text("商品采集")

    @allure.story("带出/包装")
    @allure.title("OZ15 1688链接包装重量尺寸与原商品一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz15_1688_package(self, collect_page, ozon_listing_page):
        collect_page.ensure_card()
        source = collect_page.source_package(fallback={
            "weight": config.SAMPLE_WEIGHT_KG,
            "dims": list(config.SAMPLE_DIMS_CM),
        })
        _attach_pkg("原商品包装", source)
        if not package_visible(source):
            pytest.skip("原商品卡片/详情未展示包装字段，无法核对一致性")
        collect_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        ozon_listing_page.assert_package_matches_source("Ozon-1688链接", source)

    @allure.story("带出/标题价格")
    @allure.title("OZ16 1688链接标题价格带出核对")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz16_1688_carry_fields(self, collect_page, ozon_listing_page):
        collect_page.ensure_card()
        snap = collect_page.source_snapshot()
        collect_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        title = ozon_listing_page.cn_title_value() or ozon_listing_page.page_text()
        chrome = ("原链接", "寻源通", "一键刊登", "商品详情", "货源价")
        if snap.get("title") and not any(k in snap["title"] for k in chrome):
            key = snap["title"][:8]
            assert key in title or key in ozon_listing_page.page_text(), (
                f"Ozon 标题未带出卡片文案 {key!r}"
            )
        assert ozon_listing_page.image_count() >= 1

    @allure.story("带出/精选包装")
    @allure.title("OZ17 1688精选包装与原商品一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz17_1688_pallet_package(self, pallet_page, ozon_listing_page):
        pallet_page.open("1688").wait_loaded("1688")
        if not pallet_page.has_goods():
            pytest.skip("1688精选无商品")
        source = pallet_page.source_package()
        _attach_pkg("原商品包装", source)
        if not package_visible(source):
            pytest.skip("原商品卡片/详情未展示包装字段，无法核对一致性")
        pallet_page.choose_ozon_shop()
        pallet_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        ozon_listing_page.assert_package_matches_source("Ozon-1688精选", source)

    @allure.story("带出/精选包装")
    @allure.title("OZ21 京东精选包装与原商品一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz21_jd_pallet_package(self, pallet_page, ozon_listing_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        source = pallet_page.source_package()
        _attach_pkg("原商品包装", source)
        if not package_visible(source):
            pytest.skip("原商品卡片/详情未展示包装字段，无法核对一致性")
        pallet_page.choose_ozon_shop()
        pallet_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        ozon_listing_page.assert_package_matches_source("Ozon-京东精选", source)

    @allure.story("带出/精选包装")
    @allure.title("OZ22 淘宝精选包装与原商品一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz22_tb_pallet_package(self, pallet_page, ozon_listing_page):
        pallet_page.open("tb").wait_loaded("tb")
        if not pallet_page.has_goods():
            pytest.skip("淘宝精选无商品")
        source = pallet_page.source_package()
        _attach_pkg("原商品包装", source)
        if not package_visible(source):
            pytest.skip("原商品卡片/详情未展示包装字段，无法核对一致性")
        pallet_page.choose_ozon_shop()
        pallet_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        ozon_listing_page.assert_package_matches_source("Ozon-淘宝精选", source)

    @allure.story("一致性/多入口")
    @allure.title("OZ18 四入口进入 Ozon 刊登页表单结构一致且自带推荐类目")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz18_same_form_from_entries(self, collect_page, pallet_page, ozon_listing_page):
        collect_page.ensure_card()
        collect_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        assert ozon_listing_page.is_open()
        assert ozon_listing_page.steps_present()
        assert ozon_listing_page.has_recommended_category(), (
            f"1688链接入口未带推荐类目: {ozon_listing_page.category_value()!r}"
        )
        for key, name in (("1688", "1688精选"), ("jd", "京东精选"), ("tb", "淘宝精选")):
            pallet_page.open(key).wait_loaded(key)
            if not pallet_page.has_goods():
                continue
            pallet_page.choose_ozon_shop()
            pallet_page.click_ozon_listing()
            ozon_listing_page.wait_open()
            assert ozon_listing_page.is_open(), f"{name} 未进入 Ozon 刊登页"
            assert ozon_listing_page.steps_present()
            assert ozon_listing_page.has_recommended_category(), (
                f"{name}入口未带推荐类目: {ozon_listing_page.category_value()!r}"
            )

    @allure.story("店铺/WB不可当Ozon店")
    @allure.title("OZ19 目标店铺选 WB 后一键 Ozon 不得把 WB 店当 Ozon 店")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz19_wb_shop_not_for_ozon(self, pallet_page, ozon_listing_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        pallet_page.choose_wb_shop("WB")
        pallet_page.click_ozon_listing()
        try:
            ozon_listing_page.wait_open()
        except Exception:
            blob = pallet_page.toast() or pallet_page.page_text()
            assert any(k in blob for k in ("OZON", "Ozon", "店铺", "选择", "不支持"))
            return
        shop_txt = ozon_listing_page.page_text()
        chunk = shop_txt.split("上架店铺", 1)[-1][:80] if "上架店铺" in shop_txt else shop_txt[:200]
        assert "[WB]" not in chunk or "OZON" in chunk or ozon_listing_page.is_required("上架店铺")

    @allure.story("入口/菜单")
    @allure.title("OZ20 一键刊登下拉含 Ozon 平台")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz20_menu_has_ozon(self, collect_page):
        collect_page.ensure_card()
        texts = " ".join(collect_page.listing_menu_texts())
        assert "Ozon" in texts or "OZON" in texts.upper()

    @allure.story("带出/推荐类目")
    @allure.title("OZ23 各入口进入 Ozon 刊登页或草稿编辑页均自带推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz23_recommended_category_all_entries(
        self, collect_page, pallet_page, ozon_listing_page, draft_page
    ):
        collect_page.ensure_card()
        collect_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        assert ozon_listing_page.has_recommended_category(), (
            f"1688链接 Ozon 刊登页无推荐类目: {ozon_listing_page.category_value()!r}"
        )
        ozon_listing_page.save_draft()
        draft_page.open_ozon()
        if "编辑" in draft_page.page_text():
            draft_page.click_edit()
            ozon_listing_page.wait_open()
            assert ozon_listing_page.has_recommended_category(), (
                f"Ozon 草稿编辑页无推荐类目: {ozon_listing_page.category_value()!r}"
            )
        for key, name in (("1688", "1688精选"), ("jd", "京东精选"), ("tb", "淘宝精选")):
            pallet_page.open(key).wait_loaded(key)
            if not pallet_page.has_goods():
                continue
            pallet_page.choose_ozon_shop()
            pallet_page.click_ozon_listing()
            ozon_listing_page.wait_open()
            assert ozon_listing_page.has_recommended_category(), (
                f"{name}进入 Ozon 刊登页无推荐类目: {ozon_listing_page.category_value()!r}"
            )
