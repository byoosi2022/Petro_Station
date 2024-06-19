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
