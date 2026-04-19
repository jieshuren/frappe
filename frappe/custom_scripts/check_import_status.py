#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查导入情况
"""
import json
import frappe

def check_import_status():
    """检查哪些科目被导入，哪些被跳过"""
    company = '大庆市华烁油气开采技术服务有限公司'
    json_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/期初余额.json'

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("=" * 80)
    print("导入状态检查")
    print("=" * 80)

    imported = []
    skipped_group = []
    skipped_not_found = []
    skipped_zero = []

    for item in data:
        code = item['account_code']
        balance = item['balance']
        customer = item.get('customer')
        supplier = item.get('supplier')

        if balance == 0:
            skipped_zero.append(f"{code} - {item['account_name']}")
            continue

        # 应收应付
        if customer or supplier or (code.startswith('1122') and code != '1122' and code != '1122.0'):
            imported.append(f"{code} - {item['account_name']}: {balance:,.2f}")
            continue

        # 其他科目
        account = frappe.db.get_value('Account', {
            'company': company,
            'account_number': code
        }, 'name')

        if not account:
            skipped_not_found.append(f"{code} - {item['account_name']}: {balance:,.2f}")
            continue

        is_group = frappe.db.get_value('Account', account, 'is_group')
        if is_group:
            skipped_group.append(f"{code} - {item['account_name']}: {balance:,.2f}")
            continue

        imported.append(f"{code} - {item['account_name']}: {balance:,.2f}")

    print(f"\n已导入: {len(imported)} 条")
    print(f"跳过（组科目）: {len(skipped_group)} 条")
    print(f"跳过（找不到科目）: {len(skipped_not_found)} 条")
    print(f"跳过（余额为0）: {len(skipped_zero)} 条")

    if skipped_not_found:
        print("\n找不到的科目（前10条）:")
        for item in skipped_not_found[:10]:
            print(f"  {item}")

    print("\n" + "=" * 80)
