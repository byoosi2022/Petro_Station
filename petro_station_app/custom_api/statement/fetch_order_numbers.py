import frappe

@frappe.whitelist()
def fetch_order_numbers(statement_name):
    # Fetch credit_sales_id from the child table (Statement Details) linked to the Statement
    statement_details = frappe.get_all(
        "Invoice Table Statement",  # Assuming this is the child table name
        filters={"parent": statement_name},  # Filter based on the parent (Statement)
        fields=["credit_sales_id"]  # Only fetch the credit_sales_id field
    )
    
    # Initialize an empty result list
    result = []

    # Loop through each statement detail (child table record)
    for detail in statement_details:
        credit_sales_id = detail.get("credit_sales_id")
        
        if credit_sales_id:
            # Fetch the Fuel Sales document where the name matches the credit_sales_id
            fuel_sales = frappe.get_doc("Credit Sales App", credit_sales_id)

            # Loop through the items in the Fuel Sales document
            for item in fuel_sales.items:
                # Add only the order number to the result list
                result.append(item.order_number)

    # Return the list of order numbers
    return result

import frappe
@frappe.whitelist()
def fetch_discount(statement_name):
    # Fetch necessary fields from the child table (Statement Details) linked to the Statement
    discount_details = frappe.get_all(
        "Invoice Table Statement",  # Assuming this is the child table name
        filters={"parent": statement_name},  # Filter based on the parent (Statement)
        fields=['name', 'invoice_vourcher']
    )
    
    # Initialize an empty result list
    invoice_sales = []

    # Loop through each statement detail (child table record)
    for detail in discount_details:
        sales_invoice_id = detail.get("invoice_vourcher")
        
        if sales_invoice_id:
            # Fetch the Sales Invoice document where the name matches the invoice_vourcher
            invoice_doc = frappe.get_doc("Sales Invoice", sales_invoice_id)

            # Append the necessary invoice information to the result list
            invoice_sales.append({
              "additional_discount_amount": invoice_doc.discount_amount
            })

    # Return the list of invoice sales
    return invoice_sales


