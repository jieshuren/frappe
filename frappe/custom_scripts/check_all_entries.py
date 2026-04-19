#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有凭证和GL Entry
"""
import frappe

def check_all_entries():
    """检查所有凭证"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("检查所有凭证和GL Entry")
    print("=" * 60)

    # 检查所有期初凭证
    print('\n所有期初凭证:')
    je_list = frappe.db.sql('''
        SELECT name, posting_date, docstatus, total_debit, total_credit
        FROM `tabJournal Entry`
        WHERE company = %s AND is_opening = 'Yes'
        ORDER BY creation
    ''', company, as_dict=True)

    for je in je_list:
        status = '已提交' if je.docstatus == 1 else '草稿' if je.docstatus == 0 else '已取消'
        print(f'{je.name} - {je.posting_date} - {status} - 借:{je.total_debit:,.2f}')

    print(f'\n共 {len(je_list)} 个期初凭证')

    # 检查所有应收账款 GL Entry（包括已取消的）
    print('\n所有应收账款相关 GL Entry:')
    all_gl = frappe.db.sql('''
        SELECT
            posting_date,
            account,
            party,
            voucher_no,
            debit,
            credit,
            is_cancelled
        FROM `tabGL Entry`
        WHERE company = %s
        AND (account LIKE '%%应收%%' OR account LIKE '%%112201%%')
        ORDER BY creation
    ''', company, as_dict=True)

    for gl in all_gl:
        cancelled = ' (已取消)' if gl.is_cancelled else ''
        print(f'{gl.voucher_no}{cancelled} - {gl.party} - 借:{gl.debit:,.2f} 贷:{gl.credit:,.2f}')

    print(f'\n共 {len(all_gl)} 条 GL Entry')

    # 统计未取消的
    active_gl = [gl for gl in all_gl if not gl.is_cancelled]
    print(f'未取消的: {len(active_gl)} 条')

    print("\n" + "=" * 60)
