# import frappe

# @frappe.whitelist()
# def submit_sales_invoice(doc):
    
#     invoice_list = frappe.get_all("Sales Invoice", filters={"name": doc}, fields=["name"])
    
#     # Check if the Sales Invoice is in draft status
#     if invoice_list:
#         invoice_name = invoice_list[0]['name']
#         invoice = frappe.get_doc("Sales Invoice", invoice_name)
#         if invoice.docstatus == 0:  # Draft status
#             # Submit the Sales Invoice
#             invoice.submit()
#             print(f"Sales Invoice {doc} submitted successfully.")
#         else:
#             print(f"Sales Invoice {doc} is not in draft status.")
#     else:
#         print(f"Sales Invoice {doc} not found.")
        
# @frappe.whitelist()
# def before_submit(doc, method=None):
#     # Create a Sales Invoice
#     sales_invoice = frappe.new_doc("Fuel Sales App")
#     sales_invoice.customer = doc.customer
#     sales_invoice.discount_amount = doc.additional_discount_amount
#     sales_invoice.posting_date = doc.date
#     sales_invoice.due_date = doc.due_date
#     sales_invoice.selling_price_list = doc.price_list
#     sales_invoice.cost_center = doc.station
#     sales_invoice.update_stock = 1  # Correct field name for updating stock

#     # Add items to the Sales Invoice
#     for item in doc.items:
#         item_group = frappe.get_value("Item", item.item_code, "item_group")
#         if item_group == "Fuel":
#             sales_invoice.append("items", {
#                 "item_code": item.item_code,
#                 "qty": item.qty,
#                 "rate": item.rate,
#                 "warehouse": item.warehouse,
#                 "amount": item.amount
#             })

#     # Save and submit the Sales Invoice
#     if sales_invoice.items:
#         sales_invoice.insert()
#         sales_invoice.submit()
#         frappe.db.commit()

#         # Create Payment Entry for each POS Profile and item
#         if doc.include_payments:
#             for item in doc.items:
#                 pos_profile = item.pos_profile
#                 payment_methods = frappe.get_all("POS Payment Method", filters={"parent": pos_profile},
#                                                  fields=["mode_of_payment"])
#                 for payment_method in payment_methods:
#                     mode_of_payment = payment_method.mode_of_payment
#                     mode_of_pay_doc = frappe.get_doc("Mode of Payment", mode_of_payment)
#                     default_account = mode_of_pay_doc.accounts[0].default_account
#                     currency = frappe.db.get_value("Account", default_account, "account_currency")
#                     payment_entry = frappe.new_doc("Payment Entry")
#                     payment_entry.party_type = "Customer"
#                     payment_entry.payment_type = "Receive"
#                     payment_entry.party = doc.customer
#                     payment_entry.paid_amount = item.amount  # Assuming amount is correct for each item
#                     payment_entry.received_amount = item.amount
#                     payment_entry.target_exchange_rate = 1.0
#                     payment_entry.paid_to = default_account
#                     payment_entry.paid_to_account_currency = currency
#                     payment_entry.mode_of_payment = mode_of_payment
#                     payment_entry.append("references", {
#                         "reference_doctype": "Sales Invoice",
#                         "reference_name": sales_invoice.name,
#                         "allocated_amount": item.amount
#                     })
#                     frappe.msgprint(_(f"Payments Made for invoice {sales_invoice.name}"))
#                     payment_entry.insert()
#                     payment_entry.submit()
#                     frappe.db.commit()

#     # Update the Sales Invoice with the created Payment Entries
#     doc.sales_invoice_created = sales_invoice.name
