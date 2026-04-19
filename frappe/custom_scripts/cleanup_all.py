#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底清理所有期初数据和交易记录
"""
import frappe

def cleanup_all():
    """彻底清理"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("彻底清理所有期初数据")
    print("=" * 60)

    # 1. 删除所有 GL Entry
    print("\n删除所有总账分录...")
    frappe.db.sql("DELETE FROM `tabGL Entry` WHERE company = %s", company)
    print("✓ 已删除所有总账分录")

    # 2. 删除所有 Journal Entry
    print("\n删除所有凭证...")
    frappe.db.sql("DELETE FROM `tabJournal Entry Account` WHERE parent IN (SELECT name FROM `tabJournal Entry` WHERE company = %s)", company)
    frappe.db.sql("DELETE FROM `tabJournal Entry` WHERE company = %s", company)
    print("✓ 已删除所有凭证")

    # 3. 删除期初余额调整科目
    print("\n删除临时科目...")
    temp_account = frappe.db.get_value('Account', {
        'company': company,
        'account_name': '期初余额调整'
    }, 'name')

    if temp_account:
        frappe.db.sql("DELETE FROM `tabAccount` WHERE name = %s", temp_account)
        print(f"✓ 删除临时科目: {temp_account}")

    # 4. 删除所有客户
    print("\n删除所有客户...")
    customers = frappe.db.get_all('Customer', filters={'disabled': 0}, pluck='name')
    for cust in customers:
        if cust != 'Guest':
            try:
                frappe.db.sql("DELETE FROM `tabCustomer` WHERE name = %s", cust)
                print(f"  ✓ {cust}")
            except Exception as e:
                print(f"  ✗ {cust}: {str(e)}")

    # 5. 删除所有供应商
    print("\n删除所有供应商...")
    suppliers = frappe.db.get_all('Supplier', pluck='name')
    for supp in suppliers:
        try:
            frappe.db.sql("DELETE FROM `tabSupplier` WHERE name = %s", supp)
            print(f"  ✓ {supp}")
        except Exception as e:
            print(f"  ✗ {supp}: {str(e)}")

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("彻底清理完成")
    print("=" * 60)
