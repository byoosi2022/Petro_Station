from frappe.model.document import Document
import frappe
from frappe import _

class FuelSalesApp(Document):

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
            stock_entry.custom_fuel_sales_app_id = self.name 

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
            sales_invoice.custom_fuel_sales_app_id = self.name 

            for item in self.items:
                sales_invoice.append("items", {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "rate": item.rate,
                    "warehouse": item.warehouse,
                    "amount": item.amount,
                    "custom_vehicle_plates": item.number_plate
                })

            if sales_invoice.items:
                sales_invoice.insert()
                sales_invoice.submit()
                self.sales_invoice_created = sales_invoice.name
                self.net_total = sales_invoice.net_total
                frappe.msgprint(_("Sales Invoice created and submitted"))

                # Calculate net total
                net_total = sum(item.net_amount for item in sales_invoice.items)

                # Create Payment Entry
                if self.include_payments:
                    pos_profile = self.items[0].pos_profile if self.items else None
                    payment_methods = frappe.get_all("POS Payment Method", filters={"parent": pos_profile},
                                                     fields=["mode_of_payment"])
                    for payment_method in payment_methods:
                        mode_of_payment = payment_method.mode_of_payment
                        mode_of_pay_doc = frappe.get_doc("Mode of Payment", mode_of_payment)
                        default_account = mode_of_pay_doc.accounts[0].default_account
                        currency = frappe.db.get_value("Account", default_account, "account_currency")
                        payment_entry = frappe.new_doc("Payment Entry")
                        payment_entry.party_type = "Customer"
                        payment_entry.payment_type = "Receive"
                        payment_entry.posting_date = self.date
                        payment_entry.party = self.customer
                        payment_entry.paid_amount = net_total
                        payment_entry.received_amount = net_total
                        payment_entry.target_exchange_rate = 1.0
                        payment_entry.paid_to = default_account
                        payment_entry.paid_to_account_currency = currency
                        payment_entry.mode_of_payment = mode_of_payment
                        payment_entry.custom_fuel_sales_app_id = self.name 

                        # Ensure allocated amount does not exceed the outstanding amount
                        outstanding_amount = sales_invoice.outstanding_amount
                        allocated_amount = min(net_total, outstanding_amount)
                        payment_entry.append("references", {
                            "reference_doctype": "Sales Invoice",
                            "reference_name": sales_invoice.name,
                            "allocated_amount": allocated_amount
                        })

                        payment_entry.insert()
                        payment_entry.submit()
                        frappe.db.commit()
                        frappe.msgprint(_(f"Payments Made for invoice {sales_invoice.name}"))

                    # self.db_set("sales_invoice_created", sales_invoice.name)
