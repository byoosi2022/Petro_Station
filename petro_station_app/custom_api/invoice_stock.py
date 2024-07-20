import frappe
from frappe import _

@frappe.whitelist()
def get_total_qty_and_amount(station, from_date, pump_or_tank_list, status=None):
    import json
    from datetime import datetime

    totals = {
        'warehouses': {},
        'grand_total': 0,
        'additional_discount_amount': 0,
        'outstanding_amount': 0,
        'total_payments': 0
    }

    # Convert pump_or_tank_list from JSON string to Python list if necessary
    if isinstance(pump_or_tank_list, str):
        pump_or_tank_list = json.loads(pump_or_tank_list)

    filters = {
        "docstatus": 1,
        "posting_date": from_date,
    }

    if status:
        filters["status"] = status

    sales_invoices = frappe.get_list(
        "Sales Invoice",
        filters=filters,
        fields=["name", "posting_date", "posting_time", "total", "discount_amount", "outstanding_amount"]
    )

    for invoice in sales_invoices:
        invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)

        # Ensure posting_time is in the correct string format before parsing
        posting_time_str = str(invoice_doc.posting_time)

        # Combine posting_date and posting_time to a single datetime
        invoice_posting_datetime = datetime.combine(invoice_doc.posting_date, datetime.strptime(posting_time_str, '%H:%M:%S').time())

        # Check if any item in the invoice has the specified cost_center
        has_matching_item = any(item.cost_center == station for item in invoice_doc.items)

        if has_matching_item:
            # Aggregate grand total and outstanding amount
            totals['grand_total'] += invoice_doc.total
            totals['outstanding_amount'] += invoice_doc.outstanding_amount

            # Aggregate additional discount amount only if outstanding amount is 0
            if invoice_doc.outstanding_amount < 50:
                totals['additional_discount_amount'] += invoice_doc.discount_amount

            # Aggregate total payments from related payment entries
            payment_entries = frappe.get_list(
                "Payment Entry",
                filters={"reference_name": invoice.name, "docstatus": 1},
                fields=["paid_amount"]
            )
            for payment in payment_entries:
                totals['total_payments'] += payment.paid_amount

        for item in invoice_doc.items:
            if item.cost_center == station and item.warehouse in pump_or_tank_list:
                if item.warehouse not in totals['warehouses']:
                    totals['warehouses'][item.warehouse] = {
                        'qty': 0,
                        'amount': 0,
                        'total_rate': 0,
                        'count': 0
                    }

                totals['warehouses'][item.warehouse]['qty'] += item.qty
                totals['warehouses'][item.warehouse]['amount'] += item.amount
                totals['warehouses'][item.warehouse]['total_rate'] += item.rate * item.qty
                totals['warehouses'][item.warehouse]['count'] += item.qty

    # Fetch stock entries with the same date filter
    stock_entries = frappe.get_list(
        "Stock Entry",
        filters={"stock_entry_type": "Material Transfer", "posting_date": from_date, "docstatus": 1},
        fields=["name"]
    )

    for stock_entry in stock_entries:
        stock_entry_doc = frappe.get_doc("Stock Entry", stock_entry.name)
        for item in stock_entry_doc.items:
            # Check if the source warehouse is of type pump and the cost center matches
            source_warehouse_doc = frappe.get_doc("Warehouse", item.s_warehouse)
            if source_warehouse_doc.warehouse_type == "Pump" and item.cost_center == station:
                if item.s_warehouse in pump_or_tank_list:
                    if item.s_warehouse not in totals['warehouses']:
                        totals['warehouses'][item.s_warehouse] = {
                            'qty': 0,
                            'amount': 0,
                            'total_rate': 0,
                            'count': 0
                        }

                    totals['warehouses'][item.s_warehouse]['qty'] += item.qty
                    totals['warehouses'][item.s_warehouse]['amount'] += item.amount
                    totals['warehouses'][item.s_warehouse]['total_rate'] += item.basic_rate * item.qty
                    totals['warehouses'][item.s_warehouse]['count'] += item.qty

                if item.t_warehouse in pump_or_tank_list:
                    if item.t_warehouse not in totals['warehouses']:
                        totals['warehouses'][item.t_warehouse] = {
                            'qty': 0,
                            'amount': 0,
                            'total_rate': 0,
                            'count': 0
                        }

                    totals['warehouses'][item.t_warehouse]['qty'] += item.qty
                    totals['warehouses'][item.t_warehouse]['amount'] += item.amount
                    totals['warehouses'][item.t_warehouse]['total_rate'] += item.basic_rate * item.qty
                    totals['warehouses'][item.t_warehouse]['count'] += item.qty

    # Calculate average rate
    for warehouse, data in totals['warehouses'].items():
        if data['count'] > 0:
            data['average_rate'] = data['total_rate'] / data['count']
        else:
            data['average_rate'] = 0

    return totals
