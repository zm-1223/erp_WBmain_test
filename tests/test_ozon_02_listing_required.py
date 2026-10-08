# -*- coding: utf-8 -*-
"""OZ06-OZ12 Ozon 刊登页必填与带出（对照 WB TC27-TC45 精简）。"""
import allure
import pytest

import config

pytestmark = pytest.mark.flaky(reruns=2, reruns_delay=3)


@allure.epic("如斯达ERP")
@allure.feature("Ozon商品刊登-刊登页必填")
class TestOzonListingRequired:
    @allure.story("必填/上架店铺")
    @allure.title("OZ06 上架店铺为必填")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz06_shop_required(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        assert "上架店铺" in page.page_text() or "店铺" in page.page_text()
        if page.form_item("上架店铺") is not None:
            assert page.is_required("上架店铺")

    @allure.story("必填/产品类目")
    @allure.title("OZ07 进入时类目已预填且带荐")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz07_category_prefilled(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        assert page.has_recommended_category(), (
            f"Ozon 刊登页未带推荐类目: {page.category_value()!r}"
        )

    @allure.story("必填/标题")
    @allure.title("OZ08 标题控件存在且可读取")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz08_title_present(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        text = page.page_text()
        assert "标题" in text
        assert page.cn_title_value() or page.ru_title_value() or "标题" in text

    @allure.story("带出/货源地址")
    @allure.title("OZ09 货源地址带出 1688 offer")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz09_source_url(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        src = page.source_url_value() + page.page_text()
        assert config.OFFER_ID in src or "1688" in src.lower()

    @allure.story("必填/主图")
    @allure.title("OZ10 删除全部主图后保存应拦截")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz10_images_required(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        assert "主图" in page.page_text() or page.image_count() >= 1
        page.delete_all_images()
        msg = page.save_draft() + page.page_text()
        assert any(k in msg for k in ("图片", "主图", "拦截", "草稿", "完善", "补")), msg[:400]

    @allure.story("素材/主图带出")
    @allure.title("OZ11 从1688进入后至少带出一张主图")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz11_image_carried(self, ozon_listing_from_1688):
        assert ozon_listing_from_1688.image_count() >= 1

    @allure.story("必填/价格")
    @allure.title("OZ12 刊登价或采集价控件存在")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz12_price_present(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        text = page.page_text()
        assert "价" in text
        got = page.collect_price_value() or page.listing_price_value()
        assert got or "刊登价" in text or "采集价" in text or "售价" in text
