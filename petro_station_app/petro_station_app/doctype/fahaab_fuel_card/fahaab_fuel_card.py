# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FahaabFuelCard(Document):
    def on_load(self):
        # Check if the customer is set
        if self.customer:
            self.set_customers_balance()

    def set_customers_balance(self):
        # Only set the balance if it's not already set
        if self.customers_balance:
            # Fetch total outstanding balance from Sales Invoices for the customer
            total_outstanding = frappe.db.get_value(
                "Sales Invoice",
                {"customer": self.customer, "docstatus": 0,"custom_fuel_card_number":self.custom_serie},
                "SUM(outstanding_amount)"
            )
            
            # Set the customer's balance field
            self.customers_balance = total_outstanding if total_outstanding else 0


