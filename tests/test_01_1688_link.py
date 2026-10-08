# -*- coding: utf-8 -*-
"""TC01-TC08 1688 链接采集入口。"""
import allure
import pytest

import config


@allure.epic("如斯达ERP")
@allure.feature("WB商品刊登-1688链接采集")
class Test1688LinkCollect:
    @allure.story("入口/空值")
    @allure.title("TC01 空链接点击拉取商品应提示")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc01_empty_link(self, on_collect):
        on_collect.fill_links("")
        on_collect.pull()
        tip = on_collect.toast(5) + on_collect.page_text()
        assert any(
            k in tip for k in ("请输入", "链接", "不能为空", "必填", "无效")
        ), f"空链接未拦截: {tip[:200]}"

    @allure.story("入口/非法链接")
    @allure.title("TC02 非1688链接拉取应失败")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc02_invalid_link(self, on_collect):
        on_collect.fill_links(config.INVALID_LINK)
        on_collect.pull()
        tip = on_collect.toast(6) + on_collect.page_text()
        assert not on_collect.card_visible() or any(
            k in tip for k in ("无效", "不支持", "失败", "错误", "无法")
        ), f"非法链接未失败: {tip[:300]}"

    @allure.story("入口/合法短链")
    @allure.title("TC03 短链拉取成功展示商品卡")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc03_short_link_pull(self, on_collect):
        on_collect.fill_links(config.LINK_1688_SHORT)
        on_collect.pull_and_wait_offer()
        text = on_collect.page_text()
        assert config.OFFER_ID in text
        assert "一键刊登" in text
        assert "查看详情" in text
        assert "1688 原链接" in text or "1688原链接" in text.replace(" ", "")
        assert "SKU" in text or "sku" in text.lower()

    @allure.story("入口/带追踪参数长链")
    @allure.title("TC04 长链按 offerId 拉取成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc04_full_link_pull(self, on_collect):
        on_collect.fill_links(config.LINK_1688_FULL)
        on_collect.pull_and_wait_offer()
        assert on_collect.card_visible()

    @allure.story("入口/多链接")
    @allure.title("TC05 逗号分隔多链接可拉取合法项")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc05_multi_links(self, on_collect):
        mixed = config.LINK_1688_SHORT + "," + config.INVALID_LINK
        on_collect.fill_links(mixed)
        on_collect.pull_and_wait_offer()
        assert config.OFFER_ID in on_collect.page_text()

    @allure.story("入口/原链接")
    @allure.title("TC06 点击1688原链接跳转详情")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc06_origin_link(self, on_collect):
        on_collect.ensure_card()
        before = on_collect.driver.window_handles[:]
        on_collect.click_origin_link()
        after = on_collect.driver.window_handles
        if len(after) > len(before):
            on_collect.driver.switch_to.window(after[-1])
            url = on_collect.url()
            on_collect.close_extra_tabs()
            assert config.OFFER_ID in url or "1688.com" in url
        else:
            assert config.OFFER_ID in on_collect.url() or "1688.com" in on_collect.url()

    @allure.story("入口/平台选择")
    @allure.title("TC07 一键刊登下拉含 WB 与 Ozon")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc07_one_click_menu(self, on_collect):
        on_collect.ensure_card()
        texts = " ".join(on_collect.listing_menu_texts())
        assert "WB" in texts
        assert "Ozon" in texts or "OZON" in texts.upper()

    @allure.story("入口/进入刊登页")
    @allure.title("TC08 一键刊登 WB 进入编辑页并预填")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc08_enter_wb_listing(self, on_collect, listing_page):
        on_collect.ensure_card()
        on_collect.click_wb_listing()
        listing_page.wait_open()
        text = listing_page.page_text()
        assert listing_page.is_open()
        assert config.OFFER_ID in text or config.OFFER_ID in listing_page.source_url_value()
        assert "标题" in text
        assert listing_page.steps_present()
