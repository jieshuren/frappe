#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正中文翻译
"""
import frappe

def fix_translations():
    """修正借贷翻译"""

    print("=" * 60)
    print("修正中文翻译")
    print("=" * 60)

    # 需要修正的翻译
    translations = {
        'Debit': '借方',
        'Credit': '贷方',
        'Dr': '借',
        'Cr': '贷',
        'Debit Amount': '借方金额',
        'Credit Amount': '贷方金额',
    }

    for source, target in translations.items():
        # 检查是否已存在
        existing = frappe.db.get_value('Translation', {
            'language': 'zh',
            'source_text': source
        }, 'name')

        if existing:
            # 更新
            frappe.db.set_value('Translation', existing, 'translated_text', target)
            print(f"✓ 更新: {source} -> {target}")
        else:
            # 创建新翻译
            doc = frappe.get_doc({
                'doctype': 'Translation',
                'language': 'zh',
                'source_text': source,
                'translated_text': target
            })
            doc.insert()
            print(f"✓ 创建: {source} -> {target}")

    frappe.db.commit()

    print("\n需要清除缓存才能生效")
    print("=" * 60)
