// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt

frappe.ui.form.on("Station Expenses", {
    onload: function(frm) {
        frappe.call({
            method: 'petro_station_app.custom_api.api.get_filtered_doctype',
            callback: function(response) {
                if (response.message && response.message.length > 0) {
                    var filteredNames = response.message.map(item => item.name);
                    console.log(filteredNames);
                    
                    // Set query for the 'item' field in the 'expense_items' child table
                    frm.set_query('item', 'items', function() {
                        return {
                            filters: {
                                name: ['in', filteredNames]
                            }
                        };
                    });
                    
                    // Set query for the 'party_type' field in the 'expense_items' child table
                    frm.set_query('party_type', 'items', function() {
                        return {
                            filters: {
                                name: ['in', filteredNames]
                            }
                        };
                    });

                    // Refresh the 'expense_items' child table to apply the filters
                    frm.refresh_field('items');
                }
            }
        });
    },
    party: function(frm) {
        if (frm.doc.party && frm.doc.party_type) {
            frappe.call({
                method: "petro_station_app.custom_api.api.get_party_name",
                args: {
                    party_type: frm.doc.party_type,
                    party: frm.doc.party
                },
                callback: function(r) {
                    if(r.message) {
                        frm.set_value('party_name', r.message);
                    }
                }
            });
        }
    }
});

frappe.ui.form.on('Expense Claim Items', {
    amount: function(frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
    }
});

function calculateTotalsTransfers(frm) {
    var total_amount = 0;
    frm.doc.items.forEach(function(item) {
        total_amount += item.amount;
    });
    frm.set_value('grand_total', total_amount);
    refresh_field('grand_total');
}
