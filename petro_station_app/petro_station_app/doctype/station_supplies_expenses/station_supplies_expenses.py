# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe
from frappe import _

class StationSuppliesExpenses(Document):
    def on_submit(self):
        if self.check_existing_invoice():
            frappe.msgprint(_("Supplier Expenses already exists for this Station Supplies Expenses"), alert=True)
            frappe.throw(_("Document cannot be submitted because a related Purchase Invoice already exists."))
        self.process_purchase()

    def check_existing_invoice(self):
        existing_lcv = frappe.get_all("Purchase Invoice", filters={"custom__supplies_expenses": self.name}, limit=1)
        return bool(existing_lcv)

    def process_purchase(self):
        self.create_purchase_invo_receipt()

    def create_purchase_invo_receipt(self):
        # Get default account for mode of payment
        methods = frappe.get_value("Mode of Payment Account", {"parent": self.mode_of_payment}, "default_account")
        if not methods:
            frappe.throw(_("No default account found for the mode of payment: {0}").format(self.mode_of_payment))

        purchase_invoice_entry = frappe.new_doc("Purchase Invoice")
        purchase_invoice_entry.supplier = self.supplier
        purchase_invoice_entry.set_posting_time = 1
        purchase_invoice_entry.posting_date = self.date
        purchase_invoice_entry.is_paid = self.is_paid
        purchase_invoice_entry.cash_bank_account = methods
        purchase_invoice_entry.paid_amount = self.paid_amount
        purchase_invoice_entry.mode_of_payment = self.mode_of_payment
        purchase_invoice_entry.due_date = self.due_date
        purchase_invoice_entry.cost_center = self.station
        purchase_invoice_entry.custom__supplies_expenses = self.name
        for item in self.items:
            purchase_invoice_entry.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": item.rate,
                "cost_center": self.station,
            })

        if purchase_invoice_entry.items:
            purchase_invoice_entry.insert()
            purchase_invoice_entry.submit()
            frappe.db.commit()
            frappe.msgprint(_("Station Supplies Expenses created for supplier: {0}").format(self.supplier))
