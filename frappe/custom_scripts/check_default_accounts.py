#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查默认应收应付科目
"""
import frappe

def check_default_accounts():
    """检查默认应收应付科目"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("检查默认应收应付科目")
    print("=" * 60)

    # 检查默认应收
    receivable = frappe.db.get_value('Account', '112201 - 吉林锐普石油 - 华烁',
        ['account_name', 'is_group', 'parent_account'], as_dict=True)
    print('\n默认应收账款:')
    print(f'  科目: 112201 - 吉林锐普石油')
    print(f'  是否组科目: {"是" if receivable.is_group else "否"}')
    print(f'  父科目: {receivable.parent_account}')

    # 检查默认应付
    payable = frappe.db.get_value('Account', '2202 - 应付账款 - 华烁',
        ['account_name', 'is_group', 'parent_account'], as_dict=True)
    print('\n默认应付账款:')
    print(f'  科目: 2202 - 应付账款')
    print(f'  是否组科目: {"是" if payable.is_group else "否"}')
    print(f'  父科目: {payable.parent_account}')

    # 查找应收账款组科目
    receivable_group = frappe.db.get_value('Account', {
        'company': company,
        'account_name': '应收账款',
        'is_group': 1
    }, 'name')
    print(f'\n应收账款组科目: {receivable_group or "不存在"}')

    # 查找应付账款组科目
    payable_group = frappe.db.get_value('Account', {
        'company': company,
        'account_name': '应付账款',
        'is_group': 1
    }, 'name')
    print(f'应付账款组科目: {payable_group or "不存在"}')

    print("\n" + "=" * 60)

    if not receivable.is_group:
        print("⚠️  警告：默认应收账款是明细科目，建议修改")

    if not payable.is_group:
        print("⚠️  警告：默认应付账款是明细科目，建议修改")

    print("=" * 60)
