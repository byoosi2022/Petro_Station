// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Fuel Sales App', {
//     after_submit: function(frm) {
//         // Refresh the page
//         location.reload();
//     }
// });
// Custom Script for Fuel Sales App
frappe.ui.form.on('Fuel Sales App', {
    
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Post Expense'), function() {
                frappe.call({
                    method: 'petro_station_app.custom_api.api.create_journal_entry',
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
    additional_discount_amount: function(frm) {
        calculate_and_validate_percentage_discount(frm);
    },
    net_total: function(frm) {
        calculate_and_validate_percentage_discount(frm);
    }

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

function calculate_percentage_discount(frm) {
    if (frm.doc.additional_discount_amount && frm.doc.net_total) {
        let percentage_discount = ((frm.doc.additional_discount_amount / frm.doc.net_total) * 100).toFixed(2);
        let cent = isNaN(percentage_discount) ? '0%' : percentage_discount + '%';
        frm.set_value('percentge_discount', cent);
    } else {
        frm.set_value('percentge_discount', '0%');
    }
}

function calculate_and_validate_percentage_discount(frm) {
    // Calculate percentage discount
    calculate_percentage_discount(frm);

    // Get percentage discount value
    let percentage_discount_value = parseFloat(frm.doc.percentge_discount);

    // Validate if percentage discount exceeds 10%
    if (percentage_discount_value > 10) {
        frappe.msgprint(__('Percentage Discount cannot exceed 10%.'));
        return;
    }

    // Save the form
    // frm.save()
    //     .then(() => {
    //         frappe.msgprint(__('Percentage Discount calculated and saved.'));
    //     })
    //     .catch(err => {
    //         frappe.msgprint(__('There was an error saving the document.'));
    //         console.error(err);
    //     });
}
