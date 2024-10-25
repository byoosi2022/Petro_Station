// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Fuel Card", {
// 	refresh(frm) {

// 	},
// });

// Client Script for generating custom series on form load or before save
frappe.ui.form.on('Fuel Card', {
    before_save: function(frm) {
        // Check if custom_serie is already set
        if (frm.doc.custom_serie) {
            // If custom_serie is already set, do not change it
            return;
        }

        // Get current date in MMDD-YYYY format
        let today = moment().format('MMDD-YYYY');

        // Initialize series parts
        let last_part_9999 = 9999;  // Starting value for the reducing part
        let last_part_0000 = 1;      // Starting value for the increasing part (changed to 1)

        // Fetch the last created document with the custom_serie field (if available)
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Fuel Card',
                fields: ['custom_serie'],
                limit: 1,
                order_by: 'creation desc'
            },
            callback: function(response) {
                let last_doc = response.message;

                // Check if the last document exists and has custom_serie field
                if (last_doc.length > 0 && last_doc[0].custom_serie) {
                    let last_series = last_doc[0].custom_serie;

                    // Extract the 9999-0000 parts from the last series (MMDD-YYYY-9999-0000)
                    let parts = last_series.split('-');
                    if (parts.length === 4) {
                        last_part_9999 = parseInt(parts[2]);  // Decreasing part (9999)
                        last_part_0000 = parseInt(parts[3]);  // Increasing part (0000)
                    }
                    
                    // Increment the 0000 part
                    if (last_part_0000 < 9999 && last_part_9999 > 0) {
                        last_part_0000 += 1;  // Increase 0000
                        last_part_9999 -= 1;  // Decrease 9999
                    } else if (last_part_0000 === 9999 && last_part_9999 > 0) {
                        last_part_0000 = 1;   // Reset 0000 to 1
                        last_part_9999 -= 1;  // Decrease 9999
                    }

                    // Check to ensure 9999 part doesn't go below 0
                    if (last_part_9999 < 0) {
                        frappe.throw(__('Series has reached its minimum limit.'));
                    }
                }

                // Format and set the custom series field in the form
                let custom_series = `${today}-${last_part_9999.toString().padStart(4, '0')}-${last_part_0000.toString().padStart(4, '0')}`;
                frm.set_value('custom_serie', custom_series);
            }
        });
    }
});

