import frappe
from frappe.utils import today

def update_bank_deposits(doc, method):
    try:
        # Handle cancellation of bank deposits
        if method == "on_cancel":
            cancel_bank_deposits(doc)
            return
        
        posting_date = doc.posting_date

        # Check if there's an existing "Bank Deposits" document for the posting date
        bank_deposit_name = frappe.db.get_value("Bank Deposits", {"posting_date": posting_date}, "name")
        if bank_deposit_name:
            bank_deposit = frappe.get_doc("Bank Deposits", bank_deposit_name)
        else:
            # Create a new "Bank Deposits" document
            bank_deposit = frappe.new_doc("Bank Deposits")
            bank_deposit.posting_date = posting_date
            bank_deposit.station = doc.cost_center
            bank_deposit.save()
            bank_deposit.submit()  # Submit the new document

        # Check if the Payment Entry's paid_to account is of type "Bank"
        account = frappe.get_doc("Account", doc.paid_to)
        if account.account_type == "Bank":
            # Check if the account already exists in the items table
            account_exists = False
            for item in bank_deposit.items:
                if item.bank == doc.paid_to:
                    if doc.docstatus == 2:  # If Payment Entry is cancelled
                        item.amount_banked -= doc.paid_amount
                    else:
                        item.amount_banked += doc.paid_amount
                    account_exists = True
                    break

            if not account_exists:
                # Add new item for the bank account
                new_item = bank_deposit.append("items", {
                    "bank": doc.paid_to,
                    "amount_banked": -doc.paid_amount if doc.docstatus == 2 else doc.paid_amount
                })

        # Calculate total money banked
        total_money_banked = sum(item.amount_banked for item in bank_deposit.items if item.amount_banked > 0)
        bank_deposit.total_money_banked = total_money_banked

        # Save and submit the updated document
        bank_deposit.save()
        if bank_deposit.docstatus == 1:
            bank_deposit.submit()

    except Exception as e:
        frappe.log_error(f"Error in update_bank_deposits: {e}")

def cancel_bank_deposits(doc, method=None):
    try:
        posting_date = doc.posting_date

        # Check if there's an existing "Bank Deposits" document for the posting date
        bank_deposit_name = frappe.db.get_value("Bank Deposits", {"posting_date": posting_date}, "name")
        if bank_deposit_name:
            bank_deposit = frappe.get_doc("Bank Deposits", bank_deposit_name)

            account = frappe.get_doc("Account", doc.paid_to)
            if account.account_type == "Bank":
                # Check if the account already exists in the items table
                for item in bank_deposit.items:
                    if item.bank == doc.paid_to:
                        item.amount_banked -= doc.paid_amount

            # Calculate total money banked
            total_money_banked = sum(item.amount_banked for item in bank_deposit.items if item.amount_banked > 0)
            bank_deposit.total_money_banked = total_money_banked

            # Save and submit the updated document
            bank_deposit.save()
            if bank_deposit.docstatus == 1:
                bank_deposit.submit()

    except Exception as e:
        frappe.log_error(f"Error in cancel_bank_deposits: {e}")
