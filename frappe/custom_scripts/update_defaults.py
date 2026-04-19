#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新默认科目为正确类型的科目
"""
import frappe

def update_default_accounts():
    """更新默认科目"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("更新默认科目配置")
    print("=" * 60)

    # 更新默认应收账款
    receivable = frappe.db.get_value('Account', {
        'company': company,
        'account_type': 'Receivable'
    }, 'name')

    if receivable:
        frappe.db.sql('UPDATE `tabCompany` SET default_receivable_account = %s WHERE name = %s',
                      (receivable, company))
        print(f'✓ 默认应收账款: {receivable}')

    # 更新默认库存账户（选择一个 Stock 类型的）
    stock_accounts = frappe.db.get_all('Account', {
        'company': company,
        'account_type': 'Stock'
    }, ['name', 'account_name'], limit=5)

    if stock_accounts:
        # 优先选择包含"库存商品"的
        stock = None
        for acc in stock_accounts:
            if '库存商品' in acc.account_name or '原材料' in acc.account_name:
                stock = acc.name
                break

        if not stock:
            stock = stock_accounts[0].name

        frappe.db.sql('UPDATE `tabCompany` SET default_inventory_account = %s WHERE name = %s',
                      (stock, company))
        print(f'✓ 默认库存账户: {stock}')

    frappe.db.commit()

    print("\n配置更新完成")
    print("=" * 60)
