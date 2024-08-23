import frappe  # type: ignore
from frappe import _  # type: ignore

@frappe.whitelist()
def update_vehicle_number(from_date, to_date, target_cost_center=None):
    # Prepare the filters for fetching Sales Invoices
    filters = {
        "posting_date": ["between", [from_date, to_date]],
        "docstatus": ["!=", 2],  # Exclude canceled invoices
        "custom_plate_staus": ["!=", "Remarks Set"]  # Exclude invoices with Remarks Set
    }
    
    # If a target cost center is provided, add it to the filters
    if target_cost_center:
        filters["cost_center"] = target_cost_center
    
    # Fetch all Sales Invoices that match the filters
    sales_invoices = frappe.get_all("Sales Invoice", 
                                    filters=filters, 
                                    fields=["name"])
    
    for invoice in sales_invoices:
        sales_invoice = frappe.get_doc("Sales Invoice", invoice.name)
        
        # Clear the existing remarks
        sales_invoice.remarks = ""

        # Check if the Sales Invoice is linked to any canceled document
        try:
            # Flag to check if any items match the criteria
            item_found = False

            for item in sales_invoice.items:
                if item.custom_vehicle_plates:
                    # Append each item's details to the remarks string
                    sales_invoice.remarks += f"Item: {item.item_code}, Quantity: {item.qty}, Amount: {item.amount}, Vehicle Plate: {item.custom_vehicle_plates}\n"
                    item_found = True
            
            # If any item matched, save the Sales Invoice with the updated remarks
            if item_found:
                # Set the custom_plate_status to "Remarks Set"
                sales_invoice.custom_plate_staus = "Remarks Set"
                sales_invoice.save()
                frappe.db.commit()
        except frappe.CancelledLinkError as e:
            # Log or handle the canceled link error appropriately
            frappe.log_error(message=str(e), title="Cancelled Link Error in update_vehicle_number")
            continue  # Skip this invoice and move to the next one
    
    return "Process completed."
