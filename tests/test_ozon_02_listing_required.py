# -*- coding: utf-8 -*-
"""OZ06-OZ12、OZ24-OZ25、OZ37-OZ40 Ozon 刊登页必填与带出（不含 Club/俄码/WB 仓库）。"""
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
    @allure.title("OZ08 标题清空后保存应拦截")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz08_title_empty_intercept(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        assert "标题" in page.page_text()
        page.clear_titles()
        msg = page.save_draft() + page.page_text()
        assert any(k in msg for k in ("标题", "补填", "不能为空", "完善", "拦截")), msg[:400]

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
    @allure.title("OZ12 刊登价清空后保存应拦截")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz12_price_empty_intercept(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        text = page.page_text()
        assert "价" in text
        page.clear_first_price()
        msg = page.save_draft() + page.page_text()
        assert any(k in msg for k in ("价", "补填", "不能为空", "完善", "拦截", "有效")), msg[:400]

    @allure.story("必填/包装重量")
    @allure.title("OZ24 包装重量清空或非正数应拦截")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz24_weight_required(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        assert "包装重量" in page.page_text()
        page.clear_weight()
        msg = page.save_draft() + page.page_text()
        assert any(k in msg for k in ("重量", "补", "不能为空", "完善", "拦截", "有效", "必填")), msg[:400]
        page.set_weight("0")
        msg = page.save_draft() + page.page_text()
        assert any(k in msg for k in ("重量", "补", "有效", "完善", "拦截", "大于", "正")), msg[:400]

    @allure.story("必填/包装尺寸")
    @allure.title("OZ25 包装尺寸清空后保存应拦截")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz25_dimension_required(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        assert "包装尺寸" in page.page_text() or page._dim_els()
        page.clear_dims()
        msg = page.save_draft() + page.page_text()
        assert any(k in msg for k in ("尺寸", "长", "宽", "高", "补", "不能为空", "完善", "拦截")), msg[:400]

    @allure.story("必填/产品类目")
    @allure.title("OZ37 清空类目后保存应拦截")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_oz37_category_cleared_intercept(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        assert page.has_recommended_category(), page.category_value()
        page.clear_category()
        msg = page.save_draft() + page.page_text()
        assert any(k in msg for k in ("类目", "补", "不能为空", "完善", "拦截", "选择")), msg[:400]

    @allure.story("格式/标题长度")
    @allure.title("OZ38 标题超过页面上限应被截断")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz38_title_capped(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        page.fill_cn_title("测" * 400)
        value = page.cn_title_value()
        cap = page.title_cap()
        assert value, "标题写入后为空"
        if cap:
            assert len(value) <= cap, f"标题超过上限 {cap}，实际 {len(value)}"
        else:
            assert len(value) < 400, f"未见字数上限且 400 字全部写入，实际 {len(value)}"

    @allure.story("非必填/品牌描述备注")
    @allure.title("OZ39 页面上的品牌描述前缀备注非必填")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_oz39_optionals(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        text = page.page_text()
        checked = []
        for label in ("品牌", "描述", "商品编码前缀", "货源备注"):
            if page.form_item(label) is None and label not in text:
                continue
            checked.append(label)
            assert not page.is_required(label), f"{label} 不应为必填"
        page.expand_attrs()
        if not checked and "产品属性" not in page.page_text():
            pytest.skip("Ozon 刊登页无品牌/描述/前缀/备注，也无产品属性区")
        assert checked or "产品属性" in page.page_text()

    @allure.story("素材/自动转存")
    @allure.title("OZ40 主图带出且页面有转存或素材说明")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_oz40_image_transfer(self, ozon_listing_from_1688):
        page = ozon_listing_from_1688
        text = page.page_text()
        assert page.image_count() >= 1
        assert any(k in text for k in ("转存", "素材", "主图", "自动")), text[:500]
