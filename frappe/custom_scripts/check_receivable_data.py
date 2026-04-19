#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询应收账款数据
"""
import frappe

def check_receivable_data():
    """查询应收账款数据"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("应收账款数据查询")
    print("=" * 60)

    # 查询应收账款的 GL Entry
    gl_entries = frappe.db.sql('''
        SELECT
            posting_date,
            account,
            party_type,
            party,
            voucher_type,
            voucher_no,
            debit,
            credit,
            debit - credit as balance
        FROM `tabGL Entry`
        WHERE company = %s
        AND account IN (
            SELECT name FROM `tabAccount`
            WHERE company = %s AND account_type = 'Receivable'
        )
        ORDER BY posting_date, creation
    ''', (company, company), as_dict=True)

    print(f'\n共 {len(gl_entries)} 条应收账款记录\n')

    for gl in gl_entries:
        print(f'日期: {gl.posting_date}')
        print(f'科目: {gl.account}')
        print(f'客户: {gl.party}')
        print(f'凭证: {gl.voucher_type} - {gl.voucher_no}')
        print(f'借方: {gl.debit:,.2f}, 贷方: {gl.credit:,.2f}, 余额: {gl.balance:,.2f}')
        print('-' * 60)

    # 汇总
    total_debit = sum(gl.debit for gl in gl_entries)
    total_credit = sum(gl.credit for gl in gl_entries)

    print(f'\n汇总:')
    print(f'借方总额: {total_debit:,.2f}')
    print(f'贷方总额: {total_credit:,.2f}')
    print(f'应收余额: {total_debit - total_credit:,.2f}')

    print("\n" + "=" * 60)
