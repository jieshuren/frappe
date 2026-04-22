
import frappe

def fix_all_ledgers():
    print("开始全局收付款辅助账校准 (V16 适配版)...")
    journal_entries = frappe.get_all("Journal Entry", filters={"docstatus": 1}, fields=["name"])
    total = len(journal_entries)
    print(f"共发现 {total} 笔凭证需校准。")

    for i, je in enumerate(journal_entries):
        # 1. 彻底清理旧辅助账记录
        frappe.db.sql("DELETE FROM `tabPayment Ledger Entry` WHERE voucher_no = %s", je.name)
        
        # 2. 重新触发记账逻辑
        try:
            doc = frappe.get_doc("Journal Entry", je.name)
            doc.make_gl_entries()
            
            if (i + 1) % 50 == 0:
                print(f"进度: {i + 1}/{total}")
                frappe.db.commit()
        except Exception as e:
            print(f"处理 {je.name} 时出错: {str(e)}")

    frappe.db.commit()
    print("校准完成！")
