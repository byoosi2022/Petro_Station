import frappe
from frappe import _

@frappe.whitelist()
def get_sales_invoices_with_totals(cost_center=None, posting_date=None):
    try:
        # Log filter criteria
        frappe.logger().info(f"Fetching sales invoices for cost center: {cost_center} and posting date: {posting_date}")

        # Check if cost_center or posting_date is None
        filters = {"docstatus": 1}
        if cost_center:
            filters["cost_center"] = cost_center
        if posting_date:
            filters["posting_date"] = posting_date

        # Fetch sales invoices with specified fields
        sales_invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=["name", "posting_date", "customer_name","customer","grand_total", "additional_discount_account", "outstanding_amount", "cost_center"]
        )

        # Log fetched sales invoices
        frappe.logger().info(f"Fetched {len(sales_invoices)} sales invoices")

        if not sales_invoices:
            frappe.logger().info("No sales invoices found with the given filters")
            return {
                "Invoices": [],
                "Total Grand Total": 0,
                "Total Outstanding Amount": 0,
                "Total Additional Discount": 0,
                "Total Quantity": 0
            }

        # Initialize totals
        total_grand_total = 0
        total_outstanding_amount = 0
        total_additional_discount = 0
        total_qty = 0

        # Dictionary to store aggregated invoice details
        invoices_dict = {}

        # Iterate over the fetched sales invoices
        for invoice in sales_invoices:
            # Check if invoice already exists in invoices_dict based on name
            if invoice["name"] not in invoices_dict:
                # Initialize invoice details
                invoice_details = {
                    "Invoice Name": invoice["name"],
                    "Posting Date": invoice["posting_date"],
                    "Customer Name": invoice["customer_name"],
                    "Customer": invoice["customer"],
                    "Total Amount": invoice["grand_total"],
                    "Additional Discount Account (UGX)": invoice["additional_discount_account"],
                    "Outstanding Amount (UGX)": invoice["outstanding_amount"],
                    "Cost Center": invoice["cost_center"],
                    "Items": []
                }

                # Add invoice details to invoices_dict
                invoices_dict[invoice["name"]] = invoice_details

            # Fetch items for each invoice
            items = frappe.get_all(
                "Sales Invoice Item",
                filters={"parent": invoice["name"]},
                fields=["item_code", "item_name", "qty", "rate", "amount", "discount_amount", "cost_center"]
            )

            # Log fetched items
            frappe.logger().info(f"Fetched {len(items)} items for invoice {invoice['name']}")

            # Dictionary to aggregate items by item code and cost center
            aggregated_items = {}

            # Aggregate items by item code and cost center
            for item in items:
                key = (item["item_code"], item["cost_center"])
                if key not in aggregated_items:
                    aggregated_items[key] = {
                        "Item Code": item["item_code"],
                        "Item Name": item["item_name"],
                        "Quantity": item["qty"],
                        "Rate": item["rate"],
                        "Amount": item["amount"],
                        "Discount Amount": item.get("discount_amount", 0),  # Handle missing key gracefully
                        "Cost Center": item["cost_center"]
                    }
                else:
                    # If item exists, accumulate quantities and amounts
                    aggregated_items[key]["Quantity"] += item["qty"]
                    aggregated_items[key]["Amount"] += item["amount"]

            # Append aggregated items to invoice details
            invoices_dict[invoice["name"]]["Items"].extend(list(aggregated_items.values()))

            # Calculate totals for the invoice
            for agg_item in aggregated_items.values():
                total_qty += agg_item["Quantity"]
                total_additional_discount += agg_item.get("discount_amount", 0)  # Handle missing key gracefully

            # Add invoice amounts to totals
            total_grand_total += invoice["grand_total"]
            total_outstanding_amount += invoice["outstanding_amount"]

        # Convert invoices_dict to a list of values
        invoices_list = list(invoices_dict.values())

        # Add totals to the response
        result = {
            "Invoices": invoices_list,
            "Total Grand Total": total_grand_total,
            "Total Outstanding Amount": total_outstanding_amount,
            "Total Additional Discount": total_additional_discount,
            "Total Quantity": total_qty
        }

        # Log final result
        frappe.logger().info(f"Final result: {result}")

        # Return the list of invoices with items and totals
        return result

    except Exception as e:
        frappe.throw(_("An error occurred while fetching sales invoices: {}").format(str(e)))

