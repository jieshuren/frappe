import frappe

cats = frappe.get_all("Account Category", fields=["name", "description"])
print(f"科目类别总数: {len(cats)}")
print("=" * 80)

for cat in sorted(cats, key=lambda x: x["name"]):
    print(f"\n名称: {cat['name']}")
    print(f"描述: {cat.get('description', '无')}")
    print("-" * 80)
