# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe

class DippingLog(Document):
    def validate(self):
        if not self.is_new():
            return  # Skip validation for updates to existing documents

        # Check if a DippingLog entry already exists for the same tank, branch, and date
        existing_log = frappe.db.exists({
            'doctype': 'Dipping Log',
            'tank': self.tank,
            'branch': self.branch,
            'dipping_date': self.dipping_date
        })
        
        if existing_log:
            frappe.throw(f"A DippingLog entry already exists for tank {self.tank}, branch {self.branch} on {self.dipping_date}.")
    
    def on_submit(self):
        if self.dipping_difference is None or self.dipping_difference == 0:
            return  # Skip creating Stock Entry if there is no difference
        
        if self.dipping_difference is not None:
            # Determine the type of Stock Entry and the warehouses
            if self.dipping_difference > 0:
                stock_entry_type = "Material Issue"
                message = "A loss has been issued."
                source_warehouse = self.tank
                target_warehouse = None
            else:
                stock_entry_type = "Material Receipt"
                message = "A gain has been received."
                source_warehouse = None
                target_warehouse = self.tank
            
            # Create the Stock Entry
            stock_entry = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": stock_entry_type,
                "posting_date": self.dipping_date,
                "posting_time": self.dipping_time,
                "set_posting_time": 1,
                "dipping_log_id": self.name,
                "items": [{
                    "item_code": self.item_code,
                    "s_warehouse": source_warehouse,
                    "t_warehouse": target_warehouse,
                    "cost_center": self.branch,
                    "qty": abs(self.dipping_difference)  # Ensure the quantity is always positive
                }]
            })
            
            # Insert and submit the Stock Entry
            stock_entry.insert()
            stock_entry.submit()
            
            # Display the message
            frappe.msgprint(message)
