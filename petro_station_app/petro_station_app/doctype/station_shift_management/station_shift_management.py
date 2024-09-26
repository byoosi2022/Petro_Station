# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe.utils import add_days, today

class StationShiftManagement(Document):
    def on_submit(self):
        self.take_dipping_before()
 
        # Fetch all transit warehouses
        transit_warehouses = frappe.get_all(
            "Warehouse",
            filters={"warehouse_type": "Transit"},
            fields=["name"]
        )

        # Extract list of transit warehouse names
        transit_warehouse_names = [wh['name'] for wh in transit_warehouses]

        # Fetch Stock Entry records that are drafts (docstatus 0) and of type 'Material Transfer'
        stock_entries = frappe.get_list(
            'Stock Entry',
            filters={'stock_entry_type': 'Material Transfer', 'docstatus': 0},
            fields=['name', 'posting_date', 'posting_time', 'stock_entry_type', 'docstatus'],
            order_by='posting_date desc'
        )
        
        # Check if any Stock Entry Details match the station and transit warehouse criteria
        for entry in stock_entries:
            stock_entry_details_drafts = frappe.get_all(
                'Stock Entry Detail',
                filters={
                    'parent': entry.name,
                    'docstatus': 0,  # Draft status
                    'cost_center': self.station,  # Check for matching station cost center
                    's_warehouse': ['in', transit_warehouse_names],  # Source must be transit warehouse
                    't_warehouse': ['in', transit_warehouse_names]   # Target must be transit warehouse
                },
                fields=['name', 'item_code', 's_warehouse', 't_warehouse', 'qty', 'cost_center']
            )

            # If drafts are found, raise an error
            if stock_entry_details_drafts:
                frappe.throw(f"You still haven't Recieved some draft stock entries for station {self.station}. Please complete them before proceeding.")


    def before_save(self):
        # Check if a document already exists for the same date and station
        if self.from_date and self.station:
            existing_doc = frappe.db.exists(
                'Station Shift Management',
                {
                    'from_date': self.from_date,
                    'station': self.station
                }
            )

            if existing_doc and existing_doc != self.name:
                frappe.throw(f"A shift management document already exists for station {self.station} on {self.from_date}.")

    def take_dipping_before(self):
       # Check if a Stock Reconciliation document exists for the same date and station
        if self.from_date and self.station:
            existing_doc = frappe.db.exists(
                'Stock Reconciliation',
                {
                    'posting_date': self.from_date,
                    'cost_center': self.station,
                    'purpose': "Stock Reconciliation",
                    'docstatus': 1  # docstatus 1 means the document is submitted
                }
            )

            if not existing_doc:  # Correcting the syntax for "not"
                frappe.throw(f"Dipping Levels should be taken for today before proceeding for station {self.station} on {self.from_date}.")
   
    def get_material_transfer_entries(self):
        try:
            # Fetch Stock Entry records with the required filters
            stock_entries = frappe.get_list('Stock Entry',
                filters={
                    'stock_entry_type': 'Material Transfer',
                    'docstatus': 0,  # Draft status
                    # 'posting_date':self.from_date
                },
                fields=['name', 'posting_date', 'posting_time', 'stock_entry_type', 'docstatus'],
                order_by='posting_date desc'
            )
            # Get warehouses with the specified cost center and warehouse types (Transit)
            transit_warehouses = frappe.get_all(
                "Warehouse",
                filters={
                    "warehouse_type": "Transit",
                    # "custom_cost_centre": station,
                },
                fields=["name"]
            )

            # Extract list of transit warehouse names
            transit_warehouse_names = [wh['name'] for wh in transit_warehouses]

            # Filter further to check for cost center in Stock Entry Detail child table
            filtered_entries = []
            for entry in stock_entries:
                stock_entry_details = frappe.get_all('Stock Entry Detail',
                    filters={
                        'parent': entry.name,
                        'cost_center': self.station,  # Filter by cost center == station
                        's_warehouse': ['in', transit_warehouse_names],  # Source warehouse must be of type Transit
                        't_warehouse': ['in', transit_warehouse_names]   # Target warehouse must be of type Transit
                    },
                    fields=['name', 'item_code', 's_warehouse', 't_warehouse', 'qty', 'cost_center']
                )

            if stock_entry_details:
                filtered_entries.append({
                    'stock_entry': entry.name,
                    'posting_date': entry.posting_date,
                    'status': entry.docstatus,
                    'posting_time': entry.posting_time,
                    'details': stock_entry_details
                })

            if filtered_entries:
                frappe.throw(f"Fuel Transfer should be done for today before proceeding for station {self.station} on {self.from_date}.")
         
  
        except Exception as e:
            # Log error if any and return error response
            frappe.log_error(frappe.get_traceback(), "Stock Entry Fetch Error")
            return {"status": "failed", "error": str(e)}

   
   
   
    def on_update(self):
        self.before_save()
      
       
