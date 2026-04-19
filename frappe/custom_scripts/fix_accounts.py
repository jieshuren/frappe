#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复应收应付科目并重新导入期初
"""
import frappe

def fix_and_reimport():
    """修复科目并重新导入"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("修复应收应付科目")
    print("=" * 60)

    # 1. 恢复 112201 为明细科目
    print("\n1. 恢复应收应付为明细科目:")
    frappe.db.sql("""
        UPDATE `tabAccount`
        SET is_group = 0, account_type = 'Receivable'
        WHERE name = '112201 - 吉林锐普石油 - 华烁'
    """)
    print("   ✓ 112201 - 吉林锐普石油 恢复为 Receivable 明细科目")

    frappe.db.sql("""
        UPDATE `tabAccount`
        SET is_group = 0, account_type = 'Payable'
        WHERE name = '2202 - 应付账款 - 华烁'
    """)
    print("   ✓ 2202 - 应付账款 恢复为 Payable 明细科目")

    # 2. 更新默认科目为组科目
    print("\n2. 更新公司默认科目:")
    frappe.db.sql("""
        UPDATE `tabCompany`
        SET default_receivable_account = '1122 - 应收账款 - 华烁',
            default_payable_account = '2202 - 应付账款 - 华烁'
        WHERE name = %s
    """, company)
    print("   ✓ 默认应收: 1122 - 应收账款（组科目）")
    print("   ✓ 默认应付: 2202 - 应付账款（明细科目，暂时）")

    frappe.db.commit()

    print("\n" + "=" * 60)
    print("修复完成")
    print("说明：")
    print("- 期初凭证中的应收应付科目已恢复为明细科目")
    print("- 新业务将使用组科目自动创建明细")
    print("=" * 60)
