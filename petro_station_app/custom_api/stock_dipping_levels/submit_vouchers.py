import frappe
from frappe.utils import nowdate, nowtime

@frappe.whitelist()
def submit_draft_stock_entries(voucher_list,docname):
    try:
        # Parse the JSON data for vouchers (if passed as a string)
        voucher_list = frappe.parse_json(voucher_list)

        # Check if voucher data is valid
        if not voucher_list or len(voucher_list) == 0:
            frappe.throw("No voucher data provided for submission")

        submitted_vouchers = []
        errors = []

        # Loop through the voucher list and attempt to submit each stock entry
        for voucher_data in voucher_list:
            try:
                voucher = voucher_data.get('voucher')            # Extract the voucher number
                received_date = voucher_data.get('received_date')  # Extract the received date
                time = voucher_data.get('time_recieved')          # Extract the time

                stock_entry = frappe.get_doc("Stock Entry", voucher)

                # Check if the stock entry is in Draft status
                if stock_entry.docstatus == 0:  # Draft status
                    # Check item availability in the specified warehouse
                    for item in stock_entry.items:  # Loop through items in stock entry
                        warehouse = item.s_warehouse  # Source warehouse
                        item_code = item.item_code
                        required_qty = item.qty  # Quantity needed
                        
                        # Check stock balance in the warehouse
                        stock_balance = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0

                        if stock_balance < required_qty:
                            errors.append(f"Failed to submit Stock Entry {voucher}: {required_qty} units of Item {item_code} needed in Warehouse {warehouse} to complete this transaction.")
                            break  # No need to check further if one item fails

                    if errors:
                        continue  # Skip submission if errors exist

                    # Update the posting date and posting time with received_date and time
                    stock_entry.posting_date = received_date  # Set the posting date to the received date
                    stock_entry.posting_time = time            # Set the posting time to the provided time
                    stock_entry.custom_shift_closing = docname 

                    # Submit the stock entry
                    stock_entry.submit()
                    submitted_vouchers.append(stock_entry.name)
                else:
                    errors.append(f"Stock Entry {voucher} is not in Draft status and cannot be submitted.")

            except Exception as e:
                # Log error specific to this stock entry
                frappe.log_error(frappe.get_traceback(), f"Error with Stock Entry {voucher}")
                errors.append(f"Failed to submit Stock Entry {voucher}: {str(e)}")

        if errors:
            # If there are any errors, raise an exception to prevent submission
            frappe.throw("\n".join(errors))

        return {
            "status": "success",
            "message": f"Successfully submitted the following stock entries: {', '.join(submitted_vouchers)}"
        }

    except Exception as e:
        # Log any error that occurs
        frappe.log_error(frappe.get_traceback(), "Stock Entry Submission Error")
        return {"status": "failed", "error": str(e)}
