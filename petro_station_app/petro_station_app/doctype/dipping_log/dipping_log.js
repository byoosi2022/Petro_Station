// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt

frappe.ui.form.on("Dipping Log", {
    before_load: function(frm) {
        // Set the dipping_date to the day before today when creating a new document
        if (frm.is_new()) {
            let today = frappe.datetime.get_today();
            let from_date = frappe.datetime.add_days(today, -1);
            let formatted_date = frappe.datetime.str_to_user(from_date);
            // frm.set_value('dipping_date', formatted_date);
    
            // Set the date with current date and time
            let now = new Date();
            let year = now.getFullYear();
            let month = ('0' + (now.getMonth() + 1)).slice(-2); // Months are zero based
            let day = ('0' + now.getDate()).slice(-2);
            let hours = ('0' + now.getHours()).slice(-2);
            let minutes = ('0' + now.getMinutes()).slice(-2);
            let seconds = ('0' + now.getSeconds()).slice(-2);
            let datetime_with_time = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            
            frm.set_value('date', datetime_with_time);
        }
    },
    
    // validate: function(frm) {
    //     return new Promise((resolve, reject) => {
    //         frappe.call({
    //             method: 'petro_station_app.custom_api.doctype_validate_shitf.validate_station_shift_management',
    //             args: {
    //                 station: frm.doc. branch,
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
