#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置公司默认科目
"""
import frappe

def setup_default_accounts():
    """配置公司默认科目"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("配置公司默认科目")
    print("=" * 60)

    # 查找合适的科目
    def find_account(account_name=None, account_type=None, root_type=None):
        """查找科目"""
        filters = {'company': company}
        if account_name:
            filters['account_name'] = account_name
        if account_type:
            filters['account_type'] = account_type
        if root_type:
            filters['root_type'] = root_type

        result = frappe.db.get_value('Account', filters, 'name')
        return result

    # 定义默认科目映射
    default_accounts = {
        'default_cash_account': ('库存现金', 'Cash', 'Asset'),
        'default_bank_account': ('银行存款', 'Bank', 'Asset'),
        'default_receivable_account': ('应收账款', 'Receivable', 'Asset'),
        'default_payable_account': ('应付账款', 'Payable', 'Liability'),
        'default_expense_account': ('管理费用', None, 'Expense'),
        'default_income_account': ('主营业务收入', None, 'Income'),
        'round_off_account': ('财务费用', None, 'Expense'),
        'write_off_account': ('营业外支出', None, 'Expense'),
        'exchange_gain_loss_account': ('财务费用', None, 'Expense'),
        'default_inventory_account': ('库存商品', None, 'Asset'),
        'stock_adjustment_account': ('主营业务成本', None, 'Expense'),
        'stock_received_but_not_billed': ('应付账款', 'Payable', 'Liability'),
        'expenses_included_in_valuation': ('主营业务成本', None, 'Expense'),
        'default_payroll_payable_account': ('应付职工薪酬', None, 'Liability'),
        'accumulated_depreciation_account': ('累计折旧', None, 'Asset'),
        'depreciation_expense_account': ('管理费用', None, 'Expense'),
    }

    # 使用 SQL 直接更新，避免验证问题
    updates = []

    for field, (account_name, account_type, root_type) in default_accounts.items():
        # 查找科目
        account = None

        # 先按名称查找
        account = find_account(account_name=account_name)

        # 如果没找到且有 account_type，按类型查找
        if not account and account_type:
            account = find_account(account_type=account_type, root_type=root_type)

        if account:
            updates.append((field, account))
            print(f"✓ {field}: {account}")
        else:
            print(f"✗ {field}: 未找到合适的科目 ({account_name})")

    # 批量更新
    print(f"\n开始更新公司配置...")
    for field, account in updates:
        try:
            frappe.db.sql(f"UPDATE `tabCompany` SET `{field}` = %s WHERE name = %s",
                         (account, company))
        except Exception as e:
            print(f"  更新 {field} 失败: {str(e)}")

    frappe.db.commit()

    print(f"\n配置完成！已设置 {len(updates)} 个默认科目")
    print("=" * 60)
