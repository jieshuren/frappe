#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整导入科目期初余额（包含应收应付和库存明细）
"""
import frappe
import json

def create_party_if_needed(account_name, account_type):
    """为应收应付科目创建对应的客户/供应商"""
    company = '大庆市华烁油气开采技术服务有限公司'

    if account_type == 'Receivable':
        # 创建客户
        if not frappe.db.exists('Customer', account_name):
            customer = frappe.get_doc({
                'doctype': 'Customer',
                'customer_name': account_name,
                'customer_type': 'Company',
                'customer_group': 'Commercial',
                'territory': 'China'
            })
            customer.flags.ignore_permissions = True
            customer.flags.ignore_mandatory = True
            customer.insert()
            return 'Customer', customer.name
        return 'Customer', account_name

    elif account_type == 'Payable':
        # 创建供应商
        if not frappe.db.exists('Supplier', account_name):
            supplier = frappe.get_doc({
                'doctype': 'Supplier',
                'supplier_name': account_name,
                'supplier_group': 'All Supplier Groups',
                'supplier_type': 'Company'
            })
            supplier.flags.ignore_permissions = True
            supplier.flags.ignore_mandatory = True
            supplier.insert()
            return 'Supplier', supplier.name
        return 'Supplier', account_name

    return None, None

def import_opening_complete():
    """完整导入期初余额"""
    company = '大庆市华烁油气开采技术服务有限公司'
    json_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/期初余额.json'

    print("=" * 60)
    print("完整导入科目期初余额")
    print("=" * 60)

    # 读取 JSON 文件
    with open(json_file, 'r', encoding='utf-8') as f:
        opening_data = json.load(f)

    print(f"\n读取到 {len(opening_data)} 条期初数据")

    # 准备凭证分录
    accounts_list = []
    skipped = []
    party_created = []

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
            account_info = frappe.db.get_value('Account', {
                'company': company,
                'account_name': account_name
            }, ['name', 'account_type', 'is_group'], as_dict=True)

        if not account_info:
            skipped.append(f"{account_code} {account_name} (未找到)")
            continue

        # 跳过组科目
        if account_info.is_group:
            continue

        # 跳过库存科目（ERPNext 强制要求通过库存交易）
        if account_info.account_type == 'Stock':
            skipped.append(f"{account_code} {account_name} (库存科目)")
            continue

        # 准备分录
        entry = {
            'account': account_info.name,
            'debit_in_account_currency': balance if direction == '借' else 0,
            'credit_in_account_currency': balance if direction == '贷' else 0,
        }

        # 处理应收应付科目
        if account_info.account_type in ['Receivable', 'Payable']:
            party_type, party = create_party_if_needed(account_name, account_info.account_type)
            if party_type and party:
                entry['party_type'] = party_type
                entry['party'] = party
                party_created.append(f"{party_type}: {party}")
            else:
                skipped.append(f"{account_code} {account_name} (无法创建往来单位)")
                continue

        accounts_list.append(entry)

    if party_created:
        print(f"\n✓ 创建了 {len(set(party_created))} 个往来单位")

    if skipped:
        print(f"\n⚠️  跳过 {len(skipped)} 个科目：")
        for item in skipped[:10]:
            print(f"  - {item}")
        if len(skipped) > 10:
            print(f"  ... 还有 {len(skipped) - 10} 个")

    print(f"\n准备创建凭证，包含 {len(accounts_list)} 个分录")

    # 计算借贷差额
    total_debit = sum(e['debit_in_account_currency'] for e in accounts_list)
    total_credit = sum(e['credit_in_account_currency'] for e in accounts_list)
    difference = total_debit - total_credit

    print(f"  借方合计: {total_debit:,.2f}")
    print(f"  贷方合计: {total_credit:,.2f}")
    print(f"  差额: {difference:,.2f}")

    # 如果有差额，添加调整分录
    if abs(difference) > 0.01:
        print(f"\n⚠️  借贷不平衡，添加调整科目")

        temp_account = frappe.db.get_value('Account', {
            'company': company,
            'account_name': '期初余额调整'
        }, 'name')

        if not temp_account:
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

        adjustment_entry = {
            'account': temp_account,
            'debit_in_account_currency': 0 if difference > 0 else abs(difference),
            'credit_in_account_currency': difference if difference > 0 else 0,
        }
        accounts_list.append(adjustment_entry)

    # 创建 Opening Entry
    try:
        je = frappe.get_doc({
            'doctype': 'Journal Entry',
            'company': company,
            'posting_date': '2025-01-01',
            'voucher_type': 'Opening Entry',
            'is_opening': 'Yes',
            'accounts': accounts_list
        })

        je.flags.ignore_permissions = True
        je.insert()

        print(f"\n✓ 凭证创建成功: {je.name}")
        print(f"  借方总额: {je.total_debit:,.2f}")
        print(f"  贷方总额: {je.total_credit:,.2f}")

        je.submit()
        print(f"✓ 凭证已提交")

        frappe.db.commit()

    except Exception as e:
        print(f"\n✗ 失败: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()
        return

    print("\n" + "=" * 60)
    print("期初余额导入完成")
    print("=" * 60)
