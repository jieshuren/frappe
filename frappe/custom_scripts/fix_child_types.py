#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量设置子科目类型
"""
import frappe

def fix_child_account_types():
    """批量设置子科目类型"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("批量设置子科目类型")
    print("=" * 60)

    # 需要处理的组科目及其子科目应该设置的类型
    group_accounts = {
        '应收账款': 'Receivable',
        '库存商品': 'Stock',
        '固定资产': 'Fixed Asset',
    }

    total_updated = 0

    for parent_name, account_type in group_accounts.items():
        # 查找父科目
        parent = frappe.db.get_value('Account', {
            'company': company,
            'account_name': parent_name
        }, 'name')

        if not parent:
            print(f"\n⚠ {parent_name}: 未找到")
            continue

        # 查找所有子科目（非组科目）
        children = frappe.db.get_all('Account',
            filters={'parent_account': parent, 'is_group': 0},
            fields=['name', 'account_name', 'account_type'])

        if not children:
            print(f"\n{parent_name}: 没有子科目")
            continue

        print(f"\n{parent_name} ({account_type}):")
        print(f"  找到 {len(children)} 个子科目")

        updated = 0
        for child in children:
            if child.account_type != account_type:
                try:
                    frappe.db.sql("""
                        UPDATE `tabAccount`
                        SET account_type = %s
                        WHERE name = %s
                    """, (account_type, child.name))
                    updated += 1
                    if updated <= 5:
                        print(f"    ✓ {child.account_name}")
                except Exception as e:
                    print(f"    ✗ {child.account_name}: {str(e)}")

        if updated > 5:
            print(f"    ... 还有 {updated - 5} 个")

        print(f"  更新了 {updated} 个子科目")
        total_updated += updated

    frappe.db.commit()

    print(f"\n总计更新: {total_updated} 个科目")
    print("=" * 60)
