#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科目表导入脚本
需要在 bench 环境中运行: bench --site aierp.local execute import_accounts.import_chart_of_accounts
"""
import frappe
import csv

def import_chart_of_accounts():
    """导入科目表"""
    company = '大庆市华烁油气开采技术服务有限公司'
    csv_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/科目表_ERPNext格式_EN.csv'

    # 读取 CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"共读取 {len(rows)} 条科目数据")

    # 按层级排序：先创建根科目，再创建子科目
    # 根科目没有 Parent Account
    root_accounts = [r for r in rows if not r['Parent Account']]
    child_accounts = [r for r in rows if r['Parent Account']]

    print(f"根科目: {len(root_accounts)} 个")
    print(f"子科目: {len(child_accounts)} 个")

    created = 0
    skipped = 0
    errors = []

    # 先创建根科目
    for row in root_accounts:
        try:
            account_name = row['Account Name']
            # 检查是否已存在
            exists = frappe.db.exists('Account', {
                'account_name': account_name,
                'company': company
            })

            if exists:
                print(f"跳过已存在的科目: {account_name}")
                skipped += 1
                continue

            # 创建科目
            doc = frappe.get_doc({
                'doctype': 'Account',
                'account_name': account_name,
                'company': company,
                'root_type': row['Root Type'],
                'is_group': int(row['Is Group']) if row['Is Group'] else 0,
                'account_number': row['Account Number'] if row['Account Number'] else None,
                'account_type': row['Account Type'] if row['Account Type'] else None,
                'account_currency': row['Account Currency'] if row['Account Currency'] else None,
            })
            doc.insert()
            created += 1
            print(f"创建根科目: {account_name}")

        except Exception as e:
            errors.append(f"根科目 {row['Account Name']}: {str(e)}")
            print(f"错误: {row['Account Name']} - {str(e)}")

    frappe.db.commit()

    # 再创建子科目（可能需要多次迭代）
    max_iterations = 10
    remaining = child_accounts[:]

    for iteration in range(max_iterations):
        if not remaining:
            break

        print(f"\n第 {iteration + 1} 轮创建子科目，剩余 {len(remaining)} 个")
        next_round = []

        for row in remaining:
            try:
                account_name = row['Account Name']
                parent_account = row['Parent Account']

                # 检查是否已存在
                exists = frappe.db.exists('Account', {
                    'account_name': account_name,
                    'company': company
                })

                if exists:
                    skipped += 1
                    continue

                # 查找父科目
                parent_full_name = frappe.db.get_value('Account', {
                    'account_name': parent_account,
                    'company': company
                }, 'name')

                if not parent_full_name:
                    # 父科目还不存在，留到下一轮
                    next_round.append(row)
                    continue

                # 创建科目
                doc = frappe.get_doc({
                    'doctype': 'Account',
                    'account_name': account_name,
                    'parent_account': parent_full_name,
                    'company': company,
                    'is_group': int(row['Is Group']) if row['Is Group'] else 0,
                    'account_number': row['Account Number'] if row['Account Number'] else None,
                    'account_type': row['Account Type'] if row['Account Type'] else None,
                    'account_currency': row['Account Currency'] if row['Account Currency'] else None,
                })
                doc.insert()
                created += 1
                print(f"  创建: {account_name} (父: {parent_account})")

            except Exception as e:
                errors.append(f"{row['Account Name']}: {str(e)}")
                print(f"  错误: {row['Account Name']} - {str(e)}")

        remaining = next_round
        frappe.db.commit()

    # 输出结果
    print(f"\n导入完成！")
    print(f"成功创建: {created} 个科目")
    print(f"跳过已存在: {skipped} 个科目")
    print(f"失败: {len(errors)} 个科目")

    if errors:
        print("\n错误详情：")
        for err in errors[:10]:  # 只显示前10个错误
            print(f"  - {err}")

    if remaining:
        print(f"\n警告: 还有 {len(remaining)} 个科目未能创建（可能是父科目缺失）")
        for r in remaining[:5]:
            print(f"  - {r['Account Name']} (父: {r['Parent Account']})")