@frappe.whitelist()
def get_cash_transfers_with_totals(cost_center=None, posting_date=None):
    try:
          # Check if cost_center or posting_date is None
        filters = {"docstatus": 1}
        if cost_center:
            filters["station"] = cost_center
        if posting_date:
            filters["posting_date"] = posting_date

        # Fetch sales invoices with specified fields
        cash_transfers = frappe.get_all(
            "Transfer Cash",
            filters=filters,
            fields=["name", "posting_date", "account_paid_from","paid_amount","account_paid_to", "reference_date", "station"]
        )


        if not cash_transfers:
            frappe.logger().info("No sales invoices found with the given filters")
            return {
                "Paid Amount": 0,
                        }

        # Initialize totals
        total_paid_amount = 0
         # Dictionary to store aggregated invoice details
        transfers_dict = {}

        # Iterate over the fetched sales invoices
        for cash in cash_transfers:
            # Check if invoice already exists in invoices_dict based on name
            if cash["name"] not in transfers_dict:
                # Initialize invoice details
                cash_details = {
                    "Transfer Name": cash["name"],
                    "Posting Date": cash["posting_date"],
                    "Paid To": cash["account_paid_to"],
                    "Paid From": cash["account_paid_from"],
                    "Paid Amount": cash["paid_amount"],
                    "Cost Center": cash["station"],
                
                }

                # Add invoice details to invoices_dict
                transfers_dict[cash["name"]] = cash_details
 
            total_paid_amount += cash["paid_amount"]
       
        # Convert invoices_dict to a list of values
        transfer_list = list(transfers_dict.values())

        # Add totals to the response
        result = {
            "Transfers": transfer_list,
            "Paid Amount": total_paid_amount,
        }

        # Log final result
        frappe.logger().info(f"Final result: {result}")

        # Return the list of invoices with items and totals
        return result

    except Exception as e:
        frappe.throw(_("An error occurred while fetching sales invoices: {}").format(str(e)))

@frappe.whitelist()
def get_expenses_with_totals(cost_center=None, posting_date=None):
    try:
        # Check if cost_center or posting_date is None
        filters = {"docstatus": 1, "grand_total": [">", 0]}
        if cost_center:
            filters["station"] = cost_center
        if posting_date:
            filters["date"] = posting_date

        # Fetch sales invoices with specified fields
        expenditures = frappe.get_all(
            "Fuel Sales App",
            filters=filters,
            fields=["name", "date", "station", "grand_total"]
        )

        if not expenditures:
            frappe.logger().info("No sales invoices found with the given filters")
            return {
                "Grand Total": 0,
            }

        # Initialize totals
        total_grand_amount = 0
        # Dictionary to store aggregated invoice details
        expense_dict = {}

        # Iterate over the fetched sales invoices
        for expense in expenditures:
            # Check if invoice already exists in invoices_dict based on name
            if expense["name"] not in expense_dict:
                # Initialize invoice details
                expense_details = {
                    "Expense Name": expense["name"],
                    "Posting Date": expense["date"],
                    "Grand Total": expense["grand_total"],
                }

                # Add invoice details to invoices_dict
                expense_dict[expense["name"]] = expense_details

            total_grand_amount += expense["grand_total"]

        # Convert invoices_dict to a list of values
        expense_list = list(expense_dict.values())

        # Add totals to the response
        result = {
            "Expenses": expense_list,
            "Grand Total": total_grand_amount,
        }

        # Log final result
        frappe.logger().info(f"Final result: {result}")

        # Return the list of invoices with items and totals
        return result

    except Exception as e:
        frappe.throw(_("An error occurred while fetching sales invoices: {}").format(str(e)))

@frappe.whitelist()
def get_expense_totals(cost_center=None, posting_date=None):
    try:
        # Check if cost_center or posting_date is None
        filters = {"docstatus": 1}
        if cost_center:
            filters["station"] = cost_center
        if posting_date:
            filters["date"] = posting_date

        # Fetch sales invoices with specified fields
        expenses = frappe.get_all(
            "Fuel Sales App",
            filters=filters,
            fields=["name", "date", "station", "grand_total"]
        )

        if not expenses:
            frappe.logger().info("No sales invoices found with the given filters")
            return {
                "Total Grand Total": 0,
                "Total Amount": 0,
            }

        # Initialize totals
        total_grand_total = 0
        total_amount = 0

        # Dictionary to store aggregated expense details
        expenses_dict = {}

        # Iterate over the fetched sales invoices
        for expense in expenses:
            # Check if expense already exists in expenses_dict based on name
            if expense["name"] not in expenses_dict:
                # Initialize expense details
                expense_details = {
                    "Expense Name": expense["name"],
                    "Posting Date": expense["date"],
                    "Grand Total": expense["grand_total"],
                    "Items": []
                }

                # Add expense details to expenses_dict
                expenses_dict[expense["name"]] = expense_details

            # Fetch items for each expense
            items = frappe.get_all(
                "Expense Claim Items",
                filters={"parent": expense["name"]},
                fields=["description", "party", "amount", "claim_type"]
            )

            # Dictionary to aggregate items by claim type
            aggregated_items = {}

            # Aggregate items by claim type
            for item in items:
                key = item["claim_type"]
                if key not in aggregated_items:
                    aggregated_items[key] = {
                        "Description": item["description"],
                        "Party": item["party"],
                        "Claim Type": item["claim_type"],
                        "Amount": item["amount"],
                    }
                else:
                    aggregated_items[key]["Amount"] += item["amount"]

            # Append aggregated items to expense details
            expenses_dict[expense["name"]]["Items"].extend(list(aggregated_items.values()))

            # Add expense amounts to totals
            total_grand_total += expense["grand_total"]
            for agg_item in aggregated_items.values():
                total_amount += agg_item["Amount"]

        # Convert expenses_dict to a list of values
        expenses_list = list(expenses_dict.values())

        # Add totals to the response
        result = {
            "Expenses": expenses_list,
            "Total Grand Total": total_grand_total,
            "Total Amount": total_amount
        }

        # Log final result
        frappe.logger().info(f"Final result: {result}")

        # Return the list of expenses with items and totals
        return result

    except Exception as e:
        frappe.throw(_("An error occurred while fetching expenses: {}").format(str(e)))
