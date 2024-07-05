// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Credit Sales App", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Credit Sales App', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Post Expense'), function() {
                frappe.call({
                    method: 'petro_station_app.custom_api.api.create_journal_entry_cr',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
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
    before_load: function(frm) {
        // Set the from_date to the day before today when creating a new document
        if (frm.is_new()) {
            let today = frappe.datetime.get_today();
            let from_date = frappe.datetime.add_days(today, -1);
            frm.set_value('date', from_date);
        }
    },

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
    item_code: function(frm, cdt, cdn) {
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
