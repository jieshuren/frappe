#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科目表导入脚本 v2
需要在 bench 环境中运行: bench --site aierp.local execute frappe.custom_scripts.import_accounts_v2.import_chart_of_accounts
"""
import frappe
import csv

def import_chart_of_accounts():
    """导入科目表"""
    company = '大庆市华烁油气开采技术服务有限公司'
    csv_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/科目表_ERPNext格式_EN.csv'

    # 根科目映射（CSV中的名称 -> ERPNext中可能已存在的名称）
    root_type_to_existing = {}

    # 查找已存在的根科目
    existing_roots = frappe.db.get_all('Account',
        filters={'company': company, 'parent_account': ['is', 'not set']},
        fields=['name', 'account_name', 'root_type'])

    for root in existing_roots:
        root_type_to_existing[root.root_type] = root.name
        print(f"已存在根科目: {root.account_name} ({root.root_type}) -> {root.name}")

    # 读取 CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\n共读取 {len(rows)} 条科目数据")

    # 按层级排序
    root_accounts = [r for r in rows if not r['Parent Account']]
    child_accounts = [r for r in rows if r['Parent Account']]

    print(f"根科目: {len(root_accounts)} 个")
    print(f"子科目: {len(child_accounts)} 个\n")

    created = 0
    skipped = 0
    errors = []

    # 处理根科目（跳过已存在的）
    for row in root_accounts:
        root_type = row['Root Type']
        if root_type in root_type_to_existing:
            print(f"跳过已存在的根科目: {row['Account Name']} ({root_type})")
            skipped += 1
        else:
            print(f"警告: 根科目 {row['Account Name']} ({root_type}) 不存在，需要手动创建")

    frappe.db.commit()

    # 创建子科目（多轮迭代）
    max_iterations = 15
    remaining = child_accounts[:]

    for iteration in range(max_iterations):
        if not remaining:
            break

        print(f"\n第 {iteration + 1} 轮创建子科目，剩余 {len(remaining)} 个")
        next_round = []
        round_created = 0

        for row in remaining:
            try:
                account_name = row['Account Name']
                parent_account_name = row['Parent Account']

                # 检查是否已存在
                exists = frappe.db.exists('Account', {
                    'account_name': account_name,
                    'company': company
                })

                if exists:
                    skipped += 1
                    continue

                # 查找父科目（可能是根科目或子科目）
                parent_full_name = None

                # 先检查是否是根科目
                for root_type, root_name in root_type_to_existing.items():
                    root_acc = frappe.get_doc('Account', root_name)
                    if root_acc.account_name == parent_account_name:
                        parent_full_name = root_name
                        break

                # 如果不是根科目，查找子科目
                if not parent_full_name:
                    parent_full_name = frappe.db.get_value('Account', {
                        'account_name': parent_account_name,
                        'company': company
                    }, 'name')

                if not parent_full_name:
                    # 父科目还不存在，留到下一轮
                    next_round.append(row)
                    continue

                # 检查父科目是否是组（is_group）
                parent_is_group = frappe.db.get_value('Account', parent_full_name, 'is_group')
                if not parent_is_group:
                    # 需要将父科目转换为组
                    parent_doc = frappe.get_doc('Account', parent_full_name)
                    parent_doc.is_group = 1
                    parent_doc.save()
                    print(f"  将 {parent_account_name} 转换为组科目")

                # 创建科目
                is_group = int(row['Is Group']) if row['Is Group'] else 0
                account_type = row['Account Type'] if row['Account Type'] else None

                # 如果是组科目，不能设置 account_type
                if is_group and account_type:
                    account_type = None

                doc = frappe.get_doc({
                    'doctype': 'Account',
                    'account_name': account_name,
                    'parent_account': parent_full_name,
                    'company': company,
                    'is_group': is_group,
                    'account_number': row['Account Number'] if row['Account Number'] else None,
                    'account_type': account_type,
                    'account_currency': row['Account Currency'] if row['Account Currency'] else None,
                })
                doc.insert()
                created += 1
                round_created += 1
                if round_created <= 5 or round_created % 20 == 0:
                    print(f"  创建: {account_name} (父: {parent_account_name})")

            except Exception as e:
                error_msg = str(e)
                # 只记录非重复的错误
                if 'already used' not in error_msg or iteration == 0:
                    errors.append(f"{row['Account Name']}: {error_msg}")
                    if len(errors) <= 10:
                        print(f"  错误: {row['Account Name']} - {error_msg}")

        remaining = next_round
        frappe.db.commit()

        if round_created > 0:
            print(f"  本轮创建了 {round_created} 个科目")

    # 输出结果
    print(f"\n{'='*60}")
    print(f"导入完成！")
    print(f"成功创建: {created} 个科目")
    print(f"跳过已存在: {skipped} 个科目")
    print(f"失败: {len(errors)} 个科目")

    if errors and len(errors) <= 20:
        print(f"\n错误详情：")
        for err in errors:
            print(f"  - {err}")

    if remaining:
        print(f"\n警告: 还有 {len(remaining)} 个科目未能创建")
        if len(remaining) <= 10:
            for r in remaining:
                print(f"  - {r['Account Name']} (父: {r['Parent Account']})")
