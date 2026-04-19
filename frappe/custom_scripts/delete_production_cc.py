#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除生产成本中心
"""
import frappe

def delete_production_cc():
    """删除生产成本中心"""

    try:
        frappe.delete_doc('Cost Center', '生产成本中心 - 华烁', force=1)
        frappe.db.commit()
        print('✓ 已删除: 生产成本中心 - 华烁')
    except Exception as e:
        print(f'✗ 删除失败: {str(e)}')

    # 显示剩余
    remaining = frappe.db.get_all('Cost Center',
        {'company': '大庆市华烁油气开采技术服务有限公司'},
        ['name', 'is_group']
    )
    print('\n剩余成本中心:')
    for cc in remaining:
        mark = '📁' if cc.is_group else '📄'
        print(f'  {mark} {cc.name}')
