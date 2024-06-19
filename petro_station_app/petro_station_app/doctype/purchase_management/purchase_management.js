// Copyright (c) 2024, Mututa Paul and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Management', {
    purchase_items_button: function(frm) {
        update_stock_items(frm);
    },
    before_save: function(frm) {
        // Check if total_qtys exceeds the limit
        if (frm.doc.total_qtys > frm.doc.total_qty) {
            frappe.msgprint("Total quantity of Stock transfer exceeds the limit of the Purchase Items. Please adjust quantities.");
            frappe.validated = false; // Prevent saving
        } else {
            calculateTotalsTransfers(frm);
        }
    }
});

frappe.ui.form.on('Stock transfer Item', {
    qty: function(frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
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
