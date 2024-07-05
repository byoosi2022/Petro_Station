// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transfer Cash", {
    before_load: function(frm) {
        // Set the from_date to the day before today when creating a new document
        if (frm.is_new()) {
            let today = frappe.datetime.get_today();
            let from_date = frappe.datetime.add_days(today, -1);
            frm.set_value('banking_date', from_date);
        }
    },
        // validate: function(frm) {
        //     return new Promise((resolve, reject) => {
        //         frappe.call({
        //             method: 'petro_station_app.custom_api.doctype_validate_shitf.validate_station_shift_management',
        //             args: {
        //                 station: frm.doc.station,
        //                 posting_date: frm.doc.dipping_date
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
