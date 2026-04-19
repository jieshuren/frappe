#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看现有成本中心
"""
import frappe

def check_cost_centers():
    """查看现有成本中心"""
    company = '大庆市华烁油气开采技术服务有限公司'

    cost_centers = frappe.db.get_all('Cost Center',
        {'company': company},
        ['name', 'cost_center_name', 'is_group', 'parent_cost_center'],
        order_by='name'
    )

    print('现有成本中心:')
    for cc in cost_centers:
        parent = cc.parent_cost_center if cc.parent_cost_center else '(根)'
        group_mark = '📁' if cc.is_group else '📄'
        print(f'{group_mark} {cc.name}')
        print(f'   父级: {parent}')
