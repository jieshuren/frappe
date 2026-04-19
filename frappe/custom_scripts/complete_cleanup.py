#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底清理并重置凭证编号
"""
import frappe

def complete_cleanup():
    """彻底清理所有数据"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("第一步：彻底清理所有数据")
    print("=" * 60)

    # 1. 删除所有 GL Entry
    print("\n1. 删除所有 GL Entry...")
    frappe.db.sql("DELETE FROM `tabGL Entry` WHERE company = %s", company)
    print("   ✓ 已删除所有 GL Entry")

    # 2. 删除所有 Journal Entry
    print("\n2. 删除所有凭证...")
    frappe.db.sql("DELETE FROM `tabJournal Entry Account` WHERE parent IN (SELECT name FROM `tabJournal Entry` WHERE company = %s)", company)
    frappe.db.sql("DELETE FROM `tabJournal Entry` WHERE company = %s", company)
    print("   ✓ 已删除所有凭证")

    # 3. 删除期初余额调整科目
    print("\n3. 删除临时科目...")
    temp_accounts = frappe.db.get_all('Account', {
        'company': company,
        'account_name': ['in', ['期初余额调整']]
    }, pluck='name')

    for acc in temp_accounts:
        frappe.db.sql("DELETE FROM `tabAccount` WHERE name = %s", acc)
        print(f"   ✓ 删除: {acc}")

    # 4. 删除所有客户
    print("\n4. 删除所有客户...")
    customers = frappe.db.get_all('Customer', filters={'disabled': 0}, pluck='name')
    for cust in customers:
        if cust != 'Guest':
            frappe.db.sql("DELETE FROM `tabCustomer` WHERE name = %s", cust)
            print(f"   ✓ {cust}")

    # 5. 删除所有供应商
    print("\n5. 删除所有供应商...")
    suppliers = frappe.db.get_all('Supplier', pluck='name')
    for supp in suppliers:
        frappe.db.sql("DELETE FROM `tabSupplier` WHERE name = %s", supp)
        print(f"   ✓ {supp}")

    # 6. 重置凭证编号序列
    print("\n6. 重置凭证编号...")
    frappe.db.sql("""
        DELETE FROM `tabSeries`
        WHERE name LIKE 'ACC-JV-2026-%'
    """)
    print("   ✓ 凭证编号已重置")

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("清理完成！")
    print("=" * 60)
