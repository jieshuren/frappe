import frappe

def run():
    parent = frappe.db.sql("""
        SELECT name, account_name, parent_account, is_group, account_type, account_number, lft, rgt, company
        FROM `tabAccount`
        WHERE account_name LIKE '%其他应付款%'
    """, as_dict=True)
    print("=== 其他应付款主科目 ===")
    for p in parent:
        print(p)

    for p in parent:
        if p.is_group:
            children = frappe.db.sql("""
                SELECT name, account_name, parent_account, is_group, account_type, account_number
                FROM `tabAccount`
                WHERE lft > %s AND rgt < %s AND company = %s
                ORDER BY lft
            """, (p.lft, p.rgt, p.company), as_dict=True)
            print(f"\n=== 子科目 of {p.name}（共 {len(children)} 条） ===")
            for c in children:
                print(f"  [{c.account_number or '-'}] {c.account_name} | is_group={c.is_group} | parent={c.parent_account}")
