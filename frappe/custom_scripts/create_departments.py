#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建部门结构
"""
import frappe

def create_departments():
    """创建油井维修企业的部门结构"""

    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("创建部门结构")
    print("=" * 60)

    departments = [
        '大修一队',
        '大修二队',
        '大修三队',
        '大修四队',
        '大修五队',
        '小修队',
        '高压堵漏堵水',
        '基地',
        '机关'
    ]

    for dept_name in departments:
        if not frappe.db.exists('Department', dept_name):
            dept = frappe.get_doc({
                'doctype': 'Department',
                'department_name': dept_name,
                'company': company,
                'is_group': 0  # 明细部门，不是组
            })
            dept.insert(ignore_permissions=True)
            print(f'✓ 创建部门: {dept_name}')
        else:
            print(f'  已存在: {dept_name}')

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("部门创建完成！")
    print("=" * 60)
