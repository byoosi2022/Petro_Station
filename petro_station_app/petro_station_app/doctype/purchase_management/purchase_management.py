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
        self.create_stock_transfer()
        self.create_landed_cost_voucher()

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
        existing_stock_entry = frappe.get_all("Stock Entry", filters={"custom_purchase_management_id": self.name}, limit=1)
        if existing_stock_entry:
            frappe.msgprint(_("Stock Entry already exists for this Purchase Management ID"))
            return

        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.set_posting_time = 1
        stock_entry.posting_time = self.time
        stock_entry.posting_date = self.date
        stock_entry.custom_purchase_management_id = self.name

        for item in self.stock_items:
            stock_entry.append("items", {
                "item_code": item.item,
                "qty": item.qty,
                "s_warehouse": item.accepted_warehouse,
                "t_warehouse": item.target_store,
                "cost_center": item.cost_center
            })

        if stock_entry.items:
            stock_entry.insert()
            stock_entry.submit()
            frappe.db.commit()
            frappe.msgprint(_("Stock Transfer created"))

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
