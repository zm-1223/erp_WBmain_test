# -*- coding: utf-8 -*-
"""多店铺弹窗的行判定。浏览器只负责把复选框周围的文字带回来。"""
from __future__ import annotations

from selenium.common.exceptions import StaleElementReferenceException

_PLATFORMS = ("Wildberries", "Ozon")
_MARKS = ("WB", "OZ", "Wildberries", "Ozon")


def row_blobs(row: dict) -> list[str]:
    own = (row.get("own") or "").strip()
    nxt = (row.get("next") or "").strip()
    prev = (row.get("prev") or "").strip()
    blobs: list[str] = []
    for text in (own, "\n".join(p for p in (own, nxt) if p), "\n".join(p for p in (prev, own) if p)):
        if text and text not in blobs:
            blobs.append(text)
    for text in row.get("ancestors") or []:
        text = (text or "").strip()
        if text and text not in blobs:
            blobs.append(text)
    return blobs


def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def is_platform_row(blobs: list[str], platform: str) -> bool:
    """左侧平台行：一行平台名，并带「家店」。右侧分组标题只有平台名，不算。"""
    for text in blobs:
        if any(k in text for k in ("全选", "清空", "选择目标平台", "将写入")):
            continue
        if "家" not in text:
            continue
        plats = [ln for ln in _lines(text) if ln in _PLATFORMS]
        if plats == [platform]:
            return True
    return False


def is_shop_row(blobs: list[str], keyword: str) -> bool:
    """右侧具体店铺：一个店名，旁边一行 WB 或 OZ。平台行带「家」，不算店铺。"""
    key = (keyword or "").strip().lower()
    if not key:
        return False
    for text in blobs:
        if any(k in text for k in ("全选", "清空", "搜索", "家", "选择目标平台", "将写入")):
            continue
        lines = _lines(text)
        if "WB" not in lines and "OZ" not in lines:
            continue
        names = [ln for ln in lines if ln not in _MARKS]
        if len(names) == 1 and key in names[0].lower():
            return True
    return False


def readable_texts(nodes) -> list[str]:
    """读元素文字。节点已从页面卸掉时跳过，不把整段提示读失败。"""
    texts = []
    for node in nodes:
        try:
            text = (getattr(node, "text", None) or "").strip()
        except StaleElementReferenceException:
            continue
        if text:
            texts.append(text)
    return texts


def join_flash(messages) -> str:
    """顶部消息原样保留。「请先选择目标平台和店铺」就是未勾选提示，不能丢掉。"""
    parts = []
    for message in messages:
        if isinstance(message, str):
            text = message.strip()
        else:
            try:
                text = (getattr(message, "text", None) or "").strip()
            except StaleElementReferenceException:
                continue
        if text:
            parts.append(text)
    return "\n".join(parts)
