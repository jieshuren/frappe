#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底清理并重构应收应付科目（ERPNext 标准方式）
"""
import frappe

def complete_cleanup_and_restructure():
    """彻底清理并重构"""
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

    # 3. 删除所有客户
    print("\n3. 删除所有客户...")
    customers = frappe.db.get_all('Customer', filters={'disabled': 0}, pluck='name')
    for cust in customers:
        if cust != 'Guest':
            frappe.db.sql("DELETE FROM `tabCustomer` WHERE name = %s", cust)
            print(f"   ✓ {cust}")

    # 4. 删除所有供应商
    print("\n4. 删除所有供应商...")
    suppliers = frappe.db.get_all('Supplier', pluck='name')
    for supp in suppliers:
        frappe.db.sql("DELETE FROM `tabSupplier` WHERE name = %s", supp)
        print(f"   ✓ {supp}")

    # 5. 删除客户/供应商明细科目
    print("\n5. 删除客户/供应商明细科目...")

    # 删除应收账款明细科目（112201 等）
    receivable_details = frappe.db.sql("""
        SELECT name FROM `tabAccount`
        WHERE company = %s
        AND account_number LIKE '1122%%'
        AND account_number != '1122'
        AND is_group = 0
    """, company, as_dict=True)

    for acc in receivable_details:
        frappe.db.sql("DELETE FROM `tabAccount` WHERE name = %s", acc.name)
        print(f"   ✓ 删除应收明细: {acc.name}")

    # 删除应付账款明细科目（220201 等）
    payable_details = frappe.db.sql("""
        SELECT name FROM `tabAccount`
        WHERE company = %s
        AND account_number LIKE '2202%%'
        AND account_number != '2202'
        AND is_group = 0
    """, company, as_dict=True)

    for acc in payable_details:
        frappe.db.sql("DELETE FROM `tabAccount` WHERE name = %s", acc.name)
        print(f"   ✓ 删除应付明细: {acc.name}")

    # 6. 重置凭证编号序列
    print("\n6. 重置凭证编号...")
    frappe.db.sql("""
        DELETE FROM `tabSeries`
        WHERE name LIKE 'ACC-JV-2026-%'
    """)
    print("   ✓ 凭证编号已重置")

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("第二步：重构应收应付科目（ERPNext 标准方式）")
    print("=" * 60)

    # 7. 确保 1122 是组科目
    print("\n7. 设置应收账款为组科目...")
    receivable_group = frappe.db.get_value('Account', {
        'company': company,
        'account_number': '1122'
    }, 'name')

    if receivable_group:
        frappe.db.sql("""
            UPDATE `tabAccount`
            SET is_group = 1, account_type = NULL
            WHERE name = %s
        """, receivable_group)
        print(f"   ✓ {receivable_group} 设置为组科目")

    # 8. 创建应收账款默认明细科目
    print("\n8. 创建应收账款默认明细科目...")
    default_receivable = frappe.get_doc({
        'doctype': 'Account',
        'account_name': '应收账款-默认',
        'account_number': '112200',
        'parent_account': receivable_group,
        'company': company,
        'is_group': 0,
        'account_type': 'Receivable',
        'root_type': 'Asset'
    })
    default_receivable.insert(ignore_permissions=True)
    print(f"   ✓ 创建: {default_receivable.name}")

    # 9. 确保 2202 是组科目
    print("\n9. 设置应付账款为组科目...")
    payable_group = frappe.db.get_value('Account', {
        'company': company,
        'account_number': '2202'
    }, 'name')

    if payable_group:
        frappe.db.sql("""
            UPDATE `tabAccount`
            SET is_group = 1, account_type = NULL
            WHERE name = %s
        """, payable_group)
        print(f"   ✓ {payable_group} 设置为组科目")

    # 10. 创建应付账款默认明细科目
    print("\n10. 创建应付账款默认明细科目...")
    default_payable = frappe.get_doc({
        'doctype': 'Account',
        'account_name': '应付账款-默认',
        'account_number': '220200',
        'parent_account': payable_group,
        'company': company,
        'is_group': 0,
        'account_type': 'Payable',
        'root_type': 'Liability'
    })
    default_payable.insert(ignore_permissions=True)
    print(f"   ✓ 创建: {default_payable.name}")

    # 11. 更新公司默认科目
    print("\n11. 更新公司默认科目...")
    frappe.db.sql("""
        UPDATE `tabCompany`
        SET default_receivable_account = %s,
            default_payable_account = %s
        WHERE name = %s
    """, (default_receivable.name, default_payable.name, company))
    print(f"   ✓ 默认应收: {default_receivable.name}")
    print(f"   ✓ 默认应付: {default_payable.name}")

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("清理和重构完成！")
    print("=" * 60)
    print("\n说明：")
    print("- 已删除所有期初凭证和 GL Entry")
    print("- 已删除所有客户和供应商")
    print("- 已删除所有客户/供应商明细科目")
    print("- 应收账款（1122）设置为组科目")
    print("- 应付账款（2202）设置为组科目")
    print("- 创建了默认明细科目（112200、220200）")
    print("- 期初余额将通过 Party 字段关联客户/供应商")
    print("=" * 60)
