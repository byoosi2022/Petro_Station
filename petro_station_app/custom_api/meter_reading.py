import frappe  # type: ignore
from frappe.utils import now_datetime  # type: ignore
from frappe import _  # type: ignore

def create_pump_meter_reading(doc, method):
    try:
        if doc.doctype == "Sales Invoice":
            if method == "on_cancel":
                cancel_pump_meter_reading(doc)
                return

            # Get the source warehouse (pump) for each item
            source_warehouses = set([item.get("warehouse") for item in doc.get("items")])

            for source_warehouse in source_warehouses:
                # Filter out items that do not have the item group "Fuel" for the current warehouse
                fuel_items = [item for item in doc.get("items") if item.get("item_group") == "Fuel" and item.get("warehouse") == source_warehouse]

                if fuel_items:
                    # Get the total quantity for the current item
                    total_quantity = sum([item.get("qty") for item in fuel_items])

                    # Get the present reading value from the Meter Readings doctype
                    meter_reading = frappe.get_all("Meter Readings", filters={"pump": source_warehouse}, fields=["initial_reading_value", "present_reading_value"])

                    if meter_reading:
                        present_reading_value = meter_reading[0].get("present_reading_value")
                        initial_reading_value = meter_reading[0].get("initial_reading_value")
                    else:
                        present_reading_value = 0
                        initial_reading_value = 0

                    if not present_reading_value:
                        current_reading_value = total_quantity + initial_reading_value
                    else:
                        current_reading_value = present_reading_value + total_quantity

                    # Create Pump Meter Reading entry
                    pump_meter_reading = frappe.new_doc("Pump Meter Reading")
                    pump_meter_reading.branch = doc.get("cost_center")
                    pump_meter_reading.date = now_datetime()
                    pump_meter_reading.pump_date = doc.posting_date
                    pump_meter_reading.cost_center = doc.get("cost_center")
                    pump_meter_reading.employee = frappe.session.user
                    pump_meter_reading.employer_name = frappe.get_value("User", frappe.session.user, "full_name")
                    pump_meter_reading.sales_invoice = doc.name
                    pump_meter_reading.custom_fuel_sales_app_id = doc.custom_fuel_sales_app_id
                    pump_meter_reading.pump = source_warehouse
                    pump_meter_reading.present_reading_value = present_reading_value
                    pump_meter_reading.current_reading_value = current_reading_value
                    pump_meter_reading.sales_invoice_posting_date = doc.get("posting_date")
                    pump_meter_reading.insert()

                    qty_pernow = current_reading_value - initial_reading_value
                    # Submit the Pump Meter Reading qty_as_per_now
                    pump_meter_reading.submit()

                    # Update Meter Reading with current_reading_value
                    frappe.db.set_value("Meter Readings", {"pump": source_warehouse}, {
                        "present_reading_value": current_reading_value,
                        "qty_as_per_now": qty_pernow,
                        "current_date": now_datetime()
                    })

    except Exception as e:
        frappe.log_error(_("Error creating Pump Meter Reading: {0}").format(e))
        frappe.throw(_("Error creating Pump Meter Reading. Please try again."))

def cancel_pump_meter_reading(doc):
    try:
        if doc.doctype == "Sales Invoice":
            # Get the source warehouse (pump) for each item
            source_warehouses = set([item.get("warehouse") for item in doc.get("items")])

            for source_warehouse in source_warehouses:
                # Filter out items that do not have the item group "Fuel" for the current warehouse
                fuel_items = [item for item in doc.get("items") if item.get("item_group") == "Fuel" and item.get("warehouse") == source_warehouse]

                if fuel_items:
                    # Get the total quantity for the current item
                    total_quantity = sum([item.get("qty") for item in fuel_items])

                    # Get the present reading value from the Meter Readings doctype
                    meter_reading = frappe.get_all("Meter Readings", filters={"pump": source_warehouse}, fields=["initial_reading_value", "present_reading_value"])

                    if meter_reading:
                        present_reading_value = meter_reading[0].get("present_reading_value")
                        initial_reading_value = meter_reading[0].get("initial_reading_value")
                    else:
                        present_reading_value = 0
                        initial_reading_value = 0

                    if not present_reading_value:
                        current_reading_value = initial_reading_value - total_quantity
                    else:
                        current_reading_value = present_reading_value - total_quantity

                    qty_pernow = current_reading_value - initial_reading_value

                    # Update Meter Reading with current_reading_value
                    frappe.db.set_value("Meter Readings", {"pump": source_warehouse}, {
                        "present_reading_value": current_reading_value,
                        "qty_as_per_now": qty_pernow,
                        "current_date": now_datetime()
                    })

            frappe.msgprint(_("Meter Reading updated successfully"))

    except Exception as e:
        frappe.log_error(_("Error updating Pump Meter Reading on cancel: {0}").format(e))
        frappe.throw(_("Error updating Pump Meter Reading on cancel. Please try again."))
