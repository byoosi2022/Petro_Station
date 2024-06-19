import frappe

@frappe.whitelist()
def get_item_price(item_code, uom, price_list):
    item = frappe.get_doc("Item", item_code)
    price_rate = frappe.db.get_value('Item Price', {
        'selling': '1', 
        'uom': uom, 
        'item_code': item_code, 
        "price_list":price_list
        }, 'price_list_rate')
    if item:
        return price_rate
    return None
