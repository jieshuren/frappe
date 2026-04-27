import frappe

def run():
    company = '大庆市华烁油气开采技术服务有限公司'
    print("Restoring account types...")
    
    # 1. AR
    frappe.db.sql("""
        UPDATE `tabAccount` 
        SET account_type = 'Receivable' 
        WHERE account_number IN ('1122', '112200') 
        AND company = %s
    """, (company,))
    
    # 2. AP
    frappe.db.sql("""
        UPDATE `tabAccount` 
        SET account_type = 'Payable' 
        WHERE account_number IN ('2202', '220200') 
        AND company = %s
    """, (company,))
    
    # 3. Cash
    frappe.db.sql("""
        UPDATE `tabAccount` 
        SET account_type = 'Cash' 
        WHERE account_number LIKE '1001%%' 
        AND company = %s
    """, (company,))
    
    # 4. Bank
    frappe.db.sql("""
        UPDATE `tabAccount` 
        SET account_type = 'Bank' 
        WHERE account_number LIKE '1002%%' 
        AND company = %s
    """, (company,))
    
    frappe.db.commit()
    frappe.clear_cache()
    print("Account types restored successfully.")

if __name__ == "__main__":
    run()
