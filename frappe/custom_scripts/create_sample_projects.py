#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建示例项目
"""
import frappe

def create_sample_projects():
    """创建示例项目"""

    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("创建示例项目")
    print("=" * 60)

    # 示例项目列表
    projects = [
        {'name': 'A1-001井', 'department': '大修一队 - 华烁', 'customer': '吉林锐普石油'},
        {'name': 'A1-002井', 'department': '大修一队 - 华烁', 'customer': '吉林锐普石油'},
        {'name': 'B2-001井', 'department': '大修二队 - 华烁', 'customer': '吉林锐普石油'},
        {'name': 'C3-001井', 'department': '小修队 - 华烁', 'customer': '吉林锐普石油'},
    ]

    for proj in projects:
        if not frappe.db.exists('Project', proj['name']):
            project = frappe.get_doc({
                'doctype': 'Project',
                'project_name': proj['name'],
                'company': company,
                'department': proj['department'],
                'customer': proj['customer'],
                'project_type': 'External',
                'status': 'Open'
            })
            project.insert(ignore_permissions=True)
            print(f"✓ 创建项目: {proj['name']} (归属: {proj['department']})")
        else:
            print(f"  已存在: {proj['name']}")

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("示例项目创建完成！")
    print("=" * 60)
    print("\n现在可以测试级联筛选功能：")
    print("1. 打开：会计 > 凭证 > 新建凭证")
    print("2. 在分录中选择部门：大修一队")
    print("3. 点击项目下拉框，只会显示：")
    print("   - A1-001井")
    print("   - A1-002井")
    print("4. 不会显示其他队的项目（B2-001井、C3-001井）")
    print("=" * 60)
