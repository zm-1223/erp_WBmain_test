# -*- coding: utf-8 -*-
"""从货源卡片/详情文案解析包装重量 kg、尺寸 cm。"""
from __future__ import annotations

import math
import re


def parse_number(raw: str):
    text = (raw or "").strip().replace(",", "")
    if not text:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    if not m:
        return None
    val = float(m.group(0))
    if val <= 0:
        return None
    return val


def parse_package(text: str) -> dict:
    blob = text or ""
    weight = None
    m = re.search(
        r"(?:包装\s*)?重量\s*(?:kg|KG|千克)?\s*[：:]*\s*(\d+(?:\.\d+)?)",
        blob,
        re.I,
    )
    if m:
        weight = parse_number(m.group(1))
    dims = [None, None, None]
    m = re.search(
        r"(?:包装\s*)?尺寸(?:\s*cm)?\s*[：:]*\s*"
        r"(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)\s*[x×*]\s*(\d+(?:\.\d+)?)",
        blob,
        re.I,
    )
    if not m:
        m = re.search(
            r"长\s*[：:]?\s*(\d+(?:\.\d+)?)\s*"
            r"(?:cm)?\s*[,，\s]*"
            r"宽\s*[：:]?\s*(\d+(?:\.\d+)?)\s*"
            r"(?:cm)?\s*[,，\s]*"
            r"高\s*[：:]?\s*(\d+(?:\.\d+)?)",
            blob,
            re.I,
        )
    if m:
        dims = [parse_number(m.group(i)) for i in (1, 2, 3)]
    return {"weight": weight, "dims": dims}


def same_num(a, b, abs_tol: float = 0.05) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=abs_tol)
