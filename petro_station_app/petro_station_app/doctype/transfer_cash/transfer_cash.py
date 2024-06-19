# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _


class TransferCash(Document):
    def validate(self):
        # Ensure the accounts are different
        if self.account_paid_from == self.account_paid_to:
            frappe.throw(_("Account Paid From and Account Paid To must be different"))

    def on_submit(self):
        # Create a new Payment Entry document
        payment_entry = frappe.new_doc("Payment Entry")
        payment_entry.payment_type = "Internal Transfer"
        payment_entry.posting_date = self.posting_date
        payment_entry.paid_from = self.account_paid_from 
        payment_entry.paid_to = self.account_paid_to
        payment_entry.reference_no = self.reference_no
        payment_entry.reference_date = self.reference_date
        payment_entry.paid_amount = self.paid_amount
        payment_entry.received_amount = self.paid_amount
             
        # Save and submit the Payment Entry
        payment_entry.insert()
        payment_entry.submit()
        self.transfer_id = payment_entry.name
        frappe.msgprint(_(f"Cash Transer {payment_entry.name} createrd for {self.name} Successfully"))
        self.db_set("transfer_id", payment_entry.name)
        
        # Return the payment entry name
        return payment_entry.name
    
    def on_cancel(self):
        # Get the payment entry linked to this transfer
        payment_entry = frappe.get_doc("Payment Entry", self.transfer_id)
        
        # Cancel the payment entry
        payment_entry.cancel()
        frappe.msgprint(f"Cash Transfer {self.transfer_id} canceled for {self.name}")

