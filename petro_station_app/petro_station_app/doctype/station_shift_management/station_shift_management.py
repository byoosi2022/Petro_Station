# Copyright (c) 2024, mututa paul and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe.utils import add_days, today

class StationShiftManagement(Document):
    # def before_insert(self):
    #     # Set the from_date to the day before today when creating a new document
    #     self.from_date = add_days(today(), -1)

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
                frappe.throw(f"A shift management document already exists for station {self.station} on {self.from_date}")

        # If no existing document is found, allow save
        # This method automatically proceeds to save the document

    def on_update(self):
        self.before_save()

