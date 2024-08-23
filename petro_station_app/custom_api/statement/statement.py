import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_sales_invoice_details_and_payments(customer, from_date, to_date):
    sales_invoice_data = []
    total_paid_amount = 0
    grand_total_amount = 0  # Variable to hold the grand total of all amounts
    running_balance = 0      # Variable to hold the running balance

    # Step 1: Fetch Sales Invoices and their items for the specified customer and date range
    invoices = frappe.db.sql("""
        SELECT 
            si.name AS invoice_name,
            si.custom_fuel_sales_app_id AS sales_app_id,
            si.custom_credit_sales_app AS credit_sales_id,
            si.posting_date,
            si.cost_center, 
            sii.item_code, 
            sii.custom_vehicle_plates, 
            sii.qty, 
            sii.rate, 
            sii.amount
        FROM 
            `tabSales Invoice` si
        JOIN 
            `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE 
            si.customer = %s 
            AND si.posting_date BETWEEN %s AND %s 
            AND si.docstatus = 1
    """, (customer, from_date, to_date), as_dict=True)

    for invoice in invoices:
        # Calculate the total amount for each invoice
        total_amount = flt(invoice.amount)
        grand_total_amount += total_amount  # Add to grand total
        
        # Calculate running balance
        running_balance += total_amount
        
        invoice_data = {
            "invoice_name": invoice.invoice_name,
            "cost_center":invoice.cost_center,
            "sales_app_id": invoice.sales_app_id,
            "credit_sales_id": invoice.credit_sales_id,
            "posting_date": invoice.posting_date,  # Add posting date to the invoice data
            "item_code": invoice.item_code,
            "custom_vehicle_plates": invoice.custom_vehicle_plates,
            "qty": flt(invoice.qty),
            "rate": flt(invoice.rate),
            "amount": total_amount,
            "running_balance": running_balance  # Include running balance for each invoice
        }
        
        # Add invoice data to the list
        sales_invoice_data.append(invoice_data)

    # Step 2: Fetch Payment Entries within the specified date range for the same customer
    payments = frappe.db.sql("""
        SELECT 
            pe.name AS payment_entry_name, 
            pe.posting_date,
            pe.cost_center, 
            pe.paid_amount
        FROM 
            `tabPayment Entry` pe
        WHERE 
            pe.party_type = 'Customer'
            AND pe.party = %s
            AND pe.posting_date BETWEEN %s AND %s
            AND pe.docstatus = 1
    """, (customer, from_date, to_date), as_dict=True)

    filtered_payments = []
    for payment in payments:
        total_paid_amount += flt(payment.paid_amount)
        running_balance -= flt(payment.paid_amount)  # Subtract payment from running balance
        filtered_payments.append({
            "payment_entry_name": payment.payment_entry_name,
            "cost_center":payment.cost_center,
            "posting_date": payment.posting_date,  # Include posting date for payments
            "paid_amount": payment.paid_amount
        })

    # Step 3: Fetch GL Entries for the customer where voucher type is Journal Entry
    gl_entries = frappe.db.sql("""
        SELECT
            gle.name AS gl_entry_name,
            gle.posting_date,
            gle.cost_center,
            gle.debit,
            gle.voucher_no,
            gle.credit,
            gle.remarks
        FROM
            `tabGL Entry` gle
        WHERE
            gle.party_type = 'Customer'
            AND gle.party = %s
            AND gle.voucher_type = 'Journal Entry'
            AND gle.posting_date BETWEEN %s AND %s
            AND gle.docstatus = 1
    """, (customer, from_date, to_date), as_dict=True)

    filtered_gl_entries = []
    for gl_entry in gl_entries:
        filtered_gl_entries.append({
            "gl_entry_name": gl_entry.gl_entry_name,
            "posting_date": gl_entry.posting_date,
            "cost_center":gl_entry.cost_center,
            "voucher_no": gl_entry.voucher_no,
            "debit": flt(gl_entry.debit),
            "credit": flt(gl_entry.credit),
            "remarks": gl_entry.remarks
        })

        # Update running balance: add debit amounts and credit amounts
        running_balance += flt(gl_entry.debit)  # Add debit to running balance
        total_paid_amount += flt(gl_entry.credit)  # Add credit to total paid

    # Update grand total amount calculation
    grand_total_amount += sum(flt(invoice.amount) for invoice in invoices)
    
    # Calculate outstanding amount
    outstanding_amount = grand_total_amount - total_paid_amount

    # Update running balance in each invoice data for consistency
    for invoice in sales_invoice_data:
        invoice["running_balance"] = running_balance

    return {
        "sales_invoice_data": sales_invoice_data,
        "grand_total_amount": grand_total_amount,  # Return grand total of all amounts
        "total_paid_amount": total_paid_amount,
        "outstanding_amount": outstanding_amount,  # Return outstanding amount
        "payments": filtered_payments,  # Include filtered payment details in the result
        "gl_entries": filtered_gl_entries  # Include filtered GL entries in the result
    }
