#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制删除所有科目并重新导入
"""
import frappe
import csv

def force_reimport_accounts():
    """强制删除所有科目并重新导入"""
    company = '大庆市华烁油气开采技术服务有限公司'
    csv_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/科目表_ERPNext格式_EN.csv'

    print("=" * 60)
    print("强制删除所有科目...")
    print("=" * 60)

    # 先清除公司的默认科目设置
    company_doc = frappe.get_doc('Company', company)
    default_account_fields = [
        'default_bank_account', 'default_cash_account', 'default_receivable_account',
        'default_payable_account', 'default_expense_account', 'default_income_account',
        'stock_received_but_not_billed', 'stock_adjustment_account', 'expenses_included_in_valuation',
        'default_inventory_account', 'cost_center', 'round_off_account',
        'write_off_account', 'exchange_gain_loss_account', 'unrealized_exchange_gain_loss_account',
        'accumulated_depreciation_account', 'depreciation_expense_account',
        'disposal_account', 'default_discount_account'
    ]

    print("清除公司默认科目设置...")
    for field in default_account_fields:
        if hasattr(company_doc, field):
            setattr(company_doc, field, None)

    company_doc.save()
    frappe.db.commit()
    print("  完成\n")

    # 获取所有科目并强制删除
    accounts = frappe.db.get_all('Account',
        filters={'company': company},
        fields=['name'],
        order_by='lft desc')

    print(f"找到 {len(accounts)} 个科目")
    deleted = 0

    for acc in accounts:
        try:
            # 直接从数据库删除，绕过验证
            frappe.db.sql("DELETE FROM `tabAccount` WHERE name = %s", acc.name)
            deleted += 1
            if deleted % 50 == 0:
                print(f"  已删除 {deleted} 个科目...")
        except Exception as e:
            print(f"  删除失败: {acc.name} - {str(e)}")

    frappe.db.commit()
    print(f"\n删除完成：成功删除 {deleted} 个科目\n")

    print("=" * 60)
    print("开始导入新的科目表...")
    print("=" * 60)

    # 读取 CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"共读取 {len(rows)} 条科目数据\n")

    # 分离根科目和子科目
    root_accounts = [r for r in rows if not r['Parent Account']]
    child_accounts = [r for r in rows if r['Parent Account']]

    created = 0
    errors = []
    parent_mapping = {}

    # 创建根科目
    print("创建根科目...")
    for row in root_accounts:
        try:
            account_name = row['Account Name']
            root_type = row['Root Type']
            account_number = row['Account Number'] if row['Account Number'] else None

            doc = frappe.get_doc({
                'doctype': 'Account',
                'account_name': account_name,
                'company': company,
                'root_type': root_type,
                'is_group': 1,
                'account_number': account_number,
            })
            doc.insert()
            parent_mapping[account_name] = doc.name
            created += 1
            print(f"  ✓ {account_name} ({root_type})")

        except Exception as e:
            errors.append(f"根科目 {row['Account Name']}: {str(e)}")
            print(f"  ✗ {row['Account Name']} - {str(e)}")

    frappe.db.commit()

    # 创建子科目
    print(f"\n创建子科目...")
    max_iterations = 25
    remaining = child_accounts[:]

    for iteration in range(max_iterations):
        if not remaining:
            break

        print(f"\n第 {iteration + 1} 轮，剩余 {len(remaining)} 个")
        next_round = []
        round_created = 0

        for row in remaining:
            try:
                account_name = row['Account Name']
                parent_account_name = row['Parent Account']

                # 查找父科目
                parent_full_name = parent_mapping.get(parent_account_name)

                if not parent_full_name:
                    next_round.append(row)
                    continue

                # 确保父科目是组
                parent_doc = frappe.get_doc('Account', parent_full_name)
                if not parent_doc.is_group:
                    parent_doc.is_group = 1
                    if parent_doc.account_type:
                        parent_doc.account_type = None
                    parent_doc.save()

                # 创建科目
                is_group = int(row['Is Group']) if row['Is Group'] else 0
                account_type = row['Account Type'] if row['Account Type'] else None
                account_number = row['Account Number'] if row['Account Number'] else None

                if is_group and account_type:
                    account_type = None

                doc = frappe.get_doc({
                    'doctype': 'Account',
                    'account_name': account_name,
                    'parent_account': parent_full_name,
                    'company': company,
                    'is_group': is_group,
                    'account_number': account_number,
                    'account_type': account_type,
                    'account_currency': row['Account Currency'] if row['Account Currency'] else None,
                })
                doc.insert()

                parent_mapping[account_name] = doc.name
                created += 1
                round_created += 1

                if round_created <= 10 or round_created % 100 == 0:
                    print(f"  ✓ {account_name}")

            except Exception as e:
                error_msg = str(e)
                if 'already used' not in error_msg or iteration == 0:
                    errors.append(f"{row['Account Name']}: {error_msg}")
                    if len(errors) <= 15:
                        print(f"  ✗ {row['Account Name']} - {error_msg}")

        remaining = next_round
        frappe.db.commit()

        if round_created > 0:
            print(f"  本轮创建: {round_created} 个")

        if iteration >= 3 and round_created == 0:
            break

    # 输出结果
    print("\n" + "=" * 60)
    print("导入完成！")
    print("=" * 60)
    print(f"✓ 成功创建: {created} 个科目")
    print(f"✗ 失败: {len(errors)} 个")

    if errors and len(errors) <= 20:
        print(f"\n失败详情：")
        for err in errors[:20]:
            print(f"  - {err}")

    if remaining:
        print(f"\n⚠ 未创建: {len(remaining)} 个科目")
        for r in remaining[:10]:
            print(f"  - {r['Account Name']} (父: {r['Parent Account']})")

    final_count = len(frappe.db.get_all('Account', filters={'company': company}))
    print(f"\n最终科目总数: {final_count}")
