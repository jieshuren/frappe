#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除自定义的成本中心
"""
import frappe

def delete_custom_cost_centers():
    """删除自定义创建的成本中心"""

    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("删除自定义成本中心")
    print("=" * 60)

    # 要删除的成本中心列表
    cost_centers_to_delete = [
        '生产成本中心 - 华烁',
        '大修一队成本中心 - 华烁',
        '大修二队成本中心 - 华烁',
        '大修三队成本中心 - 华烁',
        '大修四队成本中心 - 华烁',
        '大修五队成本中心 - 华烁',
        '小修队成本中心 - 华烁',
        '高压堵漏堵水成本中心 - 华烁',
        '基地成本中心 - 华烁',
        '机关成本中心 - 华烁'
    ]

    for cc_name in cost_centers_to_delete:
        if frappe.db.exists('Cost Center', cc_name):
            try:
                # 检查是否有子成本中心
                children = frappe.db.count('Cost Center', {'parent_cost_center': cc_name})
                if children > 0:
                    print(f'  ⚠ 跳过（有子成本中心）: {cc_name}')
                    continue

                # 检查是否被使用
                gl_entries = frappe.db.count('GL Entry', {'cost_center': cc_name})
                if gl_entries > 0:
                    print(f'  ⚠ 跳过（已有凭证使用）: {cc_name}')
                    continue

                # 删除
                frappe.delete_doc('Cost Center', cc_name, force=1)
                print(f'  ✓ 删除: {cc_name}')
            except Exception as e:
                print(f'  ✗ 删除失败: {cc_name} - {str(e)}')
        else:
            print(f'  不存在: {cc_name}')

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("删除完成！")
    print("=" * 60)

    # 显示剩余的成本中心
    remaining = frappe.db.get_all('Cost Center',
        {'company': company},
        ['name', 'is_group'],
        order_by='name'
    )

    print("\n剩余成本中心:")
    for cc in remaining:
        group_mark = '📁' if cc.is_group else '📄'
        print(f'  {group_mark} {cc.name}')

    print("\n" + "=" * 60)
