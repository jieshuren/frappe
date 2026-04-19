#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找调整科目
"""
import frappe

def check_adjustment():
    """查找调整科目"""
    company = '大庆市华烁油气开采技术服务有限公司'

    # 查找本年利润科目
    profit_account = frappe.db.get_value('Account', {
        'company': company,
        'account_number': '4103'
    }, 'name')

    if profit_account:
        print(f'找到本年利润科目: {profit_account}')
    else:
        print('未找到 4103 - 本年利润科目')

        # 查找其他权益类科目
        equity_accounts = frappe.db.sql('''
            SELECT name, account_name, account_number
            FROM `tabAccount`
            WHERE company = %s AND root_type = 'Equity'
            ORDER BY account_number
        ''', company, as_dict=True)

        print('\n所有权益类科目:')
        for acc in equity_accounts:
            print(f'  {acc.name}')
