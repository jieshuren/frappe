#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建客户端脚本：项目可跨部门，部门不再强制筛选项目
"""
import frappe

def create_client_script():
    """创建客户端脚本"""

    script_name = "Journal Entry - Department Project Filter"

    # 读取 JS 文件内容
    with open('/Users/comfan/Documents/GitHub/AIERP/journal_entry_account_filter.js', 'r', encoding='utf-8') as f:
        script_content = f.read()

    # 检查是否已存在
    if frappe.db.exists('Client Script', script_name):
        print(f'客户端脚本已存在: {script_name}')
        # 更新
        doc = frappe.get_doc('Client Script', script_name)
        doc.script = script_content
        doc.save()
        print('✓ 已更新脚本内容')
    else:
        # 创建新的
        doc = frappe.get_doc({
            'doctype': 'Client Script',
            'name': script_name,
            'dt': 'Journal Entry',
            'view': 'Form',
            'enabled': 1,
            'script': script_content
        })
        doc.insert(ignore_permissions=True)
        print(f'✓ 已创建客户端脚本: {script_name}')

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("配置完成！")
    print("=" * 60)
    print("\n功能说明：")
    print("1. 不再强制按部门过滤项目，允许同一项目出现在多个部门")
    print("2. 如果先选项目且项目主数据带部门，会自动填充部门")
    print("3. 如果项目主数据部门与当前分录部门不同，只提示，不自动清空")
    print("=" * 60)
