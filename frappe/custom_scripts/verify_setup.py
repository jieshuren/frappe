#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import frappe

def verify_company_setup():
    """验证公司配置"""
    company = '大庆市华烁油气开采技术服务有限公司'

    company_doc = frappe.get_doc('Company', company)

    print("=" * 60)
    print("公司默认科目配置验证")
    print("=" * 60)

    fields = [
        ('默认现金账户', 'default_cash_account'),
        ('默认银行账户', 'default_bank_account'),
        ('默认应收账款', 'default_receivable_account'),
        ('默认应付账款', 'default_payable_account'),
        ('默认费用账户', 'default_expense_account'),
        ('默认收入账户', 'default_income_account'),
        ('默认库存账户', 'default_inventory_account'),
        ('库存调整账户', 'stock_adjustment_account'),
        ('默认工资应付账户', 'default_payroll_payable_account'),
        ('累计折旧账户', 'accumulated_depreciation_account'),
    ]

    for label, field in fields:
        value = getattr(company_doc, field, None)
        if value:
            print(f"✓ {label}: {value}")
        else:
            print(f"✗ {label}: 未设置")

    print("\n" + "=" * 60)
    print("✓ 配置验证完成！")
    print("=" * 60)
