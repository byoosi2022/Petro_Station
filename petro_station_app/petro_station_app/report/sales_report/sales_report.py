# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt
import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Dynamic Link", "options": "Item", "width": 150},
        # {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": _("Pumb"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": _("Litres"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("View Invoices"), "fieldname": "_view_invoices", "fieldtype": "Data", "width": 120},
    ]
    
    conditions = ""
    values = {}
    
    if filters:
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
        if filters.get("warehouse"):
            conditions += " AND sii.warehouse = %(warehouse)s"
            values["warehouse"] = filters["warehouse"]
    
    data = frappe.db.sql(f"""
        SELECT
            sii.item_code, sii.cost_center, sii.warehouse,
            SUM(sii.qty) as total_qty,
            SUM(sii.amount) as total_amount
        FROM
            `tabSales Invoice` si
        JOIN
            `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN
            `tabItem` i ON sii.item_code = i.name
        WHERE
            si.docstatus = 1
            AND i.item_group = 'Fuel'
            {conditions}
        GROUP BY
            sii.item_code, sii.cost_center, sii.warehouse
        ORDER BY
            sii.item_code
    """, values, as_dict=1)
    
    for item in data:
        cost_center_filter = filters.get("cost_center", "")
        item["_view_invoices"] = f'<a href="/app/query-report/Item%20Wise%20Sales%20Report?cost_center={cost_center_filter}&from_date={filters["from_date"]}&to_date={filters["to_date"]}&item_code={item["item_code"]}">View Details</a>'
    
    return columns, data
