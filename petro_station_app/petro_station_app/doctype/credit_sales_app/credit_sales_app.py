# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document # type: ignore
import frappe # type: ignore
from frappe import _ # type: ignore



class CreditSalesApp(Document):
    def on_submit(self):
        fuel_items = [item for item in self.items if frappe.get_value("Item", item.item_code, "item_group") == "Fuel"]

        if fuel_items:
            # Create a Stock Transfer for fuel items
            company_abbr = frappe.get_value("Company", self.company, "abbr")
            stock_entry = frappe.new_doc("Stock Entry")
            stock_entry.stock_entry_type = "Material Transfer"
            stock_entry.set_posting_time = 1
            stock_entry.posting_time = self.time
            stock_entry.posting_date = self.date 
            stock_entry.custom_credit_sales_app = self.name 

            for item in fuel_items:
                source_warehouse = item.warehouse
                if f" - {company_abbr}" in source_warehouse:
                    source_warehouse_strip = source_warehouse[:-len(f" - {company_abbr}")].strip()
                else:
                    source_warehouse_strip = source_warehouse
                warehouse = frappe.get_all("Warehouse", filters={"warehouse_name": source_warehouse_strip},
                                           fields=["default_in_transit_warehouse", "parent_warehouse"])
                if warehouse:
                    in_transit_warehouse = warehouse[0].get("default_in_transit_warehouse")
                    if not in_transit_warehouse:
                        frappe.throw(_("Transit warehouse not set in Warehouse"))
                    stock_entry.append("items", {
                        "item_code": item.item_code,
                        "qty": item.qty,
                        "uom": item.uom,
                        "s_warehouse": in_transit_warehouse,
                        "t_warehouse": source_warehouse
                    })

            stock_entry.insert()
            stock_entry.submit()
            frappe.db.commit()
            frappe.msgprint(_("Tank to Pump transfer successfully transferred to the Client"))

        # Check if a Sales Invoice has already been created 
        if not self.sales_invoice_created:
            sales_invoice = frappe.new_doc("Sales Invoice")
            sales_invoice.customer = self.customer
            sales_invoice.discount_amount = self.additional_discount_amount
            sales_invoice.due_date = self.due_date
            sales_invoice.allocate_advances_automatically = 0 if self.include_payments == 1 else 1
            sales_invoice.cost_center = self.station 
            sales_invoice.update_stock = 1
            sales_invoice.set_posting_time = 1
            sales_invoice.posting_date = self.date
            sales_invoice.posting_time = self.time
            sales_invoice.additional_discount_account = "5125 - Discounts on Fuel - FEU"
            sales_invoice.custom_credit_sales_app = self.name 
            remarks = ""
            for item in self.items:
                sales_invoice.append("items", {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "rate": item.rate,
                    "warehouse": item.warehouse,
                    "amount": item.amount,
                    "custom_vehicle_plates": item.number_plate
                })
                # Append each item's details to the remarks string
                if item.number_plate:
                    remarks += f"Item: {item.item_code}, Quantity: {item.qty}, Amount: {item.amount}, Vehicle Plate: {item.number_plate}\n"
            # Set the accumulated remarks in the Sales Invoice
            sales_invoice.remarks = remarks
            
            if sales_invoice.items:
                sales_invoice.insert()
                sales_invoice.submit()
                self.sales_invoice_created = sales_invoice.name
                self.net_total = sales_invoice.net_total
                frappe.msgprint(_("Invoice created and submitted"))
	