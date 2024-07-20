import frappe

@frappe.whitelist()
def update_bank_deposits(docname, method=None):
    try:
        doc = frappe.get_doc("Payment Entry", docname)

        if method == "on_cancel":
            cancel_bank_deposits(doc)
            return

        posting_date = doc.posting_date

        # Check if there's an existing "Bank Deposits" document for the posting date and cost center
        bank_deposit_name = frappe.db.get_value("Bank Deposits", {"posting_date": posting_date, "station": doc.cost_center}, "name")
        if bank_deposit_name:
            bank_deposit = frappe.get_doc("Bank Deposits", bank_deposit_name)
        else:
            # Create a new "Bank Deposits" document
            bank_deposit = frappe.new_doc("Bank Deposits")
            bank_deposit.posting_date = posting_date
            bank_deposit.station = doc.cost_center
            bank_deposit.save()
            bank_deposit.submit()  # Submit the new document

        # Get all payment entries for the given posting date and cost center
        payment_entries = frappe.get_all("Payment Entry", filters={"posting_date": posting_date, "cost_center": doc.cost_center, "docstatus": ["!=", 2]}, fields=["name", "paid_to", "paid_amount", "docstatus"])

        for pe in payment_entries:
            account = frappe.get_doc("Account", pe.paid_to)
            if account.account_type == "Bank":
                account_exists = False
                for item in bank_deposit.items:
                    if item.bank == pe.paid_to:
                        if pe.docstatus == 2:  # If Payment Entry is cancelled
                            item.amount_banked -= pe.paid_amount
                        else:
                            item.amount_banked += pe.paid_amount
                        account_exists = True
                        break

                if not account_exists:
                    # Add new item for the bank account
                    bank_deposit.append("items", {
                        "bank": pe.paid_to,
                        "amount_banked": -pe.paid_amount if pe.docstatus == 2 else pe.paid_amount
                    })

        # Calculate total money banked
        total_money_banked = sum(item.amount_banked for item in bank_deposit.items if item.amount_banked > 0)
        bank_deposit.total_money_banked = total_money_banked

        # Save and submit the updated document
        bank_deposit.save()
        bank_deposit.custom_bank_deposits_status = "Deposits Made"
        if bank_deposit.docstatus == 1:
            bank_deposit.submit()

    except Exception as e:
        frappe.log_error(f"Error in update_bank_deposits: {e}")

def cancel_bank_deposits(doc):
    try:
        posting_date = doc.posting_date

        # Check if there's an existing "Bank Deposits" document for the posting date and cost center
        bank_deposit_name = frappe.db.get_value("Bank Deposits", {"posting_date": posting_date, "station": doc.cost_center}, "name")
        if bank_deposit_name:
            bank_deposit = frappe.get_doc("Bank Deposits", bank_deposit_name)

            # Check if the Payment Entry's paid_to account is of type "Bank"
            account = frappe.get_doc("Account", doc.paid_to)
            if account.account_type == "Bank":
                for item in bank_deposit.items:
                    if item.bank == doc.paid_to:
                        item.amount_banked -= doc.paid_amount
                        break

            # Calculate total money banked
            total_money_banked = sum(item.amount_banked for item in bank_deposit.items if item.amount_banked > 0)
            bank_deposit.total_money_banked = total_money_banked

            # Save the updated document
            bank_deposit.save()
            if bank_deposit.docstatus == 1:
                bank_deposit.submit()

    except Exception as e:
        frappe.log_error(f"Error in cancel_bank_deposits: {e}")

# Fetch all payment entries for a specific cost center and update bank deposits
def update_bank_deposits_for_cost_center(cost_center):
    payment_entries = frappe.get_all("Payment Entry", filters={"cost_center": cost_center, "docstatus": 1}, fields=["name", "posting_date", "cost_center", "paid_to", "paid_amount"])

    for pe in payment_entries:
        doc = frappe.get_doc("Payment Entry", pe.name)
        update_bank_deposits(doc.name)

# Example function to update bank deposits for a specific Payment Entry
@frappe.whitelist()
def update_bank_deposits_for_payment_entry(payment_entry_name):
    doc = frappe.get_doc("Payment Entry", payment_entry_name)
    update_bank_deposits_for_cost_center(doc.cost_center)

# Example usage:
# update_bank_deposits_for_payment_entry('PAYMENT-ENTRY-NAME')
