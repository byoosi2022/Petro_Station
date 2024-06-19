# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

from frappe.model.document import Document
import frappe
from frappe import _

class FuelTransfers(Document):
    def on_submit(self):
        try:
            fuel_items = [item for item in self.items if frappe.get_value("Item", item.item_code, "item_group") == "Fuel"]

            if fuel_items:
                # Create a Stock Transfer for fuel items
                stock_entry = frappe.new_doc("Stock Entry")
                stock_entry.stock_entry_type = "Material Transfer"
                stock_entry.set_posting_time = 1
                stock_entry.posting_time = self.posting_time
                stock_entry.posting_date = self.posting_date

                for item in fuel_items:
                    stock_entry.append("items", {
                        "item_code": item.item_code,
                        "qty": item.qty,
                        "s_warehouse": item.s_warehouse,
                        "t_warehouse": item.t_warehouse,
                        "difference_account": item.difference_account,
                        "cost_center": item.cost_center
                    })

                stock_entry.insert()
                stock_entry.submit()
                frappe.db.commit()
                self.db_set("tranfer_id", stock_entry.name)
                frappe.msgprint(_("Fuel transfer successfully done"))
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Fuel Transfer Error"))
            frappe.throw(_("There was an error while processing the fuel transfer. Please check the error log for details."))
