#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查应收应付账款数据
"""
import frappe

def check_receivable_payable():
    """检查应收应付数据"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("检查应收应付账款数据")
    print("=" * 60)

    # 检查应收账款科目
    print('\n应收账款科目:')
    receivable_accounts = frappe.db.get_all('Account', {
        'company': company,
        'account_type': 'Receivable'
    }, ['name', 'account_name', 'is_group', 'parent_account'])

    for acc in receivable_accounts:
        print(f'  {acc.name}')
        print(f'    名称: {acc.account_name}')
        print(f'    组科目: {acc.is_group}')
        print(f'    父科目: {acc.parent_account}')

    # 检查应付账款科目
    print('\n应付账款科目:')
    payable_accounts = frappe.db.get_all('Account', {
        'company': company,
        'account_type': 'Payable'
    }, ['name', 'account_name', 'is_group', 'parent_account'])

    for acc in payable_accounts:
        print(f'  {acc.name}')
        print(f'    名称: {acc.account_name}')
        print(f'    组科目: {acc.is_group}')
        print(f'    父科目: {acc.parent_account}')

    # 检查 GL Entry
    print('\n应收账款相关的 GL Entry:')
    receivable_gl = frappe.db.sql('''
        SELECT account, party_type, party, debit, credit
        FROM `tabGL Entry`
        WHERE company = %s AND account_type = 'Receivable'
        LIMIT 5
    ''', company, as_dict=True)

    if receivable_gl:
        for gl in receivable_gl:
            print(f'  科目: {gl.account}, {gl.party_type}: {gl.party}, 借: {gl.debit}, 贷: {gl.credit}')
    else:
        print('  无数据')

    print('\n应付账款相关的 GL Entry:')
    payable_gl = frappe.db.sql('''
        SELECT account, party_type, party, debit, credit
        FROM `tabGL Entry`
        WHERE company = %s AND account_type = 'Payable'
        LIMIT 5
    ''', company, as_dict=True)

    if payable_gl:
        for gl in payable_gl:
            print(f'  科目: {gl.account}, {gl.party_type}: {gl.party}, 借: {gl.debit}, 贷: {gl.credit}')
    else:
        print('  无数据')

    print("\n" + "=" * 60)
