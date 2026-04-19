#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除现有科目并重新导入
需要在 bench 环境中运行: bench --site aierp.local execute frappe.custom_scripts.reimport_accounts.reimport_chart_of_accounts
"""
import frappe
import csv

def reimport_chart_of_accounts():
    """删除现有科目并重新导入"""
    company = '大庆市华烁油气开采技术服务有限公司'
    csv_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/科目表_ERPNext格式_EN.csv'

    print("=" * 60)
    print("开始删除现有科目...")
    print("=" * 60)

    # 获取所有现有科目
    existing_accounts = frappe.db.get_all('Account',
        filters={'company': company},
        fields=['name', 'is_group', 'lft', 'rgt'],
        order_by='lft desc')  # 从叶子节点开始删除

    print(f"找到 {len(existing_accounts)} 个现有科目")

    # 先检查是否有交易数据
    has_transactions = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabGL Entry`
        WHERE company = %s
    """, company)[0][0]

    if has_transactions > 0:
        print(f"\n警告：发现 {has_transactions} 条会计分录！")
        print("删除科目会导致数据丢失，建议先备份数据库。")
        print("如果确定要继续，请手动执行删除操作。")
        return

    deleted = 0
    errors = []

    # 删除所有科目（从叶子节点开始）
    for acc in existing_accounts:
        try:
            doc = frappe.get_doc('Account', acc.name)
            doc.delete()
            deleted += 1
            if deleted % 50 == 0:
                print(f"  已删除 {deleted} 个科目...")
        except Exception as e:
            errors.append(f"{acc.name}: {str(e)}")
            if len(errors) <= 5:
                print(f"  删除失败: {acc.name} - {str(e)}")

    frappe.db.commit()

    print(f"\n删除完成：成功删除 {deleted} 个科目")
    if errors:
        print(f"删除失败: {len(errors)} 个科目")

    print("\n" + "=" * 60)
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

    # 第一步：创建根科目
    print("创建根科目...")
    for row in root_accounts:
        try:
            account_name = row['Account Name']
            root_type = row['Root Type']

            doc = frappe.get_doc({
                'doctype': 'Account',
                'account_name': account_name,
                'company': company,
                'root_type': root_type,
                'is_group': 1,
                'account_number': row['Account Number'] if row['Account Number'] else None,
            })
            doc.insert()
            parent_mapping[account_name] = doc.name
            created += 1
            print(f"  创建根科目: {account_name} ({root_type})")

        except Exception as e:
            errors.append(f"根科目 {row['Account Name']}: {str(e)}")
            print(f"  错误: {row['Account Name']} - {str(e)}")

    frappe.db.commit()

    # 第二步：创建子科目（多轮迭代）
    print("\n创建子科目...")
    max_iterations = 20
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
                    # 父科目还不存在，留到下一轮
                    next_round.append(row)
                    continue

                # 检查父科目是否是组
                parent_doc = frappe.get_doc('Account', parent_full_name)
                if not parent_doc.is_group:
                    parent_doc.is_group = 1
                    if parent_doc.account_type:
                        parent_doc.account_type = None
                    parent_doc.save()

                # 创建科目
                is_group = int(row['Is Group']) if row['Is Group'] else 0
                account_type = row['Account Type'] if row['Account Type'] else None

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

                parent_mapping[account_name] = doc.name
                created += 1
                round_created += 1

                if round_created <= 5 or round_created % 100 == 0:
                    print(f"  创建: {account_name}")

            except Exception as e:
                error_msg = str(e)
                if 'already used' not in error_msg or iteration == 0:
                    errors.append(f"{row['Account Name']}: {error_msg}")
                    if len(errors) <= 10:
                        print(f"  错误: {row['Account Name']} - {error_msg}")

        remaining = next_round
        frappe.db.commit()

        if round_created > 0:
            print(f"  本轮创建了 {round_created} 个科目")

        if iteration >= 3 and round_created == 0:
            print(f"  连续多轮无进展，提前结束")
            break

    # 输出结果
    print("\n" + "=" * 60)
    print("导入完成！")
    print("=" * 60)
    print(f"成功创建: {created} 个科目")
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

    # 最终统计
    final_count = len(frappe.db.get_all('Account', filters={'company': company}))
    print(f"\n最终科目总数: {final_count}")
