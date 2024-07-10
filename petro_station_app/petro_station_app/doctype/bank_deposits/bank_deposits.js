// Copyright (c) 2024, mututa paul and contributors
// For license information, please see license.txt
frappe.ui.form.on("Bank Deposits", {
    before_save: function(frm) {
        // Clear existing items before populating (optional)
        frm.clear_table('items');

        // Fetch accounts with account type "Bank"
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Account",
                filters: {
                    account_type: "Bank"
                },
                fields: ["name", "account_name"] // Fetch the fields you need
            },
            callback: function(response) {
                var accounts = response.message;
                if (accounts) {
                    accounts.forEach(function(account) {
                        var new_item = frm.add_child('items'); // Create a new child row

                        // Set values from response to new item fields
                        new_item.bank = account.name; // Assuming 'bank' field in child table

                        // Add other relevant fields here if needed
                        // new_item.other_field = account.other_field;
                    });
                    frm.refresh_field('items'); // Refresh the child table view after the loop
                }
            }
        });
    }
});

