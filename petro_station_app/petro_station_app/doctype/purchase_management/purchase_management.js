// Copyright (c) 2024, Mututa Paul and contributors
// For license information, please see license.txt  
// /home/byoosi/fahaab/apps/petro_station_app/petro_station_app/petro_station_app/doctype/purchase_management/purchase_management.py
frappe.ui.form.on('Purchase Management', {
    refresh: function(frm) {
        // Call the function to toggle the usd_exchange_rate field visibility
        toggle_usd_exchange_rate(frm);
    },
    currency: function(frm) {
        // Call the function to toggle the usd_exchange_rate field visibility
        toggle_usd_exchange_rate(frm);
    },

    purchase_items_button: function(frm) {
        update_stock_items(frm);
        update_actual_qty(frm)
    },
    before_save: function(frm) {
        // Check if total_qtys exceeds the limit
        if (frm.doc.total_qtys > frm.doc.total_qty) {
            frappe.msgprint("Total quantity of Stock transfer exceeds the limit of the Purchase Items. Please adjust quantities.");
            frappe.validated = false; // Prevent saving
        } else {
            calculateTotalsTransfers(frm);
        }
    },

    validate: function(frm) {
        // Check if the stock_items table is set
        if (frm.doc.stock_items && frm.doc.stock_items.length > 0) {
            // Iterate through each item in the stock_items table
            for (let i = 0; i < frm.doc.stock_items.length; i++) {
                let item = frm.doc.stock_items[i];

                // Get the qty and capacity_need_for_transfer for the current row
                let qty = item.qty;
                let capacityNeedForTransfer = item.capacity_need_for_transfer;

                // Check if the quantity exceeds the capacity need for transfer
                if (qty > capacityNeedForTransfer) {
                    // Notify the user and prevent saving
                    frappe.msgprint(__('Row {0}: The quantity ({1}) exceeds the capacity needed for transfer ({2}). Please adjust the quantity.', [i + 1, qty, capacityNeedForTransfer]));
                    frappe.validated = false; // Prevent saving
                    return; // Exit the loop and validation function
                }
            }
        }
        if (frm.doc.other_items) {
            // Iterate through each item in the stock_items table
            for (let i = 0; i < frm.doc.other_items.length; i++) {
                let item = frm.doc.other_items[i];

                // Get the rate and for the current row
                let rate = item.rate;
                // Check if the rate if the rate i less than zero
                if (rate < 0) {
                    // Notify the user and prevent saving
                    frappe.msgprint(__('Row {0}: The rate ({1}) can not be less or equal to zero ({2}). Please adjust the quantity.', [i + 1, qty, capacityNeedForTransfer]));
                    frappe.validated = false; // Prevent saving
                    return; // Exit the loop and validation function
                }
            }
        }
    }
});

frappe.ui.form.on('Stock transfer Item', {
    qty: function(frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
    },
    target_store: function(frm, cdt, cdn) {
        update_actual_qty(frm)
    }
});

function calculateTotalsTransfers(frm) {
    var total_qty = 0;
    frm.doc.stock_items.forEach(function(item) {
        total_qty += item.qty;
    });
    frm.set_value('total_qtys', total_qty);
    refresh_field('total_qtys'); // Refresh the total_qtys field
}

function update_stock_items(frm) {
    // Initialize total_qty
    let total_qty = 0;

    // Clear existing rows in stock_items table
    frm.clear_table('stock_items');

    // Loop through each item in the items table
    frm.doc.items.forEach(item => {
        // Create a new row in the stock_items table
        let new_row = frm.add_child('stock_items');

        // Copy fields from items to stock_items
        new_row.item = item.item;
        new_row.accepted_warehouse = item.warehouse;
        new_row.qty = item.qty;
        new_row.cost_center = item.cost_center;

        // Add the item's qty to the total_qty
        total_qty += item.qty;
    });

    // Set the total_qty in the doc
    frm.set_value('total_qtys', total_qty);

    // Refresh the stock_items table to show the new rows or updated quantities
    frm.refresh_field('stock_items');
}

function update_actual_qty(frm) {
    frm.doc.stock_items.forEach(item => {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Bin',
                filters: {
                    item_code: item.item_code,
                    warehouse: item.target_store
                },
                fieldname: 'actual_qty'
            },
            callback: function(response) {
                if (response.message) {
                    item.item_actual_qty = response.message.actual_qty;
                    item.capacity_need_for_transfer = item.tank_fuel_copacity - item.item_actual_qty
                } else {
                    item.item_actual_qty = 0;
                }
                frm.refresh_field('stock_items');
            }
        });
    });
}

// Function to toggle the visibility of the usd_exchange_rate field
function toggle_usd_exchange_rate(frm) {
    if (frm.doc.currency === 'UGX') {
        frm.set_df_property('usd_exchange_rate', 'hidden', true);
    } else {
        frm.set_df_property('usd_exchange_rate', 'hidden', false);
    }
}