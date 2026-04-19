#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入科目期初余额
"""
import frappe
import pandas as pd
from datetime import datetime

def import_opening_balances():
    """导入科目期初余额"""
    company = '大庆市华烁油气开采技术服务有限公司'
    excel_file = '/Users/comfan/Documents/GitHub/AIERP/财务数据/科目期初.xlsx'

    print("=" * 60)
    print("导入科目期初余额")
    print("=" * 60)

    # 读取 Excel 文件
    df = pd.read_excel(excel_file)
    print(f"\n读取到 {len(df)} 条期初数据")

    # 显示列名
    print(f"\n列名: {list(df.columns)}")

    # 过滤有期初余额的科目
    df_with_balance = df[
        (df['期初余额本位币'].notna()) &
        (df['期初余额本位币'] != 0)
    ].copy()

    print(f"有期初余额的科目: {len(df_with_balance)} 个")

    # 显示前10条数据
    print("\n前10条期初数据:")
    for idx, row in df_with_balance.head(10).iterrows():
        account_code = str(int(row['科目编码'])) if pd.notna(row['科目编码']) else ''
        account_name = row['科目名称']
        direction = row['方向']
        balance = row['期初余额本位币']
        print(f"  {account_code} {account_name}: {direction} {balance:,.2f}")

    # 询问是否继续
    print(f"\n准备导入 {len(df_with_balance)} 个科目的期初余额")
    print("注意：ERPNext 中期初余额通过 Opening Entry 凭证录入")
    print("\n导入方式：")
    print("1. 创建期初余额凭证（Opening Entry）")
    print("2. 日期设置为会计年度开始日期")
    print("3. 借方科目和贷方科目自动平衡")

    # 统计借贷方总额
    debit_total = df_with_balance[df_with_balance['方向'] == '借']['期初余额本位币'].sum()
    credit_total = df_with_balance[df_with_balance['方向'] == '贷']['期初余额本位币'].sum()

    print(f"\n借方总额: {debit_total:,.2f}")
    print(f"贷方总额: {credit_total:,.2f}")
    print(f"差额: {abs(debit_total - credit_total):,.2f}")

    if abs(debit_total - credit_total) > 0.01:
        print("\n⚠️  警告：借贷方不平衡！")
        print("建议先检查期初数据的准确性")

    print("\n" + "=" * 60)
    print("期初数据分析完成")
    print("=" * 60)

    # 返回数据供后续使用
    return df_with_balance
