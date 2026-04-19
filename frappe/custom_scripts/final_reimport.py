#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版本：强制删除并重新导入中国会计科目表
"""
import frappe
import csv

def final_reimport_accounts():
    """强制删除所有科目并重新导入"""
    company = '大庆市华烁油气开采技术服务有限公司'
    csv_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/科目表_ERPNext格式_EN.csv'

    print("=" * 60)
    print("强制删除所有科目...")
    print("=" * 60)

    # 清除公司的默认科目设置 - 直接用 SQL 更新
    print("清除公司默认科目设置...")

    default_fields = [
        'default_bank_account', 'default_cash_account', 'default_receivable_account',
        'default_payable_account', 'default_expense_account', 'default_income_account',
        'stock_received_but_not_billed', 'stock_adjustment_account', 'expenses_included_in_valuation',
        'default_inventory_account', 'cost_center', 'round_off_account',
        'write_off_account', 'exchange_gain_loss_account', 'unrealized_exchange_gain_loss_account',
        'accumulated_depreciation_account', 'depreciation_expense_account',
        'disposal_account', 'default_discount_account', 'capital_work_in_progress_account',
        'asset_received_but_not_billed', 'default_employee_advance_account',
        'default_payroll_payable_account', 'service_expense_account', 'default_provisional_account'
    ]

    # 直接用 SQL 更新，跳过所有验证
    for field in default_fields:
        frappe.db.sql(f"UPDATE `tabCompany` SET `{field}` = NULL WHERE name = %s", company)

    frappe.db.commit()

    # 直接从数据库删除所有科目
    frappe.db.sql("DELETE FROM `tabAccount` WHERE company = %s", company)
    frappe.db.commit()
    print("  完成\n")

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

    # 创建根科目 - 不设置 parent_account
    print("创建根科目...")
    for row in root_accounts:
        try:
            account_name = row['Account Name']
            root_type = row['Root Type']
            account_number = row['Account Number'] if row['Account Number'] else None

            # 使用 insert 方法，不通过 get_doc
            account_dict = {
                'doctype': 'Account',
                'account_name': account_name,
                'company': company,
                'root_type': root_type,
                'is_group': 1,
            }

            if account_number:
                account_dict['account_number'] = account_number

            doc = frappe.get_doc(account_dict)

            # 设置 ignore_permissions 和 ignore_mandatory
            doc.flags.ignore_permissions = True
            doc.flags.ignore_mandatory = True
            doc.insert()

            parent_mapping[account_name] = doc.name
            created += 1
            print(f"  ✓ {account_name} ({root_type}) -> {doc.name}")

        except Exception as e:
            error_msg = str(e)
            errors.append(f"根科目 {row['Account Name']}: {error_msg}")
            print(f"  ✗ {row['Account Name']} - {error_msg}")

    frappe.db.commit()
    print(f"\n根科目创建完成: {len(parent_mapping)} 个\n")

    # 创建子科目
    print("创建子科目...")
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
                    parent_doc.flags.ignore_permissions = True
                    parent_doc.save()

                # 创建科目
                is_group = int(row['Is Group']) if row['Is Group'] else 0
                account_type = row['Account Type'] if row['Account Type'] else None
                account_number = row['Account Number'] if row['Account Number'] else None

                if is_group and account_type:
                    account_type = None

                account_dict = {
                    'doctype': 'Account',
                    'account_name': account_name,
                    'parent_account': parent_full_name,
                    'company': company,
                    'is_group': is_group,
                }

                if account_number:
                    account_dict['account_number'] = account_number
                if account_type:
                    account_dict['account_type'] = account_type
                if row['Account Currency']:
                    account_dict['account_currency'] = row['Account Currency']

                doc = frappe.get_doc(account_dict)
                doc.flags.ignore_permissions = True
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
