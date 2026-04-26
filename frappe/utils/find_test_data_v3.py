import frappe

def find_test_data():
    frappe.connect()
    
    doctypes = [
        "Company", "Customer", "Supplier", "Item", "Account", 
        "Journal Entry", "Sales Invoice", "Purchase Invoice", 
        "Project", "Cost Center", "Warehouse", "Bank Account",
        "Employee", "Department", "Designation", "Task"
    ]
    
    found_records = {}
    
    for dt in doctypes:
        try:
            if not frappe.db.exists("DocType", dt):
                continue
                
            records = frappe.get_all(dt, or_filters=[
                ["name", "like", "%Test%"],
                ["name", "like", "%测试%"]
            ], fields=["name"])
            
            meta = frappe.get_meta(dt)
            title_field = meta.get_title_field()
            if title_field and title_field != "name":
                title_records = frappe.get_all(dt, or_filters=[
                    [title_field, "like", "%Test%"],
                    [title_field, "like", "%测试%"]
                ], fields=["name", title_field])
                
                existing_names = [r["name"] for r in records]
                for tr in title_records:
                    if tr["name"] not in existing_names:
                        records.append(tr)
            
            if records:
                found_records[dt] = records
        except Exception:
            pass
            
    print(frappe.as_json(found_records))

if __name__ == "__main__":
    find_test_data()
