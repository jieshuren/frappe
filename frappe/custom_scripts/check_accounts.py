#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查科目设置
"""
import frappe

def check_accounts():
    """检查科目设置"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("检查科目设置")
    print("=" * 60)

    # 1. 统计科目数量
    print("\n1. 科目统计:")
    total = frappe.db.count('Account', {'company': company})
    print(f"   总科目数: {total}")

    group_count = frappe.db.count('Account', {'company': company, 'is_group': 1})
    ledger_count = frappe.db.count('Account', {'company': company, 'is_group': 0})
    print(f"   组科目: {group_count}")
    print(f"   明细科目: {ledger_count}")

    # 2. 按 Root Type 统计
    print("\n2. 按 Root Type 统计:")
    for root_type in ['Asset', 'Liability', 'Equity', 'Income', 'Expense']:
        count = frappe.db.count('Account', {'company': company, 'root_type': root_type})
        print(f"   {root_type}: {count}")

    # 3. 按 Account Type 统计
    print("\n3. 按 Account Type 统计:")
    account_types = frappe.db.sql("""
        SELECT account_type, COUNT(*) as count
        FROM `tabAccount`
        WHERE company = %s AND account_type IS NOT NULL
        GROUP BY account_type
        ORDER BY count DESC
    """, company, as_dict=True)

    for at in account_types:
        print(f"   {at.account_type}: {at.count}")

    # 4. 检查公司默认科目
    print("\n4. 公司默认科目:")
    company_doc = frappe.get_doc('Company', company)
    default_fields = [
        'default_cash_account',
        'default_bank_account',
        'default_receivable_account',
        'default_payable_account',
        'default_expense_account',
        'default_income_account',
        'default_inventory_account',
        'cost_center',
    ]

    for field in default_fields:
        value = getattr(company_doc, field, None)
        status = '✓' if value else '✗'
        print(f"   {status} {field}: {value or '未设置'}")

    # 5. 检查期初余额
    print("\n5. 期初余额:")
    je_count = frappe.db.count('Journal Entry', {
        'company': company,
        'is_opening': 'Yes',
        'docstatus': 1
    })
    print(f"   期初凭证数: {je_count}")

    if je_count > 0:
        je = frappe.db.get_value('Journal Entry', {
            'company': company,
            'is_opening': 'Yes',
            'docstatus': 1
        }, ['name', 'total_debit', 'total_credit'], as_dict=True)

        print(f"   凭证号: {je.name}")
        print(f"   借方总额: {je.total_debit:,.2f}")
        print(f"   贷方总额: {je.total_credit:,.2f}")
        print(f"   平衡状态: {'✓ 平衡' if abs(je.total_debit - je.total_credit) < 0.01 else '✗ 不平衡'}")

    # 6. 检查往来单位
    print("\n6. 往来单位:")
    customer_count = frappe.db.count('Customer')
    supplier_count = frappe.db.count('Supplier')
    print(f"   客户数: {customer_count}")
    print(f"   供应商数: {supplier_count}")

    # 7. 检查可能的问题
    print("\n7. 潜在问题检查:")

    # 检查没有 account_type 的明细科目
    no_type = frappe.db.count('Account', {
        'company': company,
        'is_group': 0,
        'account_type': ['is', 'not set']
    })
    if no_type > 0:
        print(f"   ⚠️  {no_type} 个明细科目没有设置 account_type")
    else:
        print(f"   ✓ 所有明细科目都有 account_type")

    # 检查组科目是否有 account_type
    group_with_type = frappe.db.count('Account', {
        'company': company,
        'is_group': 1,
        'account_type': ['is', 'set']
    })
    if group_with_type > 0:
        print(f"   ⚠️  {group_with_type} 个组科目设置了 account_type（应该为空）")
    else:
        print(f"   ✓ 组科目没有设置 account_type")

    # 检查应收应付科目是否有往来单位
    receivable_accounts = frappe.db.get_all('Account', {
        'company': company,
        'account_type': 'Receivable',
        'is_group': 0
    }, ['name', 'account_name'])

    payable_accounts = frappe.db.get_all('Account', {
        'company': company,
        'account_type': 'Payable',
        'is_group': 0
    }, ['name', 'account_name'])

    print(f"   应收账款科目: {len(receivable_accounts)} 个")
    print(f"   应付账款科目: {len(payable_accounts)} 个")

    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)
