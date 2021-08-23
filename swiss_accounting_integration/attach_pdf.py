import frappe


@frappe.whitelist()
def attach_pdf(**kwargs):
    kwargs = frappe._dict(**kwargs)
    print(kwargs)
    return {
        "done": True
    }
