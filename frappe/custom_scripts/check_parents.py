#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import frappe

def check_missing_parents():
    """检查缺失的父科目"""
    company = '大庆市华烁油气开采技术服务有限公司'

    # 检查几个应该存在的父科目
    test_parents = ['资产', '银行存款', '应收账款', '固定资产', '负债']

    print("检查父科目状态：")
    for parent_name in test_parents:
        result = frappe.db.get_value('Account',
            {'account_name': parent_name, 'company': company},
            ['name', 'is_group', 'account_type'], as_dict=True)
        if result:
            print(f"  {parent_name}: 存在")
            print(f"    完整名称: {result.name}")
            print(f"    is_group: {result.is_group}")
            print(f"    account_type: {result.account_type}")
        else:
            print(f"  {parent_name}: 不存在 ❌")

    # 统计当前科目数
    total = len(frappe.db.get_all('Account', filters={'company': company}))
    print(f"\n当前总科目数: {total}")
