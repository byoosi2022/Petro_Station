// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Station Supplies Expenses", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Station Supplies Expenses', {
    onload: function(frm) {
        // Check the initial state of is_paid
        toggle_payment_fields(frm);
    },
    is_paid: function(frm) {
        // Toggle the visibility and mandatory status of fields based on the value of is_paid
        toggle_payment_fields(frm);
    },
    validate: function(frm) {
        // Check if paid_amount is zero when is_paid is checked
        if (frm.doc.is_paid && frm.doc.paid_amount == 0) {
            frappe.msgprint(__('Paid Amount cannot be zero.'));
            frappe.validated = false;
        }
    }
});

function toggle_payment_fields(frm) {
    // Toggle the visibility of fields based on the value of is_paid
    frm.toggle_display(['mode_of_payment', 'paid_amount'], frm.doc.is_paid);
    // Set fields as mandatory if is_paid is checked
    frm.toggle_reqd('mode_of_payment', frm.doc.is_paid);
    frm.toggle_reqd('paid_amount', frm.doc.is_paid);
}


frappe.ui.form.on('Station Supplies Expenses Items', {
    qty: function (frm, cdt, cdn) {
        calculateTotals(frm);
    },
    rate: function (frm, cdt, cdn) {
        calculateTotals(frm);
    }
});

function calculateTotals(frm) {
    var grand_total = 0;
    frm.doc.items.forEach(function(item) {
        item.amount = item.qty * item.rate;
       grand_total += item.amount;
    });
    frm.set_value('grand_total', grand_total);
    frm.set_value('paid_amount', grand_total);
    refresh_field('items');
}



