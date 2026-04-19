#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import frappe

def verify_accounts():
    """验证导入的科目表"""
    company = '大庆市华烁油气开采技术服务有限公司'

    # 统计各类科目
    accounts = frappe.db.get_all('Account',
        filters={'company': company},
        fields=['name', 'account_name', 'root_type', 'is_group'])

    print("=" * 60)
    print("科目表导入验证")
    print("=" * 60)
    print(f"\n总科目数: {len(accounts)}")

    # 按 root_type 分组统计
    by_root = {}
    for acc in accounts:
        rt = acc.root_type or 'None'
        if rt not in by_root:
            by_root[rt] = {'total': 0, 'group': 0, 'ledger': 0}
        by_root[rt]['total'] += 1
        if acc.is_group:
            by_root[rt]['group'] += 1
        else:
            by_root[rt]['ledger'] += 1

    print("\n按类型统计：")
    for root_type, stats in sorted(by_root.items()):
        print(f"  {root_type}:")
        print(f"    总计: {stats['total']} 个")
        print(f"    组科目: {stats['group']} 个")
        print(f"    明细科目: {stats['ledger']} 个")

    # 显示根科目
    print("\n根科目：")
    roots = frappe.db.get_all('Account',
        filters={'company': company, 'parent_account': ['is', 'not set']},
        fields=['account_name', 'root_type', 'account_number'],
        order_by='account_number')

    for root in roots:
        num = root.account_number or ''
        print(f"  {root.account_name} ({root.root_type}) {num}")

    print("\n" + "=" * 60)
    print("✓ 中国会计科目表导入成功！")
    print("=" * 60)
