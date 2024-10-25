# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document  # type: ignore
import frappe  # type: ignore
from frappe import _  # type: ignore

class CreditSalesApp(Document):
    def on_submit(self):
        # Check if customer has a fuel card and the status is "Active"
        if self.has_card == 1 and self.status == "Active":
            # Fetch the corresponding Fuel Card for the customer using the custom field
            custom_fuel_card_number = self.card_number
            fuel_card = frappe.get_doc("Fuel Card", {"customer": self.customer, "custom_serie": custom_fuel_card_number})

            if fuel_card:
                # Check if OTP code is not set or empty
                if not self.otp_code:
                    frappe.throw(_("Please fill in the OTP Code before proceeding"))

                # Validate if OTP code exists in the 'OTP Code' doctype
                existing_otp_code = frappe.db.exists('OTP Code', {'name': self.otp_code})
    
                if not existing_otp_code:  # If OTP code does not exist
                    frappe.throw(_('Error: OTP Code is not correct.'))
                
                # Calculate total outstanding balance for the customer
                total_outstanding = frappe.db.get_value(
                    "Sales Invoice",
                    {
                        "customer": self.customer,
                        "docstatus": 1,
                        "custom_fuel_card_number": self.card_number
                    },
                    "SUM(outstanding_amount)"
                ) or 0

                # Check if adding the current total would exceed the card limit
                overall_total = total_outstanding + self.grand_totals
                if overall_total > fuel_card.card_limit:
                    frappe.throw(
                        _("Total outstanding amount and grand Amount of {0} exceeds the card limit of {1}. Please adjust the invoice.").format(
                            overall_total, fuel_card.card_limit
                        )
                    )
                    
                             

                # Deduct the card limit by the current outstanding amount
                fuel_card.customers_balance += overall_total
                fuel_card.save()



        # Filter fuel items from the item list
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

            # Set the custom fuel card number only if applicable
            if self.has_card and self.card_number:
                sales_invoice.custom_fuel_card_number = self.card_number

            sales_invoice.additional_discount_account = "5125 - Discounts on Fuel - FEU"
            sales_invoice.custom_credit_sales_app = self.name
            remarks = ""

            # Append item details to the Sales Invoice
            for item in self.items:
                sales_invoice.append("items", {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "rate": item.rate,
                    "warehouse": item.warehouse,
                    "amount": item.amount,
                    "custom_vehicle_plates": item.number_plate
                })
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

    def on_cancel(self):
        # Check if customer has a fuel card and the status is "Active"
        if self.has_card == 1 and self.status == "Active":
            # Fetch the corresponding Fuel Card for the customer using the custom field
            custom_fuel_card_number = self.card_number
            fuel_card = frappe.get_doc("Fuel Card", {"customer": self.customer, "custom_serie": custom_fuel_card_number})

            if fuel_card:
                # Deduct the net_total from the customer's balance
                fuel_card.customers_balance -= self.grand_totals
                fuel_card.save()
                
    def on_update(self):
        # Check if customer has a fuel card and the status is "Active"
        if self.has_card == 1 and self.status == "Active":
            try:
                # Get customer contact number
                customer_contact = self.get_customer_contact()

                # Check if an OTP Code with the same contact number already exists
                if self.is_otp_code_exists(customer_contact):
                    return
                else:
                    # Create an OTP Code document
                    otp_code_doc = frappe.new_doc('OTP Code')
                    otp_code_doc.tel = customer_contact
                    otp_code_doc.credit_id = self.name  # self.name is the Credit Sales App name
                    otp_code_doc.insert()
                    otp_code_doc.submit()
                    frappe.msgprint('OTP Code created successfully!')
            except Exception as e:
                frappe.msgprint(str(e))

    def get_customer_contact(self):
        # Check if a fuel card is selected
        if self.pick_the_card:
            # Fetch the fuel card document
            card_id = frappe.get_doc('Fuel Card', self.pick_the_card)

            # Get the contact number from the fuel card
            contact_number = card_id.contact_number  # Assuming 'contact_number' is the field name

            # Check if contact_number is not empty
            if contact_number:
                # Clean the contact number: strip whitespace and remove '+' and '-'
                cleaned_contact_number = contact_number.strip().replace('+', '').replace('-', '')
                return cleaned_contact_number
            else:
                # Raise an error if no phone number is found
                frappe.throw('Error: No contact number found for the selected fuel card.')
        else:
            frappe.throw('Error: No fuel card selected.')

    def is_otp_code_exists(self, contact_number=None):
        # Check if an OTP Code with the same contact number exists
        existing_otp_code = frappe.db.exists('OTP Code', {'credit_id': self.name})
        return existing_otp_code is not None

