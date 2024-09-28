import frappe

@frappe.whitelist()
def get_material_transfer_entries(station):
    try:
        # Fetch Stock Entry records with the required filters
        stock_entries = frappe.get_list('Stock Entry',
            filters={
                'stock_entry_type': 'Material Transfer',
                'docstatus': 0  # Draft status
            },
            fields=['name', 'posting_date', 'posting_time', 'stock_entry_type', 'docstatus'],
            order_by='posting_date desc'
        )
        # Get warehouses with the specified cost center and warehouse types (Transit)
        transit_warehouses = frappe.get_all(
            "Warehouse",
            filters={
                "warehouse_type": "Transit",
                "custom_cost_centre": station,
            },
            fields=["name"]
        )

        # Extract list of transit warehouse names
        transit_warehouse_names = [wh['name'] for wh in transit_warehouses]

        # Filter further to check for cost center in Stock Entry Detail child table
        filtered_entries = []
        for entry in stock_entries:
            stock_entry_details = frappe.get_all('Stock Entry Detail',
                filters={
                    'parent': entry.name,
                    # 'cost_center': station,  # Filter by cost center == station
                    # 's_warehouse': ['in', transit_warehouse_names],  # Source warehouse must be of type Transit
                    't_warehouse': ['in', transit_warehouse_names]   # Target warehouse must be of type Transit
                },
                fields=['name', 'item_code', 's_warehouse', 't_warehouse', 'qty', 'cost_center']
            )

            if stock_entry_details:
                filtered_entries.append({
                    'stock_entry': entry.name,
                    'posting_date': entry.posting_date,
                    'status': entry.docstatus,
                    'posting_time': entry.posting_time,
                    'details': stock_entry_details
                })
        
        if not filtered_entries:
            return {"status": "failed", "message": "No matching Stock Entries found."}
        
        return {"status": "success", "data": filtered_entries}

    except Exception as e:
        # Log error if any and return error response
        frappe.log_error(frappe.get_traceback(), "Stock Entry Fetch Error")
        return {"status": "failed", "error": str(e)}
