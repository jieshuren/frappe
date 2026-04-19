#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看部门名称
"""
import frappe

def check_departments():
    """查看部门名称"""
    depts = frappe.db.get_all('Department',
        {'company': '大庆市华烁油气开采技术服务有限公司'},
        ['name', 'department_name']
    )
    print('部门列表:')
    for d in depts:
        print(f'  name: {d.name}')
        print(f'  department_name: {d.department_name}')
        print()
