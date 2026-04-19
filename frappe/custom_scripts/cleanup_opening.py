#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理所有期初导入数据
"""
import frappe

def cleanup_opening_data():
    """清理期初导入数据"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("清理期初导入数据")
    print("=" * 60)

    # 1. 删除所有 Opening Entry 凭证
    je_list = frappe.db.get_all('Journal Entry',
        filters={'company': company, 'is_opening': 'Yes'},
        fields=['name', 'docstatus'])

    print(f"\n找到 {len(je_list)} 个期初凭证")
    for je in je_list:
        try:
            if je.docstatus == 1:
                # 取消提交
                doc = frappe.get_doc('Journal Entry', je.name)
                doc.cancel()
                print(f"  ✓ 取消提交: {je.name}")
            # 删除
            frappe.delete_doc('Journal Entry', je.name, force=1)
            print(f"  ✓ 删除: {je.name}")
        except Exception as e:
            print(f"  ✗ {je.name}: {str(e)}")

    # 2. 删除期初余额调整科目
    temp_account = frappe.db.get_value('Account', {
        'company': company,
        'account_name': '期初余额调整'
    }, 'name')

    if temp_account:
        try:
            frappe.delete_doc('Account', temp_account, force=1)
            print(f"\n✓ 删除临时科目: {temp_account}")
        except Exception as e:
            print(f"\n✗ 删除临时科目失败: {str(e)}")

    # 3. 删除自动创建的客户（通过创建时间判断）
    customers = frappe.db.sql("""
        SELECT name FROM `tabCustomer`
        WHERE creation > DATE_SUB(NOW(), INTERVAL 2 HOUR)
        AND name NOT IN ('Guest')
    """, as_dict=True)

    print(f"\n找到 {len(customers)} 个最近创建的客户")
    for cust in customers:
        try:
            # 先删除相关的 GL Entry
            frappe.db.sql("DELETE FROM `tabGL Entry` WHERE party_type = 'Customer' AND party = %s", cust.name)
            frappe.delete_doc('Customer', cust.name, force=1)
            print(f"  ✓ 删除客户: {cust.name}")
        except Exception as e:
            print(f"  ✗ {cust.name}: {str(e)}")

    # 4. 删除自动创建的供应商
    suppliers = frappe.db.sql("""
        SELECT name FROM `tabSupplier`
        WHERE creation > DATE_SUB(NOW(), INTERVAL 2 HOUR)
    """, as_dict=True)

    print(f"\n找到 {len(suppliers)} 个最近创建的供应商")
    for supp in suppliers:
        try:
            # 先删除相关的 GL Entry
            frappe.db.sql("DELETE FROM `tabGL Entry` WHERE party_type = 'Supplier' AND party = %s", supp.name)
            frappe.delete_doc('Supplier', supp.name, force=1)
            print(f"  ✓ 删除供应商: {supp.name}")
        except Exception as e:
            print(f"  ✗ {supp.name}: {str(e)}")

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("清理完成")
    print("=" * 60)
