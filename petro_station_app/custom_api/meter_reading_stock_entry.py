import frappe  # type: ignore
from frappe.utils import now_datetime  # type: ignore
from frappe import _  # type: ignore

def create_pump_meter_reading(doc, method):
    try:
        if doc.doctype == "Stock Entry" and doc.stock_entry_type == "Material Transfer":
            if method == "on_cancel":
                cancel_stock_entry_meter_reading(doc)
                return

            # Get the source warehouse (pump) for each item
            source_warehouses = set([
                item.get("s_warehouse")
                for item in doc.get("items")
                if frappe.get_value("Warehouse", item.get("s_warehouse"), "warehouse_type") == "Pump"
            ])

            # frappe.msgprint(_("Source Warehouses: {0}").format(source_warehouses))  # Debug statement

            for source_warehouse in source_warehouses:
                # Filter items that have the item group "Fuel" for the current warehouse
                fuel_items = [
                    item for item in doc.get("items")
                    if item.get("item_group") == "Fuel" and item.get("s_warehouse") == source_warehouse
                ]

                # frappe.msgprint(_("Fuel Items for {0}: {1}").format(source_warehouse, fuel_items))  # Debug statement

                if fuel_items:
                    # Get the total quantity for the current item
                    total_quantity = sum([item.get("qty") for item in fuel_items])

                    # Get the present reading value from the Meter Readings doctype
                    meter_reading = frappe.get_all(
                        "Meter Readings", filters={"pump": source_warehouse}, 
                        fields=["initial_reading_value", "present_reading_value"]
                    )

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
                    pump_meter_reading.branch = fuel_items[0].get("cost_center")  # Assuming cost_center is at item level
                    pump_meter_reading.date = now_datetime()
                    pump_meter_reading.pump_date = doc.posting_date
                    pump_meter_reading.cost_center = fuel_items[0].get("cost_center")  # Assuming cost_center is at item level
                    pump_meter_reading.employee = frappe.session.user
                    pump_meter_reading.employer_name = frappe.get_value("User", frappe.session.user, "full_name")
                    pump_meter_reading.stock_entry_transfer_id = doc.name
                    pump_meter_reading.pump = source_warehouse
                    pump_meter_reading.present_reading_value = present_reading_value
                    pump_meter_reading.current_reading_value = current_reading_value
                    pump_meter_reading.stock_entry_posting_date = doc.posting_date

                    # Insert the document
                    pump_meter_reading.insert()

                    qty_pernow = current_reading_value - initial_reading_value
                    # Submit the Pump Meter Reading
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

def cancel_stock_entry_meter_reading(doc, method=None):
    try:
        if doc.doctype == "Stock Entry":
            if doc.stock_entry_type == "Material Transfer":
                source_warehouses = set([
                    item.get("s_warehouse")
                    for item in doc.get("items")
                    if frappe.get_value("Warehouse", item.get("s_warehouse"), "warehouse_type") == "Pump"
                ])

                for source_warehouse in source_warehouses:
                    fuel_items = [
                        item for item in doc.get("items")
                        if item.get("item_group") == "Fuel" and item.get("s_warehouse") == source_warehouse
                    ]

                    if fuel_items:
                        total_quantity = sum([item.get("qty") for item in fuel_items])

                        meter_reading = frappe.get_all(
                            "Meter Readings", filters={"pump": source_warehouse},
                            fields=["initial_reading_value", "present_reading_value"]
                        )

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

                        frappe.db.set_value("Meter Readings", {"pump": source_warehouse}, {
                            "present_reading_value": current_reading_value,
                            "qty_as_per_now": qty_pernow,
                            "current_date": now_datetime()
                        })

            # frappe.msgprint(_("Pump Meter Reading updated successfully"))

    except Exception as e:
        frappe.log_error(_("Error updating Pump Meter Reading on stock entry cancel: {0}").format(e))
        frappe.throw(_("Error updating Pump Meter Reading on stock entry cancel. Please try again."))
