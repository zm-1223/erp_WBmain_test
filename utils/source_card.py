# -*- coding: utf-8 -*-
"""从精选/采集卡片文案解析标题、货源价、SKU 数、图片数。"""
from __future__ import annotations

import re

from utils.package_fields import parse_number


def parse_source_card(text: str) -> dict:
    blob = text or ""
    offer = None
    m = re.search(r"(?:offerId|offerid|skuId|skuid)\s*[：:]*\s*(\w+)", blob, re.I)
    if m:
        offer = m.group(1)
    price = None
    m = re.search(r"(?:货源价|采集价)\s*[：:]*\s*[¥￥]?\s*(\d+(?:\.\d+)?)", blob)
    if not m:
        m = re.search(r"[¥￥]\s*(\d+(?:\.\d+)?)", blob)
    if m:
        price = parse_number(m.group(1))
    sku_n = None
    m = re.search(r"SKU\s*(?:数量)?\s*[：:]*\s*(\d+)", blob, re.I)
    if m:
        sku_n = int(m.group(1))
    img_n = None
    m = re.search(r"图片\s*(?:张数|数)?\s*[：:]*\s*(\d+)", blob)
    if m:
        img_n = int(m.group(1))
    skip_title = re.compile(
        r"一键刊登|查看|offerId|skuId|货源价|已选|寻源通|商品详情|Offer ID|"
        r"采购价|参考价|价格区间|原链接|SKU|图片|张数|打开\s*1688|全部 SKU",
        re.I,
    )
    title = ""
    candidates = []
    for line in blob.splitlines():
        line = line.strip()
        if len(line) < 4 or len(line) > 80:
            continue
        if skip_title.search(line):
            continue
        if line.startswith("¥") or line.startswith("￥"):
            continue
        if re.fullmatch(r"[\d.]+", line):
            continue
        cjk = len(re.findall(r"[\u4e00-\u9fff]", line))
        if cjk < 2 and not re.search(r"[A-Za-z]{3,}", line):
            continue
        candidates.append(line)
    if candidates:
        title = max(candidates, key=lambda s: (len(re.findall(r"[\u4e00-\u9fff]", s)), len(s)))
    return {
        "offer": offer,
        "price": price,
        "sku_n": sku_n,
        "img_n": img_n,
        "title": title,
        "raw": blob[:800],
    }
