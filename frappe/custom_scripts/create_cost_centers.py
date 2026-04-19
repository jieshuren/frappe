#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建成本中心结构
"""
import frappe

def create_cost_centers():
    """创建成本中心结构"""

    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("创建成本中心结构")
    print("=" * 60)

    # 1. 获取主成本中心
    main_cost_center = frappe.db.get_value('Cost Center', {
        'company': company,
        'cost_center_name': company
    }, 'name')

    if not main_cost_center:
        print("错误：找不到主成本中心")
        return

    print(f'\n主成本中心: {main_cost_center}')

    # 2. 创建生产成本中心（组）
    production_cc_name = '生产成本中心 - 华烁'
    if not frappe.db.exists('Cost Center', production_cc_name):
        production_cc = frappe.get_doc({
            'doctype': 'Cost Center',
            'cost_center_name': '生产成本中心',
            'parent_cost_center': main_cost_center,
            'company': company,
            'is_group': 1
        })
        production_cc.insert(ignore_permissions=True)
        print(f'✓ 创建: {production_cc_name}')
    else:
        print(f'  已存在: {production_cc_name}')

    # 3. 创建各队成本中心（明细）
    production_cost_centers = [
        '大修一队成本中心',
        '大修二队成本中心',
        '大修三队成本中心',
        '大修四队成本中心',
        '大修五队成本中心',
        '小修队成本中心',
        '高压堵漏堵水成本中心'
    ]

    for cc_name in production_cost_centers:
        full_name = f'{cc_name} - 华烁'
        if not frappe.db.exists('Cost Center', full_name):
            cc = frappe.get_doc({
                'doctype': 'Cost Center',
                'cost_center_name': cc_name,
                'parent_cost_center': production_cc_name,
                'company': company,
                'is_group': 0
            })
            cc.insert(ignore_permissions=True)
            print(f'✓ 创建: {full_name}')
        else:
            print(f'  已存在: {full_name}')

    # 4. 创建基地和机关成本中心（明细）
    other_cost_centers = [
        '基地成本中心',
        '机关成本中心'
    ]

    for cc_name in other_cost_centers:
        full_name = f'{cc_name} - 华烁'
        if not frappe.db.exists('Cost Center', full_name):
            cc = frappe.get_doc({
                'doctype': 'Cost Center',
                'cost_center_name': cc_name,
                'parent_cost_center': main_cost_center,
                'company': company,
                'is_group': 0
            })
            cc.insert(ignore_permissions=True)
            print(f'✓ 创建: {full_name}')
        else:
            print(f'  已存在: {full_name}')

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("成本中心创建完成！")
    print("=" * 60)
    print("\n结构：")
    print(f"{main_cost_center}")
    print(f"├─ {production_cc_name}")
    print(f"│  ├─ 大修一队成本中心 - 华烁")
    print(f"│  ├─ 大修二队成本中心 - 华烁")
    print(f"│  ├─ 大修三队成本中心 - 华烁")
    print(f"│  ├─ 大修四队成本中心 - 华烁")
    print(f"│  ├─ 大修五队成本中心 - 华烁")
    print(f"│  ├─ 小修队成本中心 - 华烁")
    print(f"│  └─ 高压堵漏堵水成本中心 - 华烁")
    print(f"├─ 基地成本中心 - 华烁")
    print(f"└─ 机关成本中心 - 华烁")
    print("=" * 60)
