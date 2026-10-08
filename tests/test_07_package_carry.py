# -*- coding: utf-8 -*-
"""TC59-TC62 各入口包装重量/尺寸须与原商品一致：有则带入相同值，无则留空。"""
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
@allure.feature("WB商品刊登-包装带出")
class TestPackageCarry:
    @allure.story("带出/包装重量尺寸")
    @allure.title("TC59 1688链接包装带入须与原商品一致")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.p0
    def test_tc59_1688_link_package(self, collect_page, listing_page):
        collect_page.ensure_card()
        source = collect_page.source_package(
            fallback={
                "weight": config.SAMPLE_WEIGHT_KG,
                "dims": list(config.SAMPLE_DIMS_CM),
            }
        )
        _attach_pkg("原商品包装", source)
        collect_page.click_wb_listing()
        listing_page.wait_open()
        listing_page.assert_package_matches_source("1688链接采集", source)

    @allure.story("带出/包装重量尺寸")
    @allure.title("TC60 1688精选包装带入须与原商品一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_tc60_1688_pallet_package(self, pallet_page, listing_page):
        pallet_page.open("1688").wait_loaded("1688")
        if not pallet_page.has_goods():
            pytest.skip("1688精选无商品")
        source = pallet_page.source_package()
        _attach_pkg("原商品包装", source)
        if not package_visible(source):
            pytest.skip("原商品卡片/详情未展示包装字段，无法核对一致性")
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        listing_page.assert_package_matches_source("1688精选", source)

    @allure.story("带出/包装重量尺寸")
    @allure.title("TC61 京东精选包装带入须与原商品一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_tc61_jd_pallet_package(self, pallet_page, listing_page):
        pallet_page.open("jd").wait_loaded("jd")
        if not pallet_page.has_goods():
            pytest.skip("京东精选无商品")
        source = pallet_page.source_package()
        _attach_pkg("原商品包装", source)
        if not package_visible(source):
            pytest.skip("原商品卡片/详情未展示包装字段，无法核对一致性")
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        listing_page.assert_package_matches_source("京东精选", source)

    @allure.story("带出/包装重量尺寸")
    @allure.title("TC62 淘宝精选包装带入须与原商品一致")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.p1
    @pytest.mark.need_goods
    def test_tc62_tb_pallet_package(self, pallet_page, listing_page):
        pallet_page.open("tb").wait_loaded("tb")
        if not pallet_page.has_goods():
            pytest.skip("淘宝精选无商品")
        source = pallet_page.source_package()
        _attach_pkg("原商品包装", source)
        if not package_visible(source):
            pytest.skip("原商品卡片/详情未展示包装字段，无法核对一致性")
        pallet_page.click_wb_listing()
        listing_page.wait_open()
        listing_page.assert_package_matches_source("淘宝精选", source)
