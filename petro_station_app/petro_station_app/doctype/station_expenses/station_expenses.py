# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _

class StationExpenses(Document):
    def on_submit(self):
        # Check for existing Journal Entry
        existing_receipt = frappe.get_all("Journal Entry", filters={"custom_station_expense_id": self.name}, limit=1)
        
        if existing_receipt:
            frappe.msgprint(_(f"Station Expenses already exists for {self.name}"))
            return
        
        # Get default account for mode of payment
        methods = frappe.get_value("Mode of Payment Account", {"parent": self.mode_of_payment}, "default_account")
        if not methods:
            frappe.throw(_("No default account found for the mode of payment: {0}").format(self.mode_of_payment))
        
        # Create new Journal Entry
        journal_entry = frappe.new_doc('Journal Entry')
        journal_entry.voucher_type = 'Journal Entry'
        journal_entry.company = 'Fahaab Energy Uganda'
        journal_entry.posting_date = self.date
        journal_entry.custom_station_expense_id = self.name
        
        for item in self.items:
            # Get default account for claim type
            claim_account = frappe.get_value("Expense Claim Account", {"parent": item.claim_type}, "default_account")
            if not claim_account:
                frappe.throw(_("No default account found for the claim type: {0}").format(item.claim_type))
            
            # Debit Entry
            journal_entry.append('accounts', {
                'account': "2110 - Creditors - FEU",
                'party_type': item.party_type,
                'party': item.party,
                'description': item.description,
                'debit_in_account_currency': item.amount,
                'credit_in_account_currency': 0,
                'cost_center': item.branch
            })
            
            # Credit Entry
            journal_entry.append('accounts', {
                'account': methods,
                'debit_in_account_currency': 0,
                'credit_in_account_currency': item.amount,
                'cost_center': item.branch
            })
            
            # Additional Debit Entry
            journal_entry.append('accounts', {
                'account': "2110 - Creditors - FEU",
                'party_type': item.party_type,
                'description': item.description,
                'party': item.party,
                'debit_in_account_currency': 0,
                'credit_in_account_currency': item.amount,
                'cost_center': item.branch
            })
            
            # Additional Credit Entry
            journal_entry.append('accounts', {
                'account': claim_account,
                'debit_in_account_currency': item.amount,
                'credit_in_account_currency': 0,
                'cost_center': item.branch
            })
        
        # Save the Journal Entry
        journal_entry.save()
        # Uncomment the next line if you want to submit the Journal Entry automatically
        journal_entry.submit()
        frappe.db.commit()
        frappe.msgprint(_(f"Successfully Posted  Station Expenses for {self.name}"))
