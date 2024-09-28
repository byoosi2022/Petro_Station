// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Credit Sales App", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Credit Sales App', {
    refresh: function (frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Post Expense'), function () {
                frappe.call({
                    method: 'petro_station_app.custom_api.api.create_journal_entry_cr',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function (r) {
                        if (!r.exc && r.message) {
                            frappe.msgprint(__('Journal Entry created successfully'));
                            // frm.set_value('je_id', r.message);
                            // frm.save_or_update();
                        }
                    }
                });
            });
       
        }
    },
    before_load: function (frm) {
        // Set the from_date to the day before today when creating a new document
        if (frm.is_new()) {
            let today = frappe.datetime.get_today();
            let from_date = frappe.datetime.add_days(today, -1);
            frm.set_value('date', from_date);
        }
    },
    validate: function(frm) {
        if (frm.doc.has_fuel_card) {
            if (!frm.doc.card_number) {
                frappe.msgprint(__(`Please select the Valid Card Number for ${frm.doc.customer_name}.`));
                frappe.validated = false; // Prevent form submission
            }
        }
    },
    customer: function(frm) {
        // Clear the card field initially
        frm.set_value('pick_the_card', '');
    
        // Always hide the pick_the_card field initially
        frm.toggle_display('pick_the_card', false);
    
        // Get the selected customer
        var cust = frm.doc.customer;
    
        if (cust) {
            // Show loading indicator
            frm.set_df_property('pick_the_card', 'read_only', true); // Disable the field during loading
            frm.toggle_display('pick_the_card', false); // Hide the field
    
            // Call the server to get the list of cards
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Fahaab Fuel Card',
                    filters: {
                        customer: cust,
                        docstatus: 1 // Filter only for submitted records
                    },
                    limit_page_length: 1 // Limit the results to 1 if you only need to check for existence
                },
                callback: function(response) {
                    // Hide loading indicator
                    frm.set_df_property('pick_the_card', 'read_only', false); // Re-enable the field
    
                    if (response.message && response.message.length > 0) {
                        // If cards are found, set the query to filter the pick_the_card field
                        frm.set_query('pick_the_card', function() {
                            return {
                                filters: {
                                    customer: cust,
                                    docstatus: 1 // Ensure we only show submitted cards in the dropdown
                                }
                            };
                        });
    
                        // Show the pick_the_card field if cards exist
                        frm.toggle_display('pick_the_card', true);
                    } else {
                        // If no cards are found, clear the pick_the_card field
                        frm.set_value('pick_the_card', '');
                        
                        // Hide the pick_the_card field (it should already be hidden)
                        frm.toggle_display('pick_the_card', false);
                    }
                }
            });
        } else {
            // If no customer is selected, clear the pick_the_card field and hide it
            frm.set_value('pick_the_card', '');
            frm.toggle_display('pick_the_card', false);
        }
    }
    
    
    

    // has_fuel_card: function (frm) {
    //          // Clear the fields when has_fuel_card is 0 or not set
    //          frm.set_value('card_number', '');
    //          frm.set_value('card', '');
    //          frm.set_value('status', '');
    //          frm.set_value('card_limit', '');
    //          frm.set_value('customers_balance', '');
    //     if (frm.doc.has_fuel_card == 1) {
    //         // Fetching customer-related card details
    //         if (frm.doc.customer) {
    //             frappe.call({
    //                 method: 'frappe.client.get',
    //                 args: {
    //                     doctype: 'Fahaab Fuel Card',
    //                     filters: {
    //                         customer: frm.doc.customer
    //                     }
    //                 },
    //                 callback: function (r) {
    //                     if (r.message) {
    //                         let fuel_card = r.message;

    //                         // Set values from Fahaab Fuel Card to Credit Sales App fields
    //                         frm.set_value('card_number', fuel_card.custom_serie);
    //                         frm.set_value('card', fuel_card.name);
    //                         frm.set_value('status', fuel_card.status);
    //                         frm.set_value('card_limit', fuel_card.card_limit);
    //                         frm.set_value('customers_balance', fuel_card.customers_balance);
    //                     }
    //                 }
    //             });
    //         }
    //     } else {
    //         // Clear the fields when has_fuel_card is 0 or not set
    //         frm.set_value('card_number', '');
    //         frm.set_value('card', '');
    //         frm.set_value('status', '');
    //         frm.set_value('card_limit', '');
    //         frm.set_value('customers_balance', '');
    //     }
    // }


    // validate: function(frm) {
    //     return new Promise((resolve, reject) => {
    //         frappe.call({
    //             method: 'petro_station_app.custom_api.doctype_validate_shitf.validate_station_shift_management',
    //             args: {
    //                 station: frm.doc. station,
    //                 posting_date: frm.doc.date
    //             },
    //             callback: function(r) {
    //                 if (r.message) {

    //                     resolve();

    //                 } else {
    //                     reject(__('Validation failed: No submitted Station Shift Management document found.'));
    //                 }
    //             },
    //             error: function(r) {
    //                 reject(__('Validation failed due to server error.'));
    //             }
    //         });
    //     });
    // }
});




frappe.ui.form.on('Expense Claim Items', {
    amount: function (frm, cdt, cdn) {
        calculateTotalsTransfers(frm);
    }
});
frappe.ui.form.on('Fuel Sales Items', {
    item_code: function (frm, cdt, cdn) {
        var item = frappe.get_doc(cdt, cdn);
        if (frm.doc.price_list) {
            frappe.model.set_value(cdt, cdn, 'price_list', frm.doc.price_list);
        }
    }
});


function calculateTotalsTransfers(frm) {
    var total_qty = 0;
    frm.doc.expense_items.forEach(function (item) {
        total_qty += item.amount;
    });
    frm.set_value('grand_total', total_qty);
    refresh_field('expense_items');
}
