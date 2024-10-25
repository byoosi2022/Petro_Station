import frappe

@frappe.whitelist()
def get_item_price_rate(item_code, price_list):
    print(item_code, price_list)  # Check if item_code and price_list are correct
    item_price = frappe.get_all("Item Price", filters={"item_code": item_code, "price_list": price_list}, fields=["price_list_rate"])

    if item_price:
        return item_price[0]["price_list_rate"]
    else:
        return None
    
@frappe.whitelist()
def fetch_details_cost_center(station):
    from_pos_profile = frappe.get_all("POS Profile", filters={"cost_center": station}, fields=["name","custom_fuel","warehouse"])
    from_price_list = frappe.get_all("Price List", filters={"selling": 1, "custom_stattion": station}, fields=["name"])

    if from_pos_profile and from_price_list:
        for profile in from_pos_profile:
            for price in from_price_list:
                item_price = frappe.get_value("Item Price", filters={"price_list": price["name"], "item_code": profile["custom_fuel"]}, fieldname=["price_list_rate"])
                profile["item_price"] = item_price
        return {"from_pos_profile": from_pos_profile, "from_price_list": from_price_list, "price": item_price}
    else:
        return None
    

@frappe.whitelist()
def get_fuel_items():
    # Fetch all items with the item group 'Fuel'
    fuel_items = frappe.get_list(
        'Item', 
        filters={'item_group': 'Fuel'},
        fields=['name']
    )
    return fuel_items

@frappe.whitelist()
def get_filtered_doctype():
    try:
        # Fetch the list of DocTypes filtered by name, ignoring permissions
        filtered_doctype = frappe.get_all(
            'DocType', 
            filters={'name': ['in', ['Supplier', 'Employee']]},
            fields=['name'],
            ignore_permissions=True  # This bypasses the permission check
        )
        return filtered_doctype
    except Exception as e:
        frappe.log_error(f"Error fetching filtered DocTypes: {e}")
        frappe.throw("Failed to fetch the filtered DocTypes. Please try again.")



import frappe
from frappe import _

@frappe.whitelist()
def create_journal_entry(docname):
    fuel_sales_app = frappe.get_doc('Fuel Sales App', docname)
    
    existing_receipt = frappe.get_all("Journal Entry", filters={"custom_fuel_expense_id": fuel_sales_app.name}, limit=1)
    if existing_receipt:
        frappe.msgprint(_("Journal Entry already exists for this Fuel Sales App"))
        return
    
    methods = frappe.get_value("Mode of Payment Account", {"parent": fuel_sales_app.mode_of_payment}, "default_account")
    if not methods:
        frappe.throw(_("No default account found for the mode of payment: {0}").format(fuel_sales_app.mode_of_payment))

    journal_entry = frappe.new_doc('Journal Entry')
    journal_entry.voucher_type = 'Journal Entry'
    journal_entry.company = fuel_sales_app.company
    journal_entry.posting_date = fuel_sales_app.date
    journal_entry.custom_fuel_expense_id = fuel_sales_app.name

    for item in fuel_sales_app.expense_items:
        claim_account = frappe.get_value("Expense Claim Account", {"parent": item.claim_type}, "default_account")
        if not claim_account:
            frappe.throw(_("No default account found for the claim type: {0}").format(item.claim_type))

        # Debit Entry
        journal_entry.append('accounts', {
            'account': "2110 - Creditors - FEU",
            'party_type': item.party_type,
            'party': item.party,
            'description': item.description,
            'debit_in_account_currency': item.amount,
            'credit_in_account_currency': 0,
            'cost_center': fuel_sales_app.station
        })

        # Credit Entry
        journal_entry.append('accounts', {
            'account': methods,
            'debit_in_account_currency': 0,
            'credit_in_account_currency': item.amount,
            'cost_center': fuel_sales_app.station
        })

        # Additional Debit Entry
        journal_entry.append('accounts', {
            'account': "2110 - Creditors - FEU",
            'party_type': item.party_type,
            'description': item.description,
            'party': item.party,
            'debit_in_account_currency': 0,
            'credit_in_account_currency': item.amount,
            'cost_center': fuel_sales_app.station
        })

        # Additional Credit Entry
        journal_entry.append('accounts', {
            'account': claim_account,
            'debit_in_account_currency': item.amount,
            'credit_in_account_currency': 0,
            'cost_center': fuel_sales_app.station
        })

    # Save the journal entry
    journal_entry.save()
    # Uncomment the following line to submit the journal entry
    journal_entry.submit()

    # Set the journal_entry_id in the Fuel Sales App
    # fuel_sales_app.db_set('journal_entry_id', journal_entry.name)

    return journal_entry.name


import frappe
from frappe import _

import frappe
from frappe import _

@frappe.whitelist()
def check_dont_back_date_role():
    user = frappe.session.user
    
    # Check if the user has a Role Profile with 'Don't Back Date' role
    role_profiles = frappe.get_all('Has Role', filters={'parent': user}, fields=['role'])
    
    # Collect roles from Role Profiles
    roles = [r.role for r in role_profiles]
    
    return {"has_role": "Don't Back Date" in roles}

