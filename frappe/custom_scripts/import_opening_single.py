#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性导入所有期初余额（单个凭证）
"""
import frappe
import pandas as pd
from datetime import datetime

def import_opening_single():
    """一次性导入所有期初余额"""
    company = '大庆市华烁油气开采技术服务有限公司'
    excel_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/科目期初.xlsx'

    print("=" * 60)
    print("开始导入期初余额（单个凭证）")
    print("=" * 60)

    # 读取 Excel
    df = pd.read_excel(excel_file)
    print(f'\n读取到 {len(df)} 条记录')

    # 1. 临时清除 Stock 账户类型
    print('\n第一步：临时清除 Stock 账户类型')
    stock_accounts = frappe.db.sql("""
        SELECT name FROM `tabAccount`
        WHERE company = %s AND account_type = 'Stock'
    """, company, as_dict=True)

    for acc in stock_accounts:
        frappe.db.sql("UPDATE `tabAccount` SET account_type = NULL WHERE name = %s", acc.name)
        print(f'  清除: {acc.name}')

    frappe.db.commit()

    # 2. 准备数据
    print('\n第二步：准备导入数据')
    entries = []
    customers_to_create = set()
    suppliers_to_create = set()

    for idx, row in df.iterrows():
        code = str(row['科目编码']).strip()
        account_name = str(row['科目名称']).strip()
        supplier = row.get('供应商')
        customer = row.get('客户')
        direction = str(row['方向']).strip()
        balance = float(row['期初余额本位币'])

        if balance == 0:
            continue

        # 查找科目
        account = frappe.db.get_value('Account', {
            'company': company,
            'account_number': code
        }, 'name')

        if not account:
            print(f'  ⚠ 跳过：找不到科目 {code}')
            continue

        # 获取科目类型
        account_type = frappe.db.get_value('Account', account, 'account_type')

        # 处理负数余额
        if balance < 0:
            actual_direction = '贷' if direction == '借' else '借'
            actual_balance = abs(balance)
        else:
            actual_direction = direction
            actual_balance = balance

        # 准备分录
        entry = {
            'account': account,
            'account_type': account_type,
            'debit': actual_balance if actual_direction == '借' else 0,
            'credit': actual_balance if actual_direction == '贷' else 0,
            'party_type': None,
            'party': None
        }

        # 处理往来科目
        if account_type == 'Receivable' and pd.notna(customer):
            entry['party_type'] = 'Customer'
            entry['party'] = customer
            customers_to_create.add(customer)
        elif account_type == 'Payable' and pd.notna(supplier):
            entry['party_type'] = 'Supplier'
            entry['party'] = supplier
            suppliers_to_create.add(supplier)

        entries.append(entry)

    print(f'  准备了 {len(entries)} 条分录')
    print(f'  需要创建 {len(customers_to_create)} 个客户')
    print(f'  需要创建 {len(suppliers_to_create)} 个供应商')

    # 3. 创建客户
    print('\n第三步：创建客户')
    for customer_name in customers_to_create:
        if not frappe.db.exists('Customer', customer_name):
            customer = frappe.get_doc({
                'doctype': 'Customer',
                'customer_name': customer_name,
                'customer_type': 'Company',
                'customer_group': '商业',
                'territory': '中国'
            })
            customer.insert(ignore_permissions=True)
            print(f'  ✓ {customer_name}')

    # 4. 创建供应商
    print('\n第四步：创建供应商')
    for supplier_name in suppliers_to_create:
        if not frappe.db.exists('Supplier', supplier_name):
            supplier = frappe.get_doc({
                'doctype': 'Supplier',
                'supplier_name': supplier_name,
                'supplier_group': '所有供应商组',
                'supplier_type': 'Company'
            })
            supplier.insert(ignore_permissions=True)
            print(f'  ✓ {supplier_name}')

    frappe.db.commit()

    # 5. 创建单个凭证
    print('\n第五步：创建期初凭证')

    # 计算总额
    total_debit = sum(e['debit'] for e in entries)
    total_credit = sum(e['credit'] for e in entries)

    print(f'  借方总额: {total_debit:,.2f}')
    print(f'  贷方总额: {total_credit:,.2f}')
    print(f'  差额: {abs(total_debit - total_credit):,.2f}')

    if abs(total_debit - total_credit) > 0.01:
        print('\n  ⚠ 警告：借贷不平衡！')
        return

    # 创建凭证
    je = frappe.get_doc({
        'doctype': 'Journal Entry',
        'company': company,
        'posting_date': '2025-01-01',
        'voucher_type': 'Opening Entry',
        'is_opening': 'Yes',
        'user_remark': '期初余额导入',
        'accounts': []
    })

    for entry in entries:
        je.append('accounts', {
            'account': entry['account'],
            'debit_in_account_currency': entry['debit'],
            'credit_in_account_currency': entry['credit'],
            'party_type': entry['party_type'],
            'party': entry['party']
        })

    je.insert(ignore_permissions=True)
    je.submit()

    print(f'  ✓ 创建凭证: {je.name}')
    print(f'  ✓ 包含 {len(entries)} 条分录')

    # 6. 恢复 Stock 账户类型
    print('\n第六步：恢复 Stock 账户类型')
    for acc in stock_accounts:
        frappe.db.sql("UPDATE `tabAccount` SET account_type = 'Stock' WHERE name = %s", acc.name)
        print(f'  恢复: {acc.name}')

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("导入完成！")
    print(f"凭证号: {je.name}")
    print(f"借方总额: {total_debit:,.2f}")
    print(f"贷方总额: {total_credit:,.2f}")
    print("=" * 60)
