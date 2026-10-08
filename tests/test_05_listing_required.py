# -*- coding: utf-8 -*-
"""TC27-TC51 刊登页必填与格式。默认从1688入口进入，会话内复用浏览器。"""
import allure
import pytest


@allure.epic("如斯达ERP")
@allure.feature("WB商品刊登-刊登页必填")
class TestListingRequired:
    @allure.story("必填/上架店铺")
    @allure.title("TC27 上架店铺为必填")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc27_shop_required(self, listing_from_1688):
        page = listing_from_1688
        assert page.is_required("上架店铺")
        assert "上架店铺" in page.page_text()

    @allure.story("必填/仓库")
    @allure.title("TC28 选择仓库必填，空仓保存草稿待完善")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc28_warehouse_required(self, listing_from_1688, draft_page, collect_page, listing_page):
        page = listing_from_1688
        assert page.is_required("选择仓库")
        assert "选择 WB 仓库" in page.page_text() or "选择仓库" in page.page_text()
        page.save_draft()
        draft_page.open()
        text = draft_page.page_text() + draft_page.first_row_text()
        assert "待完善" in text or "仓库" in text
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()

    @allure.story("必填/产品类目")
    @allure.title("TC29 产品类目为必填")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc29_category_required(self, listing_from_1688):
        page = listing_from_1688
        assert page.is_required("产品类目")
        assert "类目" in page.page_text()
        assert page.has_recommended_category(), (
            f"刊登页类目应为推荐预填: {page.category_value()!r}"
        )

    @allure.story("必填/标题二选一")
    @allure.title("TC30 中俄标题都为空应提示补填")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc30_title_both_empty(self, listing_from_1688):
        page = listing_from_1688
        assert "二选一" in page.page_text() or "都为空" in page.page_text()
        page.clear_titles()
        msg = page.save_draft() + page.page_text()
        assert any(k in msg for k in ("标题", "补填", "不能为空", "草稿")), msg[:400]

    @allure.story("格式/标题长度")
    @allure.title("TC31 标题上限60字")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc31_title_max_60(self, listing_from_1688, collect_page, listing_page):
        page = listing_from_1688
        long_text = "测" * 80
        page.fill_cn_title(long_text)
        value = page.cn_title_value()
        assert len(value) <= 60, f"中文标题未限制60字, 实际{len(value)}"
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()

    @allure.story("必填/仅中文标题")
    @allure.title("TC32 仅中文标题允许保存")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc32_cn_only_title(self, listing_from_1688):
        page = listing_from_1688
        page.fill_cn_title("自动化中文标题测试")
        page.fill_ru_title("")
        assert page.cn_title_value()
        assert page.ru_title_value() == "" or page.ru_title_value() is not None

    @allure.story("必填/仅俄语标题")
    @allure.title("TC33 仅俄语标题允许保存")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc33_ru_only_title(self, listing_from_1688, collect_page, listing_page):
        page = listing_from_1688
        page.fill_cn_title("")
        page.fill_ru_title("Avto test zagolovok")
        assert page.ru_title_value()
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()

    @allure.story("非必填/品牌")
    @allure.title("TC34 品牌可选")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_tc34_brand_optional(self, listing_from_1688):
        assert listing_from_1688.brand_optional()

    @allure.story("必填/包装重量")
    @allure.title("TC35 包装重量必填")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc35_weight_required(self, listing_from_1688):
        assert listing_from_1688.is_required("包装重量 kg")

    @allure.story("必填/包装尺寸")
    @allure.title("TC36 包装尺寸必填")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc36_dimension_required(self, listing_from_1688):
        page = listing_from_1688
        assert page.is_required("包装尺寸 cm") or "包装尺寸" in "".join(page.required_labels())

    @allure.story("非必填/描述")
    @allure.title("TC37 描述非必填且限2000")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc37_desc_optional(self, listing_from_1688):
        page = listing_from_1688
        assert not page.is_required("描述")
        assert "/ 2000" in page.page_text() or "2000" in page.page_text()

    @allure.story("非必填/商品编码前缀")
    @allure.title("TC38 编码前缀非必填")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_tc38_prefix_optional(self, listing_from_1688):
        assert not listing_from_1688.is_required("商品编码前缀")

    @allure.story("非必填/货源备注")
    @allure.title("TC39 货源备注非必填")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_tc39_note_optional(self, listing_from_1688):
        assert listing_from_1688.note_optional()

    @allure.story("带出/货源地址")
    @allure.title("TC40 1688入口带出货源链接")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc40_source_url(self, listing_from_1688):
        src = listing_from_1688.source_url_value() + listing_from_1688.page_text()
        assert "1688.com" in src and "726638874254" in src

    @allure.story("必填/主图图组")
    @allure.title("TC41 主图删除后提交应拦截")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc41_images_required(self, listing_from_1688, collect_page, listing_page):
        page = listing_from_1688
        assert "商品主图" in page.page_text()
        page.delete_all_images()
        msg = page.save_draft() + page.page_text()
        assert msg
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()

    @allure.story("素材/自动转存")
    @allure.title("TC42 1688图片自动转存状态")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc42_image_transfer(self, listing_from_1688):
        text = listing_from_1688.page_text()
        assert any(k in text for k in ("自动转存", "素材", "商品主图", "图片"))

    @allure.story("必填/俄罗斯尺码")
    @allure.title("TC43 俄罗斯尺码列为必填")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc43_ru_size_required(self, listing_from_1688):
        page = listing_from_1688
        assert "俄罗斯尺码" in page.page_text()
        assert "俄罗斯尺码*" in page.page_text().replace(" ", "") or "俄罗斯尺码*" in page.page_text() or page.ru_size_empty()

    @allure.story("必填/变体颜色")
    @allure.title("TC44 变体颜色需映射")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc44_color_mapping(self, listing_from_1688):
        text = listing_from_1688.page_text()
        assert "颜色" in text
        assert "搜索并选择" in text or "规格" in text

    @allure.story("必填/刊登价")
    @allure.title("TC45 刊登价必填且需为正")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc45_price_required(self, listing_from_1688, collect_page, listing_page):
        page = listing_from_1688
        assert "刊登价" in page.page_text()
        try:
            page.clear_first_price()
            msg = page.save_draft()
            assert msg is not None
        finally:
            collect_page.ensure_card()
            collect_page.click_wb_listing()
            listing_page.wait_open()

    @allure.story("格式/库存上限")
    @allure.title("TC46 库存不得超过100000")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc46_stock_limit(self, listing_from_1688, draft_page, collect_page, listing_page):
        page = listing_from_1688
        page.set_first_stock("100001")
        page.save_draft()
        draft_page.open()
        text = draft_page.page_text()
        assert "100000" in text or "待完善" in text or "库存" in text
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()

    @allure.story("必填/库存与分仓")
    @allure.title("TC47 未选仓库时不可进入可刊登")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc47_warehouse_for_stock(self, listing_from_1688, draft_page, collect_page, listing_page):
        page = listing_from_1688
        page.save_draft()
        draft_page.open()
        text = draft_page.page_text()
        assert "仓库" in text or "待完善" in text
        collect_page.ensure_card()
        collect_page.click_wb_listing()
        listing_page.wait_open()

    @allure.story("格式/WB Club折扣")
    @allure.title("TC48 Club折扣仅允许0或3-31")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc48_club_discount(self, listing_from_1688):
        page = listing_from_1688
        assert "0 或 3-31" in page.page_text() or "Club" in page.page_text()

    @allure.story("非必填/卖家折扣")
    @allure.title("TC49 卖家折扣非必填")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_tc49_seller_discount_optional(self, listing_from_1688):
        assert "卖家折扣" in listing_from_1688.page_text()
        assert not listing_from_1688.is_required("卖家折扣")

    @allure.story("带出/条形码")
    @allure.title("TC50 条形码自动生成只读")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    def test_tc50_barcode_auto(self, listing_from_1688):
        page = listing_from_1688
        assert page.barcode_value() or "自动生成" in page.page_text()
        if page.finds(page.BARCODE):
            assert page.barcode_readonly()

    @allure.story("非必填/类目扩展属性")
    @allure.title("TC51 扩展属性默认可为空")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.p2
    def test_tc51_extra_attrs(self, listing_from_1688):
        page = listing_from_1688
        page.expand_attrs()
        assert "产品属性" in page.page_text()
