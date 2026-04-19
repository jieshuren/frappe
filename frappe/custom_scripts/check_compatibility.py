#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查科目表与 ERPNext 功能的兼容性
"""
import frappe

def check_account_compatibility():
    """检查科目表兼容性"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("科目表兼容性检查")
    print("=" * 60)

    # ERPNext 需要的关键 Account Type
    required_account_types = {
        'Bank': '银行账户（用于银行对账、支付等）',
        'Cash': '现金账户（用于现金交易）',
        'Receivable': '应收账款（用于客户欠款）',
        'Payable': '应付账款（用于供应商欠款）',
        'Stock': '库存账户（用于库存估值）',
        'Tax': '税务账户（用于增值税等）',
        'Fixed Asset': '固定资产（用于资产管理）',
        'Accumulated Depreciation': '累计折旧（用于折旧计算）',
    }

    print("\n1. 检查关键账户类型：")
    for account_type, description in required_account_types.items():
        count = frappe.db.count('Account', {
            'company': company,
            'account_type': account_type
        })
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {account_type}: {count} 个 - {description}")

    # 检查是否有足够的明细科目
    print("\n2. 检查科目结构：")

    total = frappe.db.count('Account', {'company': company})
    groups = frappe.db.count('Account', {'company': company, 'is_group': 1})
    ledgers = total - groups

    print(f"  总科目数: {total}")
    print(f"  组科目: {groups}")
    print(f"  明细科目: {ledgers}")

    # 检查各类业务需要的科目
    print("\n3. 检查业务功能所需科目：")

    business_accounts = {
        '销售业务': [
            ('应收账款', 'Receivable'),
            ('主营业务收入', None),
            ('销项税额', 'Tax'),
        ],
        '采购业务': [
            ('应付账款', 'Payable'),
            ('主营业务成本', None),
            ('进项税额', 'Tax'),
        ],
        '库存管理': [
            ('库存商品', 'Stock'),
            ('原材料', 'Stock'),
            ('库存调整', None),
        ],
        '工资管理': [
            ('应付职工薪酬', None),
            ('管理费用', None),
        ],
        '固定资产': [
            ('固定资产', 'Fixed Asset'),
            ('累计折旧', 'Accumulated Depreciation'),
        ],
    }

    for business, accounts in business_accounts.items():
        print(f"\n  {business}:")
        for account_name, account_type in accounts:
            filters = {'company': company, 'account_name': account_name}
            if account_type:
                filters['account_type'] = account_type

            exists = frappe.db.exists('Account', filters)
            status = "✓" if exists else "✗"
            print(f"    {status} {account_name}")

    # 检查可能缺失的科目
    print("\n4. 建议补充的科目：")

    suggestions = []

    # 检查是否有足够的银行账户
    bank_count = frappe.db.count('Account', {
        'company': company,
        'account_type': 'Bank'
    })
    if bank_count < 3:
        suggestions.append("建议：添加更多银行账户明细科目（目前只有 {} 个）".format(bank_count))

    # 检查税务科目
    tax_count = frappe.db.count('Account', {
        'company': company,
        'account_type': 'Tax'
    })
    if tax_count == 0:
        suggestions.append("⚠️  警告：缺少税务类型科目（Tax），增值税功能可能无法正常使用")

    # 检查库存科目
    stock_count = frappe.db.count('Account', {
        'company': company,
        'account_type': 'Stock'
    })
    if stock_count == 0:
        suggestions.append("⚠️  警告：缺少库存类型科目（Stock），库存管理功能可能无法正常使用")

    if suggestions:
        for suggestion in suggestions:
            print(f"  {suggestion}")
    else:
        print("  ✓ 科目表配置完整，无需补充")

    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)
