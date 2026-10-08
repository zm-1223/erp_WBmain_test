# -*- coding: utf-8 -*-
"""TC52-TC57 草稿生成与提交。默认不真实提交 WB 刊登。"""
import allure
import pytest

import config

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)


@allure.epic("如斯达ERP")
@allure.feature("WB商品刊登-草稿提交")
class TestDraftSubmit:
    @allure.story("流程/生成草稿")
    @allure.title("TC52 必填未齐生成草稿进入待完善")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc52_save_incomplete_draft(self, collect_page, listing_page, draft_page):
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()
        assert listing_page.has_recommended_category(), (
            f"生成草稿前刊登页未带推荐类目: {listing_page.category_value()!r}"
        )
        msg = listing_page.save_draft()
        assert "草稿" in msg or "草稿" in listing_page.page_text() or "publish" in listing_page.url()
        draft_page.open()
        text = draft_page.page_text()
        assert "待完善" in text
        assert "一键WB刊登" in text or "1688" in text or config.OFFER_ID in text

    @allure.story("流程/待完善不可刊登")
    @allure.title("TC53 待完善草稿不能批量提交")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc53_incomplete_cannot_submit(self, draft_page):
        draft_page.open()
        assert draft_page.batch_submit_disabled() or "可刊登 0" in draft_page.page_text()
        assert "批量校验" in draft_page.page_text() or "可刊登" in draft_page.page_text()

    @allure.story("流程/必填齐全可刊登")
    @allure.title("TC54 补齐必填后可进入可刊登（默认不真实提交）")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc54_ready_to_publish(self, collect_page, listing_page, draft_page):
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()
        listing_page.fill_all_ru_size("42")
        has_wh = listing_page.select_first_warehouse()
        listing_page.save_draft()
        draft_page.open()
        text = draft_page.page_text()
        if not has_wh:
            pytest.skip("当前店铺无可用 WB 仓库，无法补齐必填")
        if config.SUBMIT_LIVE:
            draft_page.click_row_submit()
        else:
            assert "草稿箱" in text
            allure.attach(
                "ERP_SUBMIT_LIVE=0，跳过真实提交刊登",
                name="说明",
                attachment_type=allure.attachment_type.TEXT,
            )

    @allure.story("流程/编辑回填")
    @allure.title("TC55 草稿箱编辑回填刊登页")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc55_edit_draft(self, draft_page, listing_page):
        draft_page.open()
        if "编辑" not in draft_page.page_text():
            pytest.skip("草稿箱无记录")
        draft_page.click_edit()
        listing_page.wait_open()
        assert listing_page.is_open()
        assert listing_page.cn_title_value() or listing_page.steps_present()
        assert listing_page.has_recommended_category(), (
            f"草稿编辑页未回填推荐类目: {listing_page.category_value()!r}"
        )

    @allure.story("流程/取消")
    @allure.title("TC56 取消离开编辑页")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_tc56_cancel(self, collect_page, listing_page):
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()
        listing_page.click_cancel()
        assert "wb-one-click-listing" not in listing_page.url() or listing_page.has_text("商品采集")

    @allure.story("一致性/多入口同页")
    @allure.title("TC57 多入口进入同一套三步刊登表单")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc57_same_form_from_entries(self, collect_page, pallet_page, listing_page):
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()
        assert listing_page.steps_present()
        assert listing_page.is_required("上架店铺")
        assert listing_page.is_required("选择仓库")
        assert listing_page.has_recommended_category(), (
            f"1688链接入口未带推荐类目: {listing_page.category_value()!r}"
        )

        for key, name in (("1688", "1688精选"), ("jd", "京东精选"), ("tb", "淘宝精选")):
            pallet_page.open(key).wait_loaded(key)
            if not pallet_page.has_goods():
                continue
            pallet_page.click_wb_listing()
            listing_page.wait_open()
            assert listing_page.steps_present()
            assert listing_page.has_recommended_category(), (
                f"{name}入口未带推荐类目: {listing_page.category_value()!r}"
            )

    @allure.story("带出/推荐类目")
    @allure.title("TC58 各入口进入刊登页或草稿编辑页均自带推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc58_recommended_category_all_entries(
        self, collect_page, pallet_page, listing_page, draft_page
    ):
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()
        assert listing_page.has_recommended_category(), (
            f"1688链接刊登页无推荐类目: {listing_page.category_value()!r}"
        )
        listing_page.save_draft()
        draft_page.open()
        if "编辑" in draft_page.page_text():
            draft_page.click_edit()
            listing_page.wait_open()
            assert listing_page.has_recommended_category(), (
                f"草稿编辑页无推荐类目: {listing_page.category_value()!r}"
            )

        for key, name in (("1688", "1688精选"), ("jd", "京东精选"), ("tb", "淘宝精选")):
            pallet_page.open(key).wait_loaded(key)
            if not pallet_page.has_goods():
                continue
            pallet_page.click_wb_listing()
            listing_page.wait_open()
            assert listing_page.has_recommended_category(), (
                f"{name}进入刊登页无推荐类目: {listing_page.category_value()!r}"
            )
