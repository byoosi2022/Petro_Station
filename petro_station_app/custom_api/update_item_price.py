import frappe

@frappe.whitelist()
def update_item_price(doc=None, method=None):
    try:
        for item in doc.get("items"):
            item_code = item.get("item_code")
            rate = item.get("rate")
            price_list = item.get("price_list")
            
            # Get default UOM for the item
            item_doc = frappe.get_doc("Item", item_code)
            uom = item_doc.stock_uom
            
            # Check if Item Price record exists for the item and UOM
            item_price = frappe.get_all("Item Price", filters={"item_code": item_code, "uom": uom, "price_list": price_list})
            
            if not item_price:
                # Create Item Price record if it doesn't exist
                item_price_doc = frappe.new_doc("Item Price")
                item_price_doc.update({
                    "item_code": item_code,
                    "uom": uom,
                    "price_list": price_list,
                    "price_list_rate": rate,
                
                })
                item_price_doc.save(ignore_permissions=True)
                # frappe.msgprint(f"Item price record created for {item_code} with default UOM {uom} and price {sell_price}")
            else:
                # Update existing Item Price record if rate has changed
                for price in item_price:
                    if price.get("price_list_rate") != rate:
                        frappe.db.set_value("Item Price", price.name, {
                            "price_list_rate": rate,
                        })
                        # frappe.msgprint(f"Successfully set item price for {item_code} to {sell_price}")
 
    except Exception as e:
        frappe.log_error(f"Failed to set item prices: {e}")
        frappe.throw("Failed to set item prices. Please try again.")
