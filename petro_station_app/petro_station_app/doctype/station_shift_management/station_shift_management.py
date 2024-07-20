# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe.utils import add_days, today

class StationShiftManagement(Document):
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

        # List to hold missing tanks
        missing_tanks = []

        # Check if all tanks are saved and submitted in the dipping log
        for item in self.items:
            # Get the Default In-Transit Warehouse for the pump_or_tank
            warehouse = frappe.get_doc("Warehouse", item.pump_or_tank)
            tank = warehouse.default_in_transit_warehouse

            if not tank:
                frappe.throw(f"Default In-Transit Warehouse not set for pump or tank {item.pump_or_tank}")

            # Check if a Dipping Log entry exists for the tank
            dipping_log_exists = frappe.db.exists({
                'doctype': 'Dipping Log',
                'tank': tank,
                'branch': self.station,
                'dipping_date': self.from_date,
                'docstatus': 1
            })

            if not dipping_log_exists:
                missing_tanks.append(tank)

        # Throw an error if there are missing tanks
        if missing_tanks:
            missing_tanks_list = ", ".join(missing_tanks)
            frappe.throw(f"Dipping Level entries for the following tanks are missing or not submitted: {missing_tanks_list}")

    def on_update(self):
        self.before_save()
