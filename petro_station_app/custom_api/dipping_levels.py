import frappe
from frappe import _

@frappe.whitelist()
def get_warehouse_from_tank(tank):
    bin = frappe.get_all("Bin", filters={"Warehouse": tank}, fields=["actual_qty", "item_code"])
    return bin
    