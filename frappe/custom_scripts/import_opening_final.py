#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性导入所有期初余额（单个凭证）
"""
import json
import frappe

def import_opening():
    """一次性导入所有期初余额"""

    company = '大庆市华烁油气开采技术服务有限公司'
    json_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/期初余额.json'

    print("=" * 60)
    print("开始导入期初余额（单个凭证）")
    print("=" * 60)

    # 读取 JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f'\n读取到 {len(data)} 条记录')

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

    for item in data:
        code = item['account_code']
        direction = item['direction']
        balance = item['balance']

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

        # 检查是否为组科目
        is_group = frappe.db.get_value('Account', account, 'is_group')
        if is_group:
            print(f'  ⚠ 跳过：组科目 {account}')
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

        # 处理往来科目 - 从科目名称提取往来方
        if account_type == 'Receivable':
            # 应收账款，往来方是客户
            party_name = item['account_name']
            if party_name and party_name != '应收账款':
                entry['party_type'] = 'Customer'
                entry['party'] = party_name
                customers_to_create.add(party_name)
        elif account_type == 'Payable':
            # 应付账款，往来方是供应商
            party_name = item['account_name']
            if party_name and party_name != '应付账款':
                entry['party_type'] = 'Supplier'
                entry['party'] = party_name
                suppliers_to_create.add(party_name)

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
                'customer_group': 'Commercial',
                'territory': 'China'
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
                'supplier_group': 'All Supplier Groups',
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

    # 如果不平衡，添加调整分录
    if abs(total_debit - total_credit) > 0.01:
        print('\n  ⚠ 检测到借贷不平衡，添加调整分录')

        # 查找本年利润科目
        profit_account = frappe.db.get_value('Account', {
            'company': company,
            'account_name': '本年利润'
        }, 'name')

        if not profit_account:
            print('  ✗ 错误：找不到本年利润科目')
            frappe.db.rollback()
            return

        difference = total_debit - total_credit

        if difference > 0:
            # 借方大于贷方，在贷方添加差额
            adjustment_entry = {
                'account': profit_account,
                'account_type': None,
                'debit': 0,
                'credit': difference,
                'party_type': None,
                'party': None
            }
            print(f'  ✓ 添加调整分录: {profit_account} 贷方 {difference:,.2f}')
        else:
            # 贷方大于借方，在借方添加差额
            adjustment_entry = {
                'account': profit_account,
                'account_type': None,
                'debit': abs(difference),
                'credit': 0,
                'party_type': None,
                'party': None
            }
            print(f'  ✓ 添加调整分录: {profit_account} 借方 {abs(difference):,.2f}')

        entries.append(adjustment_entry)

        # 重新计算总额
        total_debit = sum(e['debit'] for e in entries)
        total_credit = sum(e['credit'] for e in entries)
        print(f'  调整后借方: {total_debit:,.2f}')
        print(f'  调整后贷方: {total_credit:,.2f}')

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
