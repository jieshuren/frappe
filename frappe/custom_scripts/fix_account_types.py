#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正科目类型，使其与 ERPNext 兼容
"""
import frappe

def fix_account_types():
    """修正科目类型"""
    company = '大庆市华烁油气开采技术服务有限公司'

    print("=" * 60)
    print("修正科目类型")
    print("=" * 60)

    # 需要修正的科目映射：科目名称 -> Account Type
    account_type_fixes = {
        # 应收账款（必须是 Receivable 类型）
        '应收账款': 'Receivable',

        # 库存相关科目（必须是 Stock 类型）
        '库存商品': 'Stock',
        '原材料': 'Stock',
        '周转材料': 'Stock',
        '材料采购': 'Stock',
        '在途物资': 'Stock',
        '发出商品': 'Stock',
        '委托加工物资': 'Stock',

        # 固定资产（必须是 Fixed Asset 类型）
        '固定资产': 'Fixed Asset',
        '在建工程': 'Capital Work in Progress',

        # 其他可能需要的
        '生产成本': 'Stock',
    }

    updated = 0
    not_found = []

    for account_name, account_type in account_type_fixes.items():
        # 查找科目
        account = frappe.db.get_value('Account', {
            'company': company,
            'account_name': account_name
        }, ['name', 'is_group'], as_dict=True)

        if account:
            # 如果是组科目，不能设置 account_type
            if account.is_group:
                print(f"  跳过组科目: {account_name}")
                continue

            # 更新 account_type
            try:
                frappe.db.sql("""
                    UPDATE `tabAccount`
                    SET account_type = %s
                    WHERE name = %s
                """, (account_type, account.name))

                updated += 1
                print(f"  ✓ {account_name} -> {account_type}")
            except Exception as e:
                print(f"  ✗ {account_name}: {str(e)}")
        else:
            not_found.append(account_name)
            print(f"  ⚠ {account_name}: 科目不存在")

    frappe.db.commit()

    print(f"\n修正完成：")
    print(f"  成功更新: {updated} 个科目")
    print(f"  未找到: {len(not_found)} 个科目")

    if not_found:
        print(f"\n未找到的科目：")
        for name in not_found:
            print(f"    - {name}")

    print("\n" + "=" * 60)
