#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科目表导入脚本 v3 - 处理父科目名称映射
需要在 bench 环境中运行: bench --site aierp.local execute frappe.custom_scripts.import_accounts_v3.import_chart_of_accounts
"""
import frappe
import csv

def import_chart_of_accounts():
    """导入科目表"""
    company = '大庆市华烁油气开采技术服务有限公司'
    csv_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/科目表_ERPNext格式_EN.csv'

    # CSV中的父科目名称 -> 系统中实际的科目完整名称
    parent_name_mapping = {}

    # 查找已存在的根科目
    existing_roots = frappe.db.get_all('Account',
        filters={'company': company, 'parent_account': ['is', 'not set']},
        fields=['name', 'account_name', 'root_type'])

    # 建立根科目映射
    root_type_mapping = {
        'Asset': None,
        'Liability': None,
        'Equity': None,
        'Income': None,
        'Expense': None
    }

    for root in existing_roots:
        root_type_mapping[root.root_type] = root.name
        print(f"根科目: {root.account_name} ({root.root_type}) -> {root.name}")

    # CSV中的根科目名称映射到实际的根科目
    csv_root_to_type = {
        '资产': 'Asset',
        '负债': 'Liability',
        '权益': 'Equity',
        '收入': 'Income',
        '费用': 'Expense'
    }

    for csv_name, root_type in csv_root_to_type.items():
        if root_type in root_type_mapping and root_type_mapping[root_type]:
            parent_name_mapping[csv_name] = root_type_mapping[root_type]

    print(f"\n父科目映射:")
    for csv_name, full_name in parent_name_mapping.items():
        print(f"  {csv_name} -> {full_name}")

    # 读取 CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\n共读取 {len(rows)} 条科目数据")

    # 跳过根科目行
    child_accounts = [r for r in rows if r['Parent Account']]

    print(f"需要导入的子科目: {len(child_accounts)} 个\n")

    created = 0
    skipped = 0
    errors = []

    # 创建子科目（多轮迭代）
    max_iterations = 20
    remaining = child_accounts[:]

    for iteration in range(max_iterations):
        if not remaining:
            break

        print(f"第 {iteration + 1} 轮创建子科目，剩余 {len(remaining)} 个")
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

                # 查找父科目
                parent_full_name = None

                # 先检查映射表
                if parent_account_name in parent_name_mapping:
                    parent_full_name = parent_name_mapping[parent_account_name]
                else:
                    # 查找已创建的科目
                    parent_full_name = frappe.db.get_value('Account', {
                        'account_name': parent_account_name,
                        'company': company
                    }, 'name')

                if not parent_full_name:
                    # 父科目还不存在，留到下一轮
                    next_round.append(row)
                    continue

                # 检查父科目是否是组（is_group）
                parent_doc = frappe.get_doc('Account', parent_full_name)
                if not parent_doc.is_group:
                    # 需要将父科目转换为组
                    # 如果有 account_type，需要先清除
                    if parent_doc.account_type:
                        parent_doc.account_type = None
                    parent_doc.is_group = 1
                    parent_doc.save()
                    if round_created <= 3:
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

                # 将新创建的科目加入映射
                parent_name_mapping[account_name] = doc.name

                created += 1
                round_created += 1
                if round_created <= 5 or round_created % 50 == 0:
                    print(f"  创建: {account_name} (父: {parent_account_name})")

            except Exception as e:
                error_msg = str(e)
                # 只记录非重复的错误
                if 'already used' not in error_msg or iteration == 0:
                    errors.append(f"{row['Account Name']}: {error_msg}")
                    if len(errors) <= 15:
                        print(f"  错误: {row['Account Name']} - {error_msg}")

        remaining = next_round
        frappe.db.commit()

        if round_created > 0:
            print(f"  本轮创建了 {round_created} 个科目")

        # 如果连续3轮都没有进展，提前退出
        if iteration >= 3 and round_created == 0:
            print(f"  连续多轮无进展，提前结束")
            break

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
        if len(remaining) <= 15:
            for r in remaining:
                print(f"  - {r['Account Name']} (父: {r['Parent Account']})")
