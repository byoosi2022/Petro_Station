# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe

# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Invoice"), "fieldname": "invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Litres"), "fieldname": "quantity", "fieldtype": "Float", "width": 100},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
    ]
    
    conditions = ""
    values = {}
    
    if filters and filters.get("item_code"):
        conditions += " AND sii.item_code = %(item_code)s"
        values["item_code"] = filters["item_code"]
        
    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]
    if filters.get("customer"):
        conditions += " AND si.customer = %(customer)s"
        values["customer"] = filters["customer"]
    if filters.get("cost_center"):
        conditions += " AND sii.cost_center = %(cost_center)s"
        values["cost_center"] = filters["cost_center"]
    
    data = frappe.db.sql(f"""
        SELECT
            sii.item_code, si.name as invoice, si.posting_date, si.customer, sii.cost_center,
            sii.qty as quantity, sii.amount
        FROM
            `tabSales Invoice` si
        JOIN
            `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE
            si.docstatus = 1
            {conditions}
        ORDER BY
            si.posting_date DESC
    """, values, as_dict=1)
    
    return columns, data
