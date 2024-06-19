import frappe
from frappe import _

@frappe.whitelist()
def create_stock_transfer_server(doc,method=None):
    if isinstance(doc, str):
        doc = frappe.parse_json(doc)

    try:
        if doc.get("doctype") == "Sales Invoice":
            # Check if source_warehouse ends with the company abbreviation
            company_abbr = frappe.get_value("Company", doc.get("company"), "abbr")

            # Flag to track if at least one item with item group 'Fuel' is found
            fuel_item_found = False

            # Create a single Stock Entry for transfer
            stock_entry = frappe.new_doc("Stock Entry")
            stock_entry.stock_entry_type = "Material Transfer"
            
            for item in doc.get("items"):
                if item.get("item_group") == "Fuel":
                    fuel_item_found = True
                    source_warehouse = item.get("warehouse")
                    if f" - {company_abbr}" in source_warehouse:
                        # Remove the company abbreviation
                        source_warehouse_strip = source_warehouse[:-len(f" - {company_abbr}")].strip()
                    else:
                        source_warehouse_strip = source_warehouse

                    warehouse = frappe.get_all("Warehouse", filters={"warehouse_name": source_warehouse_strip}, fields=["default_in_transit_warehouse", "parent_warehouse"])
                    if warehouse:
                        # Get the default in transit warehouse
                        in_transit_warehouse = warehouse[0].get("default_in_transit_warehouse")
                        if not in_transit_warehouse:
                            frappe.throw(_("Transit warehouse not set in Warehouse"))

                        stock_entry.append("items", {
                            "item_code": item.get("item_code"),
                            "qty": item.get("qty"),  # Adjust quantity as needed
                            "uom": item.get("uom"),
                            "s_warehouse": in_transit_warehouse,
                            "t_warehouse": source_warehouse
                        })

            if fuel_item_found:
                stock_entry.insert()
                stock_entry.submit()
                frappe.msgprint(_("Tank to Pump transfer successfully tranfered to the Client"))
    except Exception as e:
        frappe.log_error(_("Error creating stock transfer: {0}").format(e))
        frappe.throw(_("Error creating stock transfer. Please try again."))
