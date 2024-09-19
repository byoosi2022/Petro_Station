# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _

class PurchaseManagement(Document):
    def on_submit(self):
        self.process_purchase()

    def process_purchase(self):
        self.create_purchase_receipt()
        self.create_purchase_invo_receipt()
        self.create_purchase_invoice()
        self.create_landed_cost_voucher()
        self.create_stock_transfer()
       

    def create_purchase_receipt(self):
        existing_receipt = frappe.get_all("Purchase Receipt", filters={"custom_purchase_management_id": self.name}, limit=1)
        if existing_receipt:
            frappe.msgprint(_("Purchase Receipt already exists for this Purchase Management ID"))
            return
        
        purchase_receipt_entry = frappe.new_doc("Purchase Receipt")
        purchase_receipt_entry.supplier = self.supplier
        purchase_receipt_entry.set_posting_time = 1
        purchase_receipt_entry.posting_time = self.time
        purchase_receipt_entry.posting_date = self.date
        purchase_receipt_entry.due_date = self.due_date
        purchase_receipt_entry.supplier_delivery_note = self.supplier_invoice
        purchase_receipt_entry.bill_date = self.supplier_invoice_date
        purchase_receipt_entry.currency = self.currency
        
        # Set conversion rates based on currency
        if self.currency == 'UGX':
            purchase_receipt_entry.conversion_rate = 1
            purchase_receipt_entry.plc_conversion_rate = 1
       
        else:
            purchase_receipt_entry.conversion_rate = self.usd_exchange_rate
            purchase_receipt_entry.plc_conversion_rate = self.usd_exchange_rate
      
        purchase_receipt_entry.buying_price_list = self.price_list
        purchase_receipt_entry.transporter_name = self.transporter_name
        purchase_receipt_entry.lr_no = self.vehicle_number_plate
        purchase_receipt_entry.lr_date = self.lr_date
        purchase_receipt_entry.custom_purchase_management_id = self.name

        for item in self.items:
            if self.currency:
                purchase_receipt_entry.append("items", {
                    "item_code": item.item,
                    "qty": item.qty,
                    "rate": item.rate,
                    "warehouse": item.warehouse,
                    "cost_center": item.cost_center
                })

        if purchase_receipt_entry.items:
            purchase_receipt_entry.insert()
            self.purchase_receipt_name = purchase_receipt_entry.name
            purchase_receipt_entry.submit()
            frappe.db.commit()
            frappe.msgprint(_("Purchase Receipt created"))
            # self.purchase_receipt_name = purchase_receipt_entry.name
    #  create the invoice for the reciept
    
    def create_purchase_invo_receipt(self):
        existing_lcv = frappe.get_all("Purchase Invoice", filters={"custom_purchase_reciept_id": self.name}, limit=1)
        if existing_lcv:
            frappe.msgprint(_("Purchase Invoice already exists for this Purchase Management ID"))
            return

        if not hasattr(self, 'purchase_receipt_name') or not self.purchase_receipt_name:
            frappe.throw(_("Purchase Invoice must be created before Landed Cost Voucher."))

        purchase_invo = frappe.get_doc("Purchase Receipt", self.purchase_receipt_name)
        purchase_invoice_entry = frappe.new_doc("Purchase Invoice")
        purchase_invoice_entry.supplier = purchase_invo.supplier
        purchase_invoice_entry.currency = purchase_invo.currency
        purchase_invoice_entry.set_posting_time = 1
        purchase_invoice_entry.posting_time = purchase_invo.posting_time
        purchase_invoice_entry.posting_date = purchase_invo.posting_date
        purchase_invoice_entry.due_date = self.due_date
        purchase_invoice_entry.bill_no = purchase_invo.supplier_delivery_note
        purchase_invoice_entry.bill_date = self.supplier_invoice_date
        purchase_invoice_entry.buying_price_list = self.price_list
        
         # Set conversion rates based on currency
        if self.currency == 'UGX':
            purchase_invoice_entry.conversion_rate = 1
            purchase_invoice_entry.plc_conversion_rate = 1
       
        else:
            purchase_invoice_entry.conversion_rate = self.usd_exchange_rate
            purchase_invoice_entry.plc_conversion_rate = self.usd_exchange_rate
        
        purchase_invoice_entry.custom_purchase_reciept_id = self.name
        for item in purchase_invo.items:
            purchase_invoice_entry.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": item.rate,
                "warehouse": item.warehouse,
                "cost_center": item.cost_center,
                "purchase_receipt":purchase_invo.name
                })
            
        if purchase_invoice_entry.items:
                purchase_invoice_entry.insert()
                purchase_invoice_entry.submit()
                frappe.db.commit()
                frappe.msgprint(_("Purchase Invoice created for supplier:"))
    
    # ends here............

    def create_purchase_invoice(self):
        existing_invoices = frappe.get_all("Purchase Invoice", filters={"custom_purchase_management_id": self.name}, limit=1)
        if existing_invoices:
            frappe.msgprint(_("Purchase Invoice already exists for this Purchase Management ID"))
            return

        grouped_items = {}
        for item in self.other_items:
            key = (item.supplier, item.currency,item.invoice_date)
            if key not in grouped_items:
                grouped_items[key] = []
            grouped_items[key].append(item)

        for key, items in grouped_items.items():
            supplier, currency,invoice_date = key
            purchase_invoice_entry = frappe.new_doc("Purchase Invoice")
            purchase_invoice_entry.supplier = supplier
            purchase_invoice_entry.currency = currency
            purchase_invoice_entry.set_posting_time = 1
            purchase_invoice_entry.posting_time = self.time
            purchase_invoice_entry.posting_date = invoice_date
            purchase_invoice_entry.due_date = self.due_date
            purchase_invoice_entry.bill_no = self.supplier_invoice
            purchase_invoice_entry.bill_date = self.supplier_invoice_date
            purchase_invoice_entry.buying_price_list = self.price_list
            purchase_invoice_entry.custom_purchase_management_id = self.name

            for item in items:
                purchase_invoice_entry.append("items", {
                    "item_code": item.item,
                    "qty": item.qty,
                    "rate": item.rate,
                    "net_rate":item.rate,
                    "warehouse": item.accepted_warehouse,
                    "cost_center": item.cost_center
                })

            if purchase_invoice_entry.items:
                purchase_invoice_entry.insert()
                purchase_invoice_entry.submit()
                frappe.db.commit()
                frappe.msgprint(_("Purchase Invoice created for supplier: {0}, currency: {1}").format(supplier, currency))

    def create_stock_transfer(self):
        # Group items by target store
        if not self.stock_items:
            frappe.msgprint(_("No items to transfer"), alert=True)
            return
        target_store_map = {}
        for item in self.stock_items:
            if item.target_store:
                if item.target_store not in target_store_map:
                    target_store_map[item.target_store] = []
                target_store_map[item.target_store].append(item)

        # Create a Stock Entry for each target store
        for target_store, items in target_store_map.items():
            existing_stock_entry = frappe.get_all("Stock Entry", filters={"custom_purchase_management_id": self.name, "t_warehouse": target_store}, limit=1)
            if existing_stock_entry:
                frappe.msgprint(_("Stock Entry already exists for target store {0}").format(target_store))
                continue

            # Create new Stock Entry for the current target store
            stock_entry = frappe.new_doc("Stock Entry")
            stock_entry.stock_entry_type = "Material Transfer"
            stock_entry.set_posting_time = 1  # Allow setting of custom posting time
        
            # Use the date and time from the first valid item in this group
            stock_entry.posting_date = items[0].date if items[0].date else frappe.utils.today()
            stock_entry.posting_time = items[0].time if items[0].time else frappe.utils.nowtime()
            stock_entry.custom_purchase_management_id = self.name
            stock_entry.t_warehouse = target_store

            # Add items to the stock entry
            for item in items:
                if item.qty > 0 and item.accepted_warehouse:  # Ensure valid qty and source warehouse
                    stock_entry.append("items", {
                        "item_code": item.item,
                        "qty": item.qty,
                        "s_warehouse": item.accepted_warehouse,
                        "t_warehouse": target_store,
                        "cost_center": item.cost_center or self.cost_center  # Use item's cost center or default to Purchase Management's cost center
                    })
                else:
                    frappe.msgprint(_("Skipping item {0} due to invalid qty or source warehouse").format(item.item), alert=True)

            # Check if items were added before inserting and submitting the Stock Entry
            if stock_entry.items:
                try:
                    stock_entry.insert()
                    stock_entry.submit()
                    frappe.db.commit()
                    frappe.msgprint(_("Stock Transfer created for target store {0}").format(target_store))
                except Exception as e:
                    frappe.throw(_("An error occurred while creating Stock Transfer for target store {0}: {1}").format(target_store, str(e)))
            else:
                frappe.msgprint(_("No valid items to transfer for target store {0}").format(target_store), alert=True)

    def create_landed_cost_voucher(self):
        existing_lcv = frappe.get_all("Landed Cost Voucher", filters={"custom_purchase_management_id": self.name}, limit=1)
        if existing_lcv:
            frappe.msgprint(_("Landed Cost Voucher already exists for this Purchase Management ID"))
            return

        if not hasattr(self, 'purchase_receipt_name') or not self.purchase_receipt_name:
            frappe.throw(_("Purchase Receipt must be created before Landed Cost Voucher."))

        purchase_receipt_entry = frappe.get_doc("Purchase Receipt", self.purchase_receipt_name)

        landed_voucher = frappe.new_doc("Landed Cost Voucher")
        landed_voucher.posting_date = self.date
        landed_voucher.custom_purchase_management_id = self.name
        landed_voucher.append("purchase_receipts", {
            "receipt_document_type": "Purchase Receipt",
            "receipt_document": self.purchase_receipt_name,
            "supplier": purchase_receipt_entry.supplier,
            "grand_total": purchase_receipt_entry.base_total
        })

        for item in purchase_receipt_entry.items:
            landed_voucher.append("items", {
                "item_code": item.item_code,
                "description": item.description,
                "qty": item.qty,
                "rate": item.base_rate,
                "cost_center": item.cost_center,
                "amount": item.base_amount,
                "receipt_document_type": "Purchase Receipt",
                "receipt_document": self.purchase_receipt_name,
                "purchase_receipt_item": item.name,
                "is_fixed_asset": item.is_fixed_asset
            })

        for item in self.other_items:
            item_defaults = frappe.get_doc("Item Default", {"parent": item.item, "parentfield": "item_defaults"})
            expense_account = item_defaults.expense_account if item_defaults else None
            landed_voucher.append("taxes", {
                "description": item.item,
                "amount": item.amount,
                "expense_account": expense_account,
            })

        landed_voucher.insert()
        landed_voucher.submit()
        frappe.db.commit()
        frappe.msgprint(_("Landed Cost Voucher created"))