# @frappe.whitelist()
# def validate_sales_app_date(doc):
#     # Ensure doc is a dict
#     if not isinstance(doc, dict):
#         frappe.throw(_("Document must be a dictionary"))
    
#     # Get the sale date from the document
#     sale_date = doc.get('date')
    
#     # Get today's date
#     today = frappe.utils.today()
    
#     # Call the role check function
#     has_dont_back_date_role = check_dont_back_date_role()
    
#     # Check if the user has the 'Don't Back Date' role and the date is not today
#     if has_dont_back_date_role.get('has_role') and sale_date != today:
#         frappe.throw(_("You cannot save this document with the sale date set to {0}. Please choose today's date.").format(sale_date))


@frappe.whitelist()
def create_journal_entry_cr(docname):
    fuel_sales_app = frappe.get_doc('Credit Sales App', docname)
    
    existing_receipt = frappe.get_all("Journal Entry", filters={"custom_fuel_expense_id": fuel_sales_app.name}, limit=1)
    if existing_receipt:
        frappe.msgprint(_("Journal Entry already exists for this Fuel Sales App"))
        return
    
    methods = frappe.get_value("Mode of Payment Account", {"parent": fuel_sales_app.mode_of_payment}, "default_account")
    if not methods:
        frappe.throw(_("No default account found for the mode of payment: {0}").format(fuel_sales_app.mode_of_payment))

    journal_entry = frappe.new_doc('Journal Entry')
    journal_entry.voucher_type = 'Journal Entry'
    journal_entry.company = fuel_sales_app.company
    journal_entry.posting_date = fuel_sales_app.date
    journal_entry.custom_credit_sales_app = fuel_sales_app.name

    for item in fuel_sales_app.expense_items:
        claim_account = frappe.get_value("Expense Claim Account", {"parent": item.claim_type}, "default_account")
        if not claim_account:
            frappe.throw(_("No default account found for the claim type: {0}").format(item.claim_type))

        # Debit Entry
        journal_entry.append('accounts', {
            'account': "2110 - Creditors - FEU",
            'party_type': item.party_type,
            'party': item.party,
            'description': item.description,
            'debit_in_account_currency': item.amount,
            'credit_in_account_currency': 0,
            'cost_center': fuel_sales_app.station
        })

        # Credit Entry
        journal_entry.append('accounts', {
            'account': methods,
            'debit_in_account_currency': 0,
            'credit_in_account_currency': item.amount,
            'cost_center': fuel_sales_app.station
        })

        # Additional Debit Entry
        journal_entry.append('accounts', {
            'account': "2110 - Creditors - FEU",
            'party_type': item.party_type,
            'description': item.description,
            'party': item.party,
            'debit_in_account_currency': 0,
            'credit_in_account_currency': item.amount,
            'cost_center': fuel_sales_app.station
        })

        # Additional Credit Entry
        journal_entry.append('accounts', {
            'account': claim_account,
            'debit_in_account_currency': item.amount,
            'credit_in_account_currency': 0,
            'cost_center': fuel_sales_app.station
        })

    # Save the journal entry
    journal_entry.save()
    # Uncomment the following line to submit the journal entry
    journal_entry.submit()

    # Set the journal_entry_id in the Fuel Sales App
    # fuel_sales_app.db_set('journal_entry_id', journal_entry.name)

    return journal_entry.name


@frappe.whitelist()
def get_details_cost_center(station):
    # Get warehouses with the specified cost center and warehouse types
    from_warehouse = frappe.get_all(
        "Warehouse",
        filters={
            "custom_cost_centre": station,
            "warehouse_type": ["in", ["Pump", "Store"]]
        },
        fields=["name"]
    )
    return from_warehouse

@frappe.whitelist()
def get_details_tanks(station):
    # Get warehouses with the specified cost center and warehouse types
    from_warehouse = frappe.get_all(
        "Warehouse",
        filters={
            "custom_cost_centre": station,
            "warehouse_type": ["in", ["Transit"]]
        },
        fields=["name","custom_tank_item"]
    )
    return from_warehouse



@frappe.whitelist()
def get_details_employee(station):
    # Get Employee with the specified cost center 
    fetch_employee = frappe.get_all(
        "Employee",
        filters={
            "payroll_cost_center": station,
             },
        fields=["name","employee_name","designation"]
    )
    return fetch_employee

