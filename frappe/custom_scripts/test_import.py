#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入基础数据
"""
import frappe
from frappe.custom_scripts.import_vouchers import import_vouchers_from_excel

def test_import():
    """测试导入"""
    file_path = '/Users/comfan/Documents/GitHub/AIERP/财务数据/HuaShuo_凭证列表_202501-202503.xlsx'
    count = import_vouchers_from_excel(file_path)
    print(f'\n准备导入 {count} 个凭证')
