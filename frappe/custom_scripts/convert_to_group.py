#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将应收应付明细科目改为组科目
"""
import frappe

def convert_to_group():
    """将应收应付科目改为组科目"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("将应收应付科目改为组科目")
    print("=" * 60)

    # 1. 将 112201 - 吉林锐普石油 改为组科目
    print("\n1. 处理应收账款科目:")
    receivable = '112201 - 吉林锐普石油 - 华烁'

    # 检查是否有子科目
    children = frappe.db.count('Account', {'parent_account': receivable})
    if children > 0:
        print(f"   ✗ 该科目有 {children} 个子科目，无法直接转换")
    else:
        # 清除 account_type（组科目不能有类型）
        frappe.db.sql("""
            UPDATE `tabAccount`
            SET is_group = 1, account_type = NULL
            WHERE name = %s
        """, receivable)
        print(f"   ✓ 已将 {receivable} 改为组科目")

    # 2. 将 2202 - 应付账款 改为组科目
    print("\n2. 处理应付账款科目:")
    payable = '2202 - 应付账款 - 华烁'

    children = frappe.db.count('Account', {'parent_account': payable})
    if children > 0:
        print(f"   ✗ 该科目有 {children} 个子科目，无法直接转换")
    else:
        frappe.db.sql("""
            UPDATE `tabAccount`
            SET is_group = 1, account_type = NULL
            WHERE name = %s
        """, payable)
        print(f"   ✓ 已将 {payable} 改为组科目")

    frappe.db.commit()

    # 3. 更新公司默认科目
    print("\n3. 更新公司默认科目:")

    # 应收改为 1122 - 应收账款（组科目）
    receivable_group = '1122 - 应收账款 - 华烁'
    frappe.db.sql("""
        UPDATE `tabCompany`
        SET default_receivable_account = %s
        WHERE name = %s
    """, (receivable_group, company))
    print(f"   ✓ 默认应收账款改为: {receivable_group}")

    # 应付保持 2202（现在已经是组科目）
    print(f"   ✓ 默认应付账款: {payable}（已改为组科目）")

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("修改完成")
    print("=" * 60)
