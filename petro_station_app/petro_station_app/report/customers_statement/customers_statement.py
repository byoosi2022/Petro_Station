# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    # Define the columns for the report
    columns = [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Dynamic Link", "options": "Item", "width": 150},
        {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": _("Litres"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 100},
        {"label": _("Total Amount"), "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Invoice Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Payment Posting Date"), "fieldname": "payment_posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Vehicle No"), "fieldname": "custom_vehicle_plates", "fieldtype": "Data", "width": 150},
        {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
        {"label": _("Paid Amount"), "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Voucher Type"), "fieldname": "voucher_type", "fieldtype": "Data", "width": 120},
        {"label": _("Running Balance"), "fieldname": "running_balance", "fieldtype": "Currency", "width": 120},
        {"label": _("Opening Balance"), "fieldname": "opening_balance", "fieldtype": "Currency", "width": 120},
        {"label": _("Closing Balance"), "fieldname": "closing_balance", "fieldtype": "Currency", "width": 120},
    ]
    
    # Initialize conditions and values
    conditions = ""
    values = {}
    
    # Apply filters if present
    if filters:
        if filters.get("from_date"):
            conditions += " AND si.posting_date >= %(from_date)s"
            conditions += " AND pe.posting_date >= %(from_date)s"  # For payment date
            values["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            conditions += " AND si.posting_date <= %(to_date)s"
            conditions += " AND pe.posting_date <= %(to_date)s"  # For payment date
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

    # Fetch data from the database
    data = frappe.db.sql(f"""
        SELECT
            sii.item_code,
            sii.cost_center,
            sii.warehouse,
            sii.qty AS total_qty,
            sii.rate,
            sii.amount AS total_amount,
            si.posting_date AS posting_date,
            pe.posting_date AS payment_posting_date,
            sii.custom_vehicle_plates,
            si.grand_total,
            IFNULL(pe.paid_amount, 0) AS paid_amount,
            CASE 
                WHEN IFNULL(pe.paid_amount, 0) > 0 THEN 'Payment Entry'
                ELSE 'Sales Invoice'
            END AS voucher_type,
            (si.grand_total - IFNULL(pe.paid_amount, 0)) AS running_balance,
            (SELECT IFNULL(SUM(grand_total), 0) 
             FROM `tabSales Invoice` 
             WHERE customer = si.customer AND posting_date < si.posting_date) AS opening_balance,
            (SELECT IFNULL(SUM(grand_total), 0) 
             FROM `tabSales Invoice` si2 
             WHERE si2.customer = si.customer AND si2.posting_date <= si.posting_date) - IFNULL(pe.paid_amount, 0) AS closing_balance
        FROM
            `tabSales Invoice` si
        JOIN
            `tabSales Invoice Item` sii ON si.name = sii.parent
        JOIN
            `tabItem` i ON sii.item_code = i.item_code
        LEFT JOIN
            `tabPayment Entry` pe ON pe.party = si.customer AND pe.party_type = 'Customer'
        WHERE
            i.item_group = 'Fuel'
            {conditions}
        ORDER BY
            si.posting_date, sii.item_code
    """, values, as_dict=1)

    # Clean the data to show payment details only where applicable
    cleaned_data = []
    previous_payment_entry = None

    for row in data:
        cleaned_row = row.copy()

        # Adjust payment details visibility
        if row['paid_amount'] == 0 or (previous_payment_entry == row['payment_posting_date']):
            cleaned_row['payment_posting_date'] = None
            cleaned_row['paid_amount'] = None
            cleaned_row['voucher_type'] = None
        else:
            previous_payment_entry = row['payment_posting_date']

        cleaned_data.append(cleaned_row)

    return columns, cleaned_data
