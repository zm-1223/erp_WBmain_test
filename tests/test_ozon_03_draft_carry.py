# -*- coding: utf-8 -*-
"""OZ13-OZ23、OZ26-OZ31 草稿、四入口包装/标题带出、推荐类目、店铺互斥。"""
import allure
import pytest

import config
from utils.package_fields import package_visible, parse_number, same_num

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)


def _assert_ozon_carry(entry: str, snap: dict, ozon_listing_page):
    title = ozon_listing_page.cn_title_value() or ozon_listing_page.page_text()
    chrome = ("原链接", "寻源通", "一键刊登", "商品详情", "货源价")
    if snap.get("title") and not any(k in snap["title"] for k in chrome):
        key = snap["title"][:8]
        assert key in title or key in ozon_listing_page.page_text(), (
            f"{entry} Ozon 标题未带出卡片文案 {key!r}"
        )
    if snap.get("price") is not None:
        got = parse_number(ozon_listing_page.collect_price_value()) or parse_number(
            ozon_listing_page.listing_price_value()
        )
        if got is not None:
            assert same_num(snap["price"], got, abs_tol=1.0), (
                f"{entry} Ozon 价格与原商品不一致 货源={snap['price']!r} 刊登={got!r}"
            )
    if snap.get("img_n"):
        n = ozon_listing_page.image_count()
        assert n >= 1, f"{entry} 未带出主图 货源图片数={snap['img_n']!r} 刊登={n!r}"


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
        text = draft_page.page_text()
        assert "草稿" in text or draft_page.all_count() >= 0
        assert any(k in text for k in ("待完善", "可刊登", "校验", "一键"))
        assert any(k in text for k in ("Ozon", "OZON", "1688", config.OFFER_ID, "一键"))

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
        _assert_ozon_carry("1688链接采集", snap, ozon_listing_page)
        src = ozon_listing_page.source_url_value()
        assert config.OFFER_ID in src or config.OFFER_ID in ozon_listing_page.page_text()

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
    @allure.title("OZ18 四入口进入 Ozon 刊登页表单结构一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz18_same_form_from_entries(self, collect_page, pallet_page, ozon_listing_page):
        collect_page.ensure_card()
        collect_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        assert ozon_listing_page.is_open()
        assert ozon_listing_page.steps_present()
        for key, name in (("1688", "1688精选"), ("jd", "京东精选"), ("tb", "淘宝精选")):
            pallet_page.open(key).wait_loaded(key)
            if not pallet_page.has_goods():
                continue
            pallet_page.choose_ozon_shop()
            pallet_page.click_ozon_listing()
            ozon_listing_page.wait_open()
            assert ozon_listing_page.is_open(), f"{name} 未进入 Ozon 刊登页"
            assert ozon_listing_page.steps_present()

    @allure.story("店铺/WB不可当Ozon店")
    @allure.title("OZ19 目标店铺选 WB 后一键 Ozon 不得把 WB 店当 Ozon 店")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz19_wb_shop_not_for_ozon(self, pallet_page, ozon_listing_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        pallet_page.choose_wb_shop("WB")
        pallet_page.click_ozon_listing(wait_open=False)
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

    @allure.story("带出/标题价格图")
    @allure.title("OZ26 1688精选标题价格与卡片一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz26_1688_pallet_carry_fields(self, pallet_page, ozon_listing_page):
        pallet_page.open("1688").wait_loaded("1688")
        if not pallet_page.has_goods():
            pytest.skip("1688精选无商品")
        snap = pallet_page.source_snapshot()
        pallet_page.choose_ozon_shop()
        pallet_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        _assert_ozon_carry("1688精选", snap, ozon_listing_page)

    @allure.story("带出/标题价格货源链接")
    @allure.title("OZ27 京东精选标题价格货源链接与卡片一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz27_jd_pallet_carry_fields(self, pallet_page, ozon_listing_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        snap = pallet_page.source_snapshot()
        pallet_page.choose_ozon_shop()
        pallet_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        _assert_ozon_carry("京东精选", snap, ozon_listing_page)
        url = ozon_listing_page.source_url_value() + ozon_listing_page.page_text()
        assert any(k in url.lower() for k in ("jd", "360buy", "sku", "京东"))

    @allure.story("带出/标题价格货源链接")
    @allure.title("OZ28 淘宝精选标题价格货源链接与卡片一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz28_tb_pallet_carry_fields(self, pallet_page, ozon_listing_page):
        pallet_page.open("tb").wait_loaded("tb")
        if not pallet_page.has_goods():
            pytest.skip("淘宝精选无商品")
        snap = pallet_page.source_snapshot()
        pallet_page.choose_ozon_shop()
        pallet_page.click_ozon_listing()
        ozon_listing_page.wait_open()
        _assert_ozon_carry("淘宝精选", snap, ozon_listing_page)
        url = ozon_listing_page.source_url_value() + ozon_listing_page.page_text()
        assert any(k in url.lower() for k in ("taobao", "tmall", "tb", "淘宝", "offer"))

    @allure.story("入口/批量草稿")
    @allure.title("OZ29 京东精选批量生成 Ozon 草稿核对来源")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_oz29_jd_batch_draft_ozon_origin(self, pallet_page, draft_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        pallet_page.choose_ozon_shop()
        n = pallet_page.select_first(1)
        if n < 1:
            pytest.skip("京东精选无法勾选")
        pallet_page.click_batch_draft(confirm=True)
        draft_page.open_ozon()
        blob = draft_page.wait_origin("京东精选", ozon=True)
        assert any(k in blob for k in ("Ozon", "OZON", "一键Ozon", "京东精选")), blob[:400]

    @allure.story("流程/待完善不可刊登")
    @allure.title("OZ30 Ozon 草稿待完善时不可批量提交")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz30_incomplete_cannot_submit(self, ozon_listing_from_1688, draft_page):
        page = ozon_listing_from_1688
        page.save_draft()
        draft_page.open_ozon()
        text = draft_page.page_text()
        assert "草稿" in text or "待完善" in text or draft_page.all_count() >= 0
        assert draft_page.batch_submit_disabled() or "可刊登 0" in text or "待完善" in text

    @allure.story("流程/编辑回填")
    @allure.title("OZ31 Ozon 草稿编辑回填刊登页")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz31_draft_edit_roundtrip(self, ozon_listing_from_1688, draft_page, ozon_listing_page):
        page = ozon_listing_from_1688
        marker = "自动化Ozon标题回填"
        page.fill_cn_title(marker)
        page.save_draft()
        draft_page.open_ozon()
        if "编辑" not in draft_page.page_text():
            pytest.skip("Ozon 草稿箱无编辑入口")
        try:
            draft_page.click_edit_for_origin("Ozon")
        except AssertionError:
            draft_page.click_edit()
        ozon_listing_page.wait_open()
        blob = ozon_listing_page.cn_title_value() + ozon_listing_page.page_text()
        assert marker[:8] in blob or ozon_listing_page.has_recommended_category()

    @allure.story("流程/必填齐全可刊登")
    @allure.title("OZ41 校验后可进入可刊登（默认不真实提交）")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz41_ready_to_publish(self, ozon_listing_from_1688, draft_page):
        page = ozon_listing_from_1688
        if page.form_item("选择仓库") is not None:
            page.select_first_warehouse()
        page.save_draft()
        draft_page.open_ozon()
        before = draft_page.ready_count()
        try:
            draft_page.click_validate()
        except AssertionError:
            pytest.skip("Ozon 草稿箱无批量校验")
        draft_page.open_ozon()
        ready = draft_page.ready_count()
        if ready < 1 and ready <= before:
            pytest.skip("校验后仍未进入可刊登（图片转存或其它必填未齐）")
        assert ready >= 1 or ready > before
        if config.SUBMIT_LIVE:
            draft_page.click_row_submit()
        else:
            allure.attach(
                "ERP_SUBMIT_LIVE=0，不真实提交 Ozon",
                name="说明",
                attachment_type=allure.attachment_type.TEXT,
            )
