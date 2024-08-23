import frappe
from frappe.utils import today

def create_petro_currency_exchange(doc, method):
    # Get the relevant fields from Purchase Management
    date = doc.date
    currency = doc.currency
    usd_exchange_rate = doc.usd_exchange_rate

    # Check if a Petro Currency Exchange with the same date, from_currency, and exchange_rate exists
    existing_exchange = frappe.get_all("Petro Currency Exchange",
                                       filters={
                                           'exchange_rate': usd_exchange_rate
                                       },
                                       limit=1)

    # If not, create a new Petro Currency Exchange 
    if not existing_exchange:
        new_exchange = frappe.get_doc({
            'doctype': 'Petro Currency Exchange',
            'date': date,
            'from_currency': currency,
            'to_currency': "UGX",
            'exchange_rate': usd_exchange_rate
        })
        new_exchange.insert()
        frappe.msgprint("Petro Currency Exchange created successfully.")

# Connect the function to the event
frappe.whitelist()(create_petro_currency_exchange)
