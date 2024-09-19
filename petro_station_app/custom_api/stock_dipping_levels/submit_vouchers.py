import frappe

@frappe.whitelist()
def submit_draft_stock_entries(voucher_list):
    try:
        # Parse the JSON data for vouchers (if passed as a string)
        voucher_list = frappe.parse_json(voucher_list)

        # Check if voucher data is valid
        if not voucher_list or len(voucher_list) == 0:
            frappe.throw("No voucher data provided for submission")

        submitted_vouchers = []

        # Loop through the voucher list and submit each stock entry
        for voucher in voucher_list:
            stock_entry = frappe.get_doc("Stock Entry", voucher)

            # Check if the stock entry is in Draft status
            if stock_entry.docstatus == 0:  # Draft status
                stock_entry.submit()  # Submit the stock entry
                submitted_vouchers.append(stock_entry.name)
            else:
                frappe.msgprint(f"Stock Entry {voucher} is not in Draft status and cannot be submitted.")

        return {
            "status": "success",
            "message": f"Successfully submitted the following stock entries: {', '.join(submitted_vouchers)}"
        }

    except Exception as e:
        # Log any error that occurs
        frappe.log_error(frappe.get_traceback(), "Stock Entry Submission Error")
        return {"status": "failed", "error": str(e)}