@frappe.whitelist()
def get_gl_acount(station, from_date=None):
    if not from_date:
        return {"error": "from_date is required"}

    # Get GL Entries with the specified cost center and exclude cancelled entries from the from_date onwards
    fetch_entries = frappe.get_all(
        "GL Entry",
        filters={"cost_center": station, "is_cancelled": 0, "posting_date": (">=", from_date)},
        fields=["name", "debit", "credit", "account"]
    )

    # Dictionary to store the total debits and credits for each account
    account_totals = {}

    # Fetch the associated Account document using the account field from each GL Entry
    for entry in fetch_entries:
        account_doc = frappe.get_doc("Account", entry['account'])
        if account_doc.account_type == "Cash" and account_doc.parent_account != "1141 - SOROTI HQ Cash - FEU":
            if entry['account'] not in account_totals:
                account_totals[entry['account']] = {
                    "account": entry['account'],
                    "total_debits": 0,
                    "total_credits": 0
                }
            account_totals[entry['account']]["total_debits"] += entry['debit']
            account_totals[entry['account']]["total_credits"] += entry['credit']

    # Convert the totals dictionary to a list of values
    result = list(account_totals.values())

    return result

@frappe.whitelist()
def get_gl_acount_withoutdate(station):
    # Get GL Entries with the specified cost center
    fetch_entries = frappe.get_all(
        "GL Entry",
        filters={"cost_center": station,"is_cancelled": 0,},
        fields=["name", "debit", "credit", "account"]
    )

    # Dictionary to store the total debits and credits for each account
    account_totals = {}

    # Fetch the associated Account document using the account field from each GL Entry
    for entry in fetch_entries:
        account_doc = frappe.get_doc("Account", entry['account'])
        if account_doc.account_type == "Cash" and account_doc.parent_account != "1141 - SOROTI HQ Cash - FEU":
            if entry['account'] not in account_totals:
                account_totals[entry['account']] = {
                    "account": entry['account'],
                    "total_debits": 0,
                    "total_credits": 0
                }
            account_totals[entry['account']]["total_debits"] += entry['debit']
            account_totals[entry['account']]["total_credits"] += entry['credit']

    return account_totals


@frappe.whitelist()
def get_total_qty_and_amount(station, from_date, pump_or_tank_list, status=None):
    import json
    from datetime import datetime

    totals = {
        'warehouses': {},
        'grand_total': 0,
        'additional_discount_amount': 0,
        'outstanding_amount': 0,
        'total_payments': 0
    }

    # Convert pump_or_tank_list from JSON string to Python list if necessary
    if isinstance(pump_or_tank_list, str):
        pump_or_tank_list = json.loads(pump_or_tank_list)

    filters = {
        "docstatus": 1,
        "posting_date": from_date,
    }

    if status:
        filters["status"] = status

    sales_invoices = frappe.get_list(
        "Sales Invoice",
        filters=filters,
        fields=["name", "posting_date", "posting_time", "total", "discount_amount", "outstanding_amount"]
    )

    for invoice in sales_invoices:
        invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)

        # Ensure posting_time is in the correct string format before parsing
        posting_time_str = str(invoice_doc.posting_time)

        # Combine posting_date and posting_time to a single datetime
        invoice_posting_datetime = datetime.combine(invoice_doc.posting_date, datetime.strptime(posting_time_str, '%H:%M:%S').time())

        # Check if any item in the invoice has the specified cost_center
        has_matching_item = any(item.cost_center == station for item in invoice_doc.items)

        if has_matching_item:
            # Aggregate grand total and outstanding amount
            totals['grand_total'] += invoice_doc.total
            totals['outstanding_amount'] += invoice_doc.outstanding_amount

            # Aggregate additional discount amount only if outstanding amount is 0
            if invoice_doc.outstanding_amount < 50:
                totals['additional_discount_amount'] += invoice_doc.discount_amount

            # Aggregate total payments from related payment entries
            payment_entries = frappe.get_list(
                "Payment Entry",
                filters={"reference_name": invoice.name, "docstatus": 1},
                fields=["paid_amount"]
            )
            for payment in payment_entries:
                totals['total_payments'] += payment.paid_amount

        for item in invoice_doc.items:
            if item.cost_center == station and item.warehouse in pump_or_tank_list:
                if item.warehouse not in totals['warehouses']:
                    totals['warehouses'][item.warehouse] = {
                        'qty': 0,
                        'amount': 0,
                        'total_rate': 0,
                        'count': 0
                    }

                totals['warehouses'][item.warehouse]['qty'] += item.qty
                totals['warehouses'][item.warehouse]['amount'] += item.amount
                totals['warehouses'][item.warehouse]['total_rate'] += item.rate * item.qty
                totals['warehouses'][item.warehouse]['count'] += item.qty

    # Calculate average rate
    for warehouse, data in totals['warehouses'].items():
        if data['count'] > 0:
            data['average_rate'] = data['total_rate'] / data['count']
        else:
            data['average_rate'] = 0

    return totals

@frappe.whitelist()
def get_system_reading(pump,from_date):
    filters = {
        "docstatus": 1,
        "pump": pump,
        "pump_date": from_date,
    }
    system_meter_readings = frappe.get_list(
        "Pump Meter Reading",
        filters=filters,
        fields=["name", "current_reading_value"],
        order_by="creation desc",  # Order by creation date in descending order to get the most recent reading
        limit=1  # Limit to one document, i.e., the most recent one
    )

    if system_meter_readings:
        return system_meter_readings[0]['current_reading_value']
    else:
        return None  # Handle case where no readings are found

