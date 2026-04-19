#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入科目期初余额到 ERPNext
通过创建 Opening Entry (Journal Entry) 实现
"""
import frappe
import json

def import_opening_entry():
    """创建期初余额凭证"""
    company = '大庆市华烁油气开采技术服务有限公司'
    json_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/期初余额.json'

    print("=" * 60)
    print("导入科目期初余额")
    print("=" * 60)

    # 读取 JSON 文件
    with open(json_file, 'r', encoding='utf-8') as f:
        opening_data = json.load(f)

    print(f"\n读取到 {len(opening_data)} 条期初数据")

    # 统计借贷方总额
    debit_total = sum(item['balance'] for item in opening_data if item['direction'] == '借')
    credit_total = sum(item['balance'] for item in opening_data if item['direction'] == '贷')

    print(f"\n借方总额: {debit_total:,.2f}")
    print(f"贷方总额: {credit_total:,.2f}")
    print(f"差额: {abs(debit_total - credit_total):,.2f}")

    # 准备凭证分录
    accounts_list = []
    not_found = []

    for item in opening_data:
        account_code = item['account_code']
        account_name = item['account_name']
        direction = item['direction']
        balance = abs(item['balance'])

        # 查找科目
        account_info = frappe.db.get_value('Account', {
            'company': company,
            'account_number': account_code
        }, ['name', 'account_type', 'is_group'], as_dict=True)

        if not account_info:
            # 尝试按名称查找
            account_info = frappe.db.get_value('Account', {
                'company': company,
                'account_name': account_name
            }, ['name', 'account_type', 'is_group'], as_dict=True)

        if not account_info:
            not_found.append(f"{account_code} {account_name}")
            continue

        # 跳过组科目
        if account_info.is_group:
            not_found.append(f"{account_code} {account_name} (组科目)")
            continue

        # 跳过应收应付科目（需要指定往来单位）和库存科目（需要库存交易）
        if account_info.account_type in ['Receivable', 'Payable']:
            not_found.append(f"{account_code} {account_name} (需要往来单位)")
            continue

        if account_info.account_type == 'Stock':
            not_found.append(f"{account_code} {account_name} (需要库存交易)")
            continue

        # 添加分录
        entry = {
            'account': account_info.name,
            'debit_in_account_currency': balance if direction == '借' else 0,
            'credit_in_account_currency': balance if direction == '贷' else 0,
        }
        accounts_list.append(entry)

    if not_found:
        print(f"\n⚠️  未找到 {len(not_found)} 个科目：")
        for acc in not_found[:10]:
            print(f"  - {acc}")
        if len(not_found) > 10:
            print(f"  ... 还有 {len(not_found) - 10} 个")

    print(f"\n准备创建凭证，包含 {len(accounts_list)} 个分录")

    # 计算借贷差额
    total_debit = sum(entry['debit_in_account_currency'] for entry in accounts_list)
    total_credit = sum(entry['credit_in_account_currency'] for entry in accounts_list)
    difference = total_debit - total_credit

    print(f"  借方合计: {total_debit:,.2f}")
    print(f"  贷方合计: {total_credit:,.2f}")
    print(f"  差额: {difference:,.2f}")

    # 如果有差额，添加调整分录
    if abs(difference) > 0.01:
        print(f"\n⚠️  借贷不平衡，差额 {difference:,.2f}")
        print("  原因：跳过了应收应付和库存科目")
        print("  添加临时调整科目以平衡凭证")

        # 查找或创建临时调整科目
        temp_account = frappe.db.get_value('Account', {
            'company': company,
            'account_name': '期初余额调整'
        }, 'name')

        if not temp_account:
            # 创建临时调整科目
            temp_doc = frappe.get_doc({
                'doctype': 'Account',
                'account_name': '期初余额调整',
                'company': company,
                'root_type': 'Liability',
                'is_group': 0,
                'parent_account': frappe.db.get_value('Account', {
                    'company': company,
                    'account_name': '负债',
                    'is_group': 1
                }, 'name')
            })
            temp_doc.flags.ignore_permissions = True
            temp_doc.insert()
            temp_account = temp_doc.name
            print(f"  ✓ 创建临时科目: {temp_account}")

        # 添加调整分录
        adjustment_entry = {
            'account': temp_account,
            'debit_in_account_currency': 0 if difference > 0 else abs(difference),
            'credit_in_account_currency': difference if difference > 0 else 0,
        }
        accounts_list.append(adjustment_entry)
        print(f"  ✓ 添加调整分录: {'贷方' if difference > 0 else '借方'} {abs(difference):,.2f}")

    # 创建 Opening Entry
    try:
        je = frappe.get_doc({
            'doctype': 'Journal Entry',
            'company': company,
            'posting_date': '2025-01-01',  # 会计年度开始日期
            'voucher_type': 'Opening Entry',
            'is_opening': 'Yes',
            'accounts': accounts_list
        })

        je.flags.ignore_permissions = True
        je.insert()

        print(f"\n✓ 凭证创建成功: {je.name}")
        print(f"  借方总额: {je.total_debit:,.2f}")
        print(f"  贷方总额: {je.total_credit:,.2f}")

        # 提交凭证
        je.submit()
        print(f"✓ 凭证已提交")

        frappe.db.commit()

    except Exception as e:
        print(f"\n✗ 创建凭证失败: {str(e)}")
        frappe.db.rollback()
        return

    print("\n" + "=" * 60)
    print("期初余额导入完成")
    print("=" * 60)
