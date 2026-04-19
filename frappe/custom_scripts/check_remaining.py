#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import frappe

def check_remaining_accounts():
    """查看剩余科目"""
    company = '大庆市华烁油气开采技术服务有限公司'

    accounts = frappe.db.get_all('Account',
        filters={'company': company},
        fields=['name', 'account_name', 'is_group', 'root_type', 'parent_account'],
        order_by='lft')

    print(f"剩余科目数: {len(accounts)}\n")

    # 按 root_type 分组
    by_root = {}
    for acc in accounts:
        rt = acc.root_type or 'None'
        if rt not in by_root:
            by_root[rt] = []
        by_root[rt].append(acc)

    for root_type, accs in by_root.items():
        print(f"\n{root_type}: {len(accs)} 个")
        for acc in accs[:10]:
            parent = acc.parent_account or '(根科目)'
            print(f"  {acc.account_name} | {acc.name}")
