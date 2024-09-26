import frappe
from frappe.utils import nowdate

@frappe.whitelist()
def create_stock_reconciliation(items_data, posting_date, posting_time,station,docname):
    try:
        # Parse the JSON data for items (if passed as a string)
        items_data = frappe.parse_json(items_data)

        # Check if items data is valid
        if not items_data or len(items_data) == 0:
            frappe.throw("No items data provided for Stock Reconciliation")

        # Create a new Stock Reconciliation document
        stock_reconciliation = frappe.new_doc("Stock Reconciliation")
        stock_reconciliation.set_posting_time = 1
        stock_reconciliation.posting_date = posting_date  # Use provided posting date
        stock_reconciliation.posting_time = posting_time  # Use provided posting time
        stock_reconciliation.cost_center = station
        stock_reconciliation.custom_shift_closing = docname
       

        # Loop through the items data and add rows to stock reconciliation
        for item in items_data:
            item_code = item.get('item_code')
            warehouse = item.get('warehouse')
            qty = item.get('qty')

            # Check if the necessary fields are present
            if not item_code or not warehouse or qty is None:
                frappe.throw(f"Missing required fields for item {item_code}")

            # Add a row to the items child table
            stock_reconciliation.append("items", {
                "item_code": item_code,
                "warehouse": warehouse,
                "qty": qty,
                "valuation_rate": item.get("valuation_rate", 0)  # Optional: set valuation rate
            })

        # Save and submit the Stock Reconciliation
        stock_reconciliation.save()
        stock_reconciliation.submit()  # Uncomment this to automatically submit the document

        return {"status": "success", "message": f"Stock Reconciliation {stock_reconciliation.name} created successfully"}

    except Exception as e:
        # Log any error that occurs
        frappe.log_error(frappe.get_traceback(), "Stock Reconciliation Error")
        return {"status": "failed", "error": str(e)}
