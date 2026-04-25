import frappe

cat = frappe.get_doc("Account Category", "现金及现金等价物")
print(f"名称: {cat.name}")
print(f"描述: {cat.description}")
print("---")

cat2 = frappe.get_doc("Account Category", "应收账款")
print(f"名称: {cat2.name}")
print(f"描述: {cat2.description}")
