# Custom Script for Doctype - MMDD-YYYY-9999-0000 in custom_series field
import frappe
from datetime import datetime

# Initialize global counters (decreasing and increasing)
last_part_9999 = 9999
last_part_0000 = 0

def custom_naming(doc, method):
    global last_part_9999, last_part_0000

    # Get the current date in MMDD-YYYY format
    today = datetime.today().strftime('%m%d-%Y')

    # Increment 0000 part
    if last_part_0000 < 9999:
        last_part_0000 += 1
    else:
        # Reset 0000 and decrease 9999 part if 0000 reaches 9999
        last_part_0000 = 0
        if last_part_9999 > 0:
            last_part_9999 -= 1
        else:
            frappe.throw("Series has reached its minimum limit.")

    # Set the generated series in the custom_series field
    doc.custom_series = f"{today}-{str(last_part_9999).zfill(4)}-{str(last_part_0000).zfill(4)}"
    
@frappe.whitelist()   
def fetch_card_details(customer,custom_number):
    fuel_card = frappe.get_doc("Fahaab Fuel Card", {"customer": customer, "custom_serie": custom_number})
    return fuel_card

