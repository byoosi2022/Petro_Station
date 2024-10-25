// Copyright (c) 2024, Mututa Paul and contributors  
// For license information, please see license.txt  


frappe.ui.form.on('Station Shift Management', {
    station: function (frm) {
        frappe.call({
            method: 'petro_station_app.custom_api.api.get_details_tanks',
            args: {
                station: frm.doc.station,
            },
            callback: function (r) {
                if (r.message) {
                    var items = r.message; // Assign the returned items

                    if (items && Array.isArray(items)) {
                        // Clear existing items before populating (optional)
                        frm.clear_table('dipping_details');

                        // Loop through each item in the response
                        for (var i = 0; i < items.length; i++) {
                            var new_item = frm.add_child('dipping_details'); // Create a new child row

                            // Set values from response to new item fields
                            new_item.tank = items[i].name;
                            new_item.item = items[i].custom_tank_item;
                            // Add other relevant fields here
                        }

                        frm.refresh_field('dipping_details'); // Refresh the child table view after the loop
                    } else {
                        frappe.msgprint("No items data found in response.");
                    }
                }
            }
        });
        frappe.call({
            method: 'petro_station_app.custom_api.api.get_details_cost_center',
            args: {
                station: frm.doc.station,
            },
            callback: function (r) {
                if (r.message) {
                    var items = r.message; // Assign the returned items

                    if (items && Array.isArray(items)) {
                        // Clear existing items before populating (optional)
                        frm.clear_table('items');

                        // Loop through each item in the response
                        for (var i = 0; i < items.length; i++) {
                            var new_item = frm.add_child('items'); // Create a new child row

                            // Set values from response to new item fields
                            new_item.pump_or_tank = items[i].name;
                            // Add other relevant fields here
                        }

                        frm.refresh_field('items'); // Refresh the child table view after the loop
                    } else {
                        frappe.msgprint("No items data found in response.");
                    }
                }
            }
        });

        frappe.call({
            method: 'petro_station_app.custom_api.api.get_details_employee',
            args: {
                station: frm.doc.station,
            },
            callback: function (r) {
                if (r.message) {
                    var items = r.message; // Assign the returned items

                    if (items && Array.isArray(items)) {
                        // Clear existing items before populating (optional)
                        frm.clear_table('attendance');

                        // Loop through each item in the response
                        for (var i = 0; i < items.length; i++) {
                            var new_item = frm.add_child('attendance'); // Create a new child row

                            // Set values from response to new item fields
                            new_item.employee = items[i].name;
                            new_item.employee_name = items[i].employee_name;
                            new_item.designation = items[i].designation;

                            // Add other relevant fields here
                        }

                        frm.refresh_field('attendance'); // Refresh the child table view after the loop
                    } else {
                        frappe.msgprint("No items data found in response.");
                    }
                }
            }
        });

        frappe.call({
            method: 'petro_station_app.custom_api.api.get_gl_acount_withoutdate',
            args: {
                station: frm.doc.station,
            },
            callback: function (r) {
                if (r.message) {
                    var accounts = r.message; // Assign the returned accounts

                    // Clear existing items before populating (optional)
                    frm.clear_table('accounts');

                    // Loop through each key in the response
                    for (var key in accounts) {
                        if (accounts.hasOwnProperty(key)) {
                            var account_data = accounts[key];
                            var new_item = frm.add_child('accounts'); // Create a new child row

                            // Set values from response to new item fields
                            new_item.account = account_data.account;
                            new_item.amount_recived = account_data.total_debits;
                            new_item.amount_spent = account_data.total_credits;
                            new_item.available_amount = account_data.total_debits - account_data.total_credits;

                            // Add other relevant fields here
                        }
                    }

                    frm.refresh_field('accounts'); // Refresh the child table view after the loop
                } else {
                    frappe.msgprint("No accounts data found in response.");
                }
            }
        });
        populateInvoiceItems(frm);

        populateCashTransferTable(frm);
        fetchStockTransfersDraft(frm)

        populateExpenditureTable344(frm);
    },
    get_dipping_levels: function (frm) {
        fetcheDippingLevels(frm);
        
        // postStockReconciliation(frm) 

    },
    get_drafts: function (frm) {
        fetchStockTransfersDraft(frm)
        // postStockReconciliation(frm) get_drafts

    },
    transfer_fuel: function (frm) {
        // Prompt the user for confirmation
        frappe.confirm(
            'Are you sure you want to submit all draft fuel tranfer entries?', // Message to display
            function () {
                // User clicked "Yes"
                submitDraftStockEntries(frm);
            },
            function () {
                // User clicked "No"
                frappe.msgprint('Submission cancelled.'); // Optional message on cancellation
            }
        );
    },
    take_dipping: function (frm) {
        // Prompt the user for confirmation
        frappe.confirm(
            'Are you sure you want to take the dipping levels?', // Message to display
            function () {
                // User clicked "Yes"
                postStockReconciliation(frm);
            },
            function () {
                // User clicked "No"
                frappe.msgprint('Submission cancelled.'); // Optional message on cancellation
            }
        );
    },

    get_pump_details: function (frm) {
        fetchSalesDetails(frm);
    },
    get_all_shift_details: function (frm) {
        populateInvoiceItemsStockEntry(frm);
    },

    get_bankings_and_cash: function (frm) {
        // getBankingandCash(frm);
        getBankingandCashwithoutdate(frm);
    },

    get_for_todaty: function (frm) {
        getBankingandCash(frm);
        // getBankingandCashwithoutdate(frm);
    },
    get_invoice_details: function (frm) {
        populateInvoiceItems(frm);
    },

    get_all_transfers_for_today: function (frm) {
        populateCashTransferTable(frm);
    },

    get_all_expense_for_today: function (frm) {
        populateExpenditureTable344(frm);
    },

    before_submit: function (frm) {
        // Check if the items table is set and has items
        if (frm.doc.items && frm.doc.items.length > 0) {
            // Array to store promises for validation
            let validations = frm.doc.items.map((item, i) => {
                return new Promise((resolve, reject) => {
                    // Get the warehouse type for the current item.pump_or_tank
                    frappe.db.get_value('Warehouse', item.pump_or_tank, 'warehouse_type', (r) => {
                        if (r && r.warehouse_type !== 'Store') {
                            // Get the relevant values for the current row
                            let opening = item.opening_meter_reading;
                            let closing = item.closing_meter_reading;
                            let current_reading = item.current_reading_value;
                            let qty_based_on_sales = item.qty_based_on_sales;
                            let qty_sold_on_meter_reading = item.qty_sold_on_meter_reading;
                            let sales_based_on_invoices = item.sales_based_on_invoices;
                            let sales_based_on_meter_reading = item.sales_based_on_meter_reading;

                            // Tolerance for floating-point comparison
                            let tolerance = 1000.000;

                            // Check if the opening_meter_reading is zero
                            if (opening === 0) {
                                // Notify the user and prevent saving
                                frappe.msgprint(__('Row {0}: Opening Meter Reading cannot be zero. Please enter a valid reading.', [i + 1]));
                                resolve(false);
                            }

                            // Check if the closing_meter_reading does not equal the current_reading_value
                            if (Math.abs(closing - current_reading) > tolerance) {
                                // Notify the user and prevent saving
                                frappe.msgprint(__('Row {0}: Your Closing Meter Reading ({1}) is not equal to the Recent System Meter Reading ({2}). Please make sure you put more sales in the system or there are double sales entries. Make sure you Cross-check before closing this shift.', [i + 1, closing.toFixed(3), current_reading.toFixed(3)]));
                                resolve(false);
                            }

                            // Check if the qty_based_on_sales does not equal the qty_sold_on_meter_reading
                            if (Math.abs(qty_based_on_sales - qty_sold_on_meter_reading) > tolerance) {
                                // Notify the user and prevent saving
                                frappe.msgprint(__('Row {0}: Your Quantity Based on Sales ({1}) is not equal to the Quantity Sold on Meter Reading ({2}). Please make sure you put more sales in the system or there are double sales entries. Make sure you Cross-check before closing this shift.', [i + 1, qty_based_on_sales.toFixed(3), qty_sold_on_meter_reading.toFixed(3)]));
                                resolve(false);
                            }

                            // Check if the sales_based_on_invoices does not equal the sales_based_on_meter_reading
                            if (Math.abs(sales_based_on_invoices - sales_based_on_meter_reading) > tolerance) {
                                // Notify the user and prevent saving
                                frappe.msgprint(__('Row {0}: Your Sales Based on Invoices ({1}) is not equal to the Sales Based on Meter Reading ({2}). Please make sure you put more sales in the system or there are double sales entries. Make sure you Cross-check before closing this shift.', [i + 1, sales_based_on_invoices.toFixed(3), sales_based_on_meter_reading.toFixed(3)]));
                                resolve(false);
                            }

                            resolve(true); // Validation passed for this item
                        } else {
                            resolve(true); // Warehouse type is Store or not found, skip validation for this item
                        }
                    });
                });
            });

            // Wait for all validations to complete
            Promise.all(validations).then(results => {
                // If any validation failed, set frappe.validated to false
                if (results.includes(false)) {
                    frappe.validated = false;
                } else {
                    frappe.validated = true;
                }
            }).catch(err => {
                console.error(err);
                frappe.validated = false;
            });
        }
        
    },


    get_calculations: function (frm) {
        CalculateTotal(frm);
    },

    before_load: function (frm) {
        // Set the from_date to the day before today when creating a new document
        if (frm.is_new()) {
            let today = frappe.datetime.get_today();
            let from_date = frappe.datetime.add_days(today, -1);
            frm.set_value('from_date', from_date);
        }
    }

});

frappe.ui.form.on('Station Shift Management item', {
    opening_meter_reading: function (frm, cdt, cdn) {
        calculateQtySold(frm, cdt, cdn);
    },
    closing_meter_reading: function (frm, cdt, cdn) {
        calculateQtySold(frm, cdt, cdn);
        updateTheCurentReading(frm, cdt, cdn)
    },
    pump_rate: function (frm, cdt, cdn) {
        calculateQtySold(frm, cdt, cdn);
    }
});
frappe.ui.form.on('Dipping Items', {
    dipping_qty: function (frm, cdt, cdn) {
        calculateAmountOnDipping(frm, cdt, cdn);
    }
});

function calculateQtySold(frm, cdt, cdn) {
    // Get the specific child table row being edited
    let row = locals[cdt][cdn];

    // Calculate the quantity sold on meter reading for the current row difference_amount
    row.qty_sold_on_meter_reading = row.closing_meter_reading - row.opening_meter_reading;
    row.sales_based_on_meter_reading = row.pump_rate * row.qty_sold_on_meter_reading;
    row.difference_amount = row.sales_based_on_meter_reading - row.sales_based_on_invoices;
    // Refresh the field in the current row
    frm.refresh_field('items');

    // Optionally, refresh only the specific row
    frm.refresh_field('qty_sold_on_meter_reading', row.name);
}

function updateTheCurentReading(frm, cdt, cdn) {
    // Get the specific child table row being edited petro_station_app.custom_api.api.get_system_reading
    let row = locals[cdt][cdn];
    frappe.call({
        method: "petro_station_app.custom_api.api.get_system_reading",
        args: {
            pump: row.pump_or_tank,
            from_date: frm.doc.from_date // Pass the list of pump_or_tank values
        },
        callback: function (response) {
            if (response.message) {
                row.current_reading_value = response.message;
                if (row.closing_meter_reading !== row.current_reading_value) {

                    frappe.msgprint(__('Last Meter Reading not equal to your Closing Meter Reading, You Might be missing to enter some sells in the System Please enter them'));
                }
                // Refresh the field in the current row
                frm.refresh_field('items');
                // Optionally, refresh only the specific row
                frm.refresh_field('current_reading_value', row.name);

            }

        },
        error: function (err) {
            // Handle server call error
            console.log(err);
            frappe.msgprint(__('Error fetching data. Please try again later.'));
        }
    });

}


function fetchSalesDetails(frm) {
    // Clear specific fields in existing items
    frm.doc.items.forEach(item => {
        item.qty_based_on_sales = null;
        item.sales_based_on_invoices = null;
        item.pump_rate = null;
        item.sales_based_on_meter_reading = null;
        item.difference_amount = null;
    });

    let pumpOrTankList = frm.doc.items.map(item => item.pump_or_tank);

    frappe.call({
        method: "petro_station_app.custom_api.api.get_total_qty_and_amount",
        args: {
            station: frm.doc.station,
            status: frm.doc.status,
            from_date: frm.doc.from_date,
            to_date: frm.doc.to_date,
            pump_or_tank_list: pumpOrTankList // Pass the list of pump_or_tank values
        },
        callback: function (response) {
            if (response && response.message) {
                // console.log(response.message);
                if (Object.keys(response.message.warehouses).length === 0) {
                    frappe.msgprint(__('No Data Found'));
                } else {
                    // Update specific fields with new data
                    frm.doc.items.forEach(item => {
                        if (response.message.warehouses[item.pump_or_tank]) {
                            let warehouseData = response.message.warehouses[item.pump_or_tank];
                            item.qty_based_on_sales = warehouseData.qty;
                            item.sales_based_on_invoices = warehouseData.amount;
                            item.pump_rate = warehouseData.average_rate;
                            item.sales_based_on_meter_reading = item.pump_rate * item.qty_sold_on_meter_reading;
                            item.difference_amount = item.sales_based_on_meter_reading - item.sales_based_on_invoices;
                        } else {
                            item.qty_based_on_sales = null;
                            item.sales_based_on_invoices = null;
                            item.pump_rate = null;
                            item.sales_based_on_meter_reading = null;
                            item.difference_amount = null;
                        }
                    });

                    // Refresh the items table to reflect the changes
                    let percentaget_discount = ((response.message.additional_discount_amount / response.message.grand_total) * 100).toFixed(2) + '%';
                    // Set and refresh the specified fields
                    frm.set_value('total_discount', response.message.additional_discount_amount);
                    frm.refresh_field('total_discount');
                    frm.set_value('total_sales', response.message.grand_total);
                    frm.refresh_field('total_sales');
                    frm.set_value('total_credit_sales', response.message.outstanding_amount);
                    frm.refresh_field('total_credit_sales');
                    frm.set_value('total_cash_sales', response.message.total_payments);
                    frm.refresh_field('total_cash_sales');
                    frm.set_value('percentaget_discount', percentaget_discount);
                    frm.refresh_field('percentaget_discount');
                    frm.refresh_field("items");

                }
            } else {
                // Handle error or unexpected response
                frappe.msgprint(__('Error fetching data. Please try again later.'));
            }
        },
        error: function (err) {
            // Handle server call error
            console.log(err);
            frappe.msgprint(__('Error fetching data. Please try again later.'));
        }
    });
}

function CalculateTotal(frm) {
    let pumpOrTankList = frm.doc.items.map(item => item.pump_or_tank);
    frm.doc.total_sales = null;
    frm.doc.total_cash_sales = null;
    frm.doc.percentaget_discount = null;

    frappe.call({
        method: "petro_station_app.custom_api.api.get_total_qty_and_amount",
        args: {
            station: frm.doc.station,
            status: frm.doc.status,
            from_date: frm.doc.from_date,
            to_date: frm.doc.to_date,
            pump_or_tank_list: pumpOrTankList // Pass the list of pump_or_tank values
        },
        callback: function (response) {
            if (response && response.message) {
                // console.log(response.message);
                if (Object.keys(response.message).length === 0) {
                    frappe.msgprint(__('No Data Found'));
                } else {
                    // Refresh the items table to reflect the changes
                    // Refresh the items table to reflect the changes
                    // Refresh the items table to reflect the changes
                    // Refresh the items table to reflect the changes
                    let percentaget_discount = ((response.message.additional_discount_amount / response.message.total_payments) * 100).toFixed(2);
                    percentaget_discount = isNaN(percentaget_discount) ? '0%' : percentaget_discount + '%';

                    // Set and refresh the specified fields
                    frm.set_value('total_discount', response.message.additional_discount_amount);
                    frm.refresh_field('total_discount');
                    frm.set_value('total_sales', response.message.grand_total);
                    frm.refresh_field('total_sales');
                    frm.set_value('total_credit_sales', response.message.outstanding_amount);
                    frm.refresh_field('total_credit_sales');
                    frm.set_value('total_cash_sales', response.message.total_payments);
                    frm.refresh_field('total_cash_sales');
                    frm.set_value('percentaget_discount', percentaget_discount);
                    frm.refresh_field('percentaget_discount');
                    frm.refresh_field("items");

                }
            } else {
                // Handle error or unexpected response
                frappe.msgprint(__('Error fetching data. Please try again later.'));
            }
        },
        error: function (err) {
            // Handle server call error
            console.log(err);
            frappe.msgprint(__('Error fetching data. Please try again later.'));
        }
    });
}

function getBankingandCash(frm) {

    frappe.call({
        method: 'petro_station_app.custom_api.api.get_gl_acount',
        args: {
            station: frm.doc.station,
            from_date: frm.doc.from_date,
        },
        callback: function (r) {
            if (r.message) {
                var accounts = r.message; // Assign the returned accounts

                // Clear existing items before populating (optional)
                frm.clear_table('accounts');

                // Loop through each key in the response
                for (var key in accounts) {
                    if (accounts.hasOwnProperty(key)) {
                        var account_data = accounts[key];
                        var new_item = frm.add_child('accounts'); // Create a new child row

                        // Set values from response to new item fields
                        new_item.account = account_data.account;
                        new_item.amount_recived = account_data.total_debits;
                        new_item.amount_spent = account_data.total_credits;
                        new_item.available_amount = account_data.total_debits - account_data.total_credits;

                        // Add other relevant fields here
                    }
                }

                frm.refresh_field('accounts'); // Refresh the child table view after the loop
            } else {
                frappe.msgprint("No accounts data found in response.");
            }
        }
    });


}

function getBankingandCashwithoutdate(frm) {

    frappe.call({
        method: 'petro_station_app.custom_api.api.get_gl_acount_withoutdate',
        args: {
            station: frm.doc.station,
            //  from_date: frm.doc.from_date,
        },
        callback: function (r) {
            if (r.message) {
                var accounts = r.message; // Assign the returned accounts

                // Clear existing items before populating (optional)
                frm.clear_table('accounts');

                // Loop through each key in the response
                for (var key in accounts) {
                    if (accounts.hasOwnProperty(key)) {
                        var account_data = accounts[key];
                        var new_item = frm.add_child('accounts'); // Create a new child row

                        // Set values from response to new item fields
                        new_item.account = account_data.account;
                        //new_item.amount_recived = account_data.total_debits;
                        new_item.amount_recived = account_data.total_debits > 1 ? account_data.total_debits : 0;
                        new_item.amount_spent = account_data.total_credits;
                        new_item.available_amount = account_data.total_debits - account_data.total_credits;

                        // Add other relevant fields here
                    }
                }

                frm.refresh_field('accounts'); // Refresh the child table view after the loop
            } else {
                frappe.msgprint("No accounts data found in response.");
            }
        }
    });


}

function validateBankingandCash(frm) {
    if (frm.doc.accounts && frm.doc.accounts.length > 0) {
        // Array to store promises for validation
        let validations = frm.doc.accounts.map((item, i) => {
            return new Promise((resolve, reject) => {
                // Tolerance for floating-point comparison
                let tolerance = 5000.000;

                // Check if the closing_meter_reading does not equal the current_reading_value
                if (Math.abs(closing - current_reading) > tolerance) {
                    // Notify the user and prevent saving
                    frappe.msgprint(__('Row {0}: Your Closing Meter Reading ({1}) is not equal to the Recent System Meter Reading ({2}). Please make sure you put more sales in the system or there are double sales entries. Make sure you Cross-check before closing this shift.', [i + 1, closing.toFixed(3), current_reading.toFixed(3)]));
                    resolve(false);
                } else {
                    resolve(true); // Warehouse type is Store or not found, skip validation for this item
                }
            });
        });

        // Wait for all validations to complete
        Promise.all(validations).then(results => {
            // If any validation failed, set frappe.validated to false
            if (results.includes(false)) {
                frappe.validated = false;
            } else {
                frappe.validated = true;
            }
        }).catch(err => {
            console.error(err);
            frappe.validated = false;
        });
    }
}
function populateInvoiceItems(frm) {
    frappe.call({
        method: 'petro_station_app.custom_api.invoice.get_sales_invoices_with_totals',
        args: {
            cost_center: frm.doc.station,
            posting_date: frm.doc.from_date,
        },
        callback: function (r) {
            // console.log(r)
            if (r.message && r.message.Invoices) {
                var invoices = r.message.Invoices;

                // Clear existing items before populating (optional)
                frm.clear_table('invoice_items');

                // Loop through each invoice in the response
                for (var i = 0; i < invoices.length; i++) {
                    var invoice = invoices[i];
                    var items = invoice.Items; // Assuming Items is an array

                    // Loop through each item in the invoice
                    for (var j = 0; j < items.length; j++) {
                        var item = items[j];
                        var new_item = frm.add_child('invoice_items'); // Create a new child row


                        // Set values from item to new item fields
                        new_item.invoice_id = invoice['Invoice Name'];
                        new_item.date = invoice['Posting Date'];
                        new_item.customer_name = invoice['Customer Name'];
                        new_item.customer = invoice['Customer'];
                        new_item.item_code = item['Item Code'];
                        new_item.quantity = item['Quantity'];
                        new_item.amount = item['Amount'];
                        // Add other relevant fields based on your data structure

                        frm.refresh_field('invoice_items'); // Refresh the child table view after each item
                    }
                }
            } else {
                frappe.msgprint("No valid invoices found in response.");
            }
        },
        error: function (xhr, textStatus, error) {
            console.error('Error fetching invoices:', error);
            frappe.msgprint('Error fetching invoices. Please try again.');
        }
    });
}

function populateCashTransferTable(frm) {
    frappe.call({
        method: 'petro_station_app.custom_api.invoice.get_cash_transfers_with_totals',
        args: {
            cost_center: frm.doc.station,
            posting_date: frm.doc.from_date,
        },
        callback: function (r) {
            // console.log(r)
            if (r.message && r.message.Transfers) {
                var transfers = r.message.Transfers;

                // Clear existing items before populating (optional)
                frm.clear_table('cash_transfers');

                // Loop through each invoice in the response
                for (var i = 0; i < transfers.length; i++) {
                    var transfer = transfers[i];
                    // Loop through each item in the invoice

                    var new_item = frm.add_child('cash_transfers'); // Create a new child row
                    // Set values from item to new item fields
                    new_item.transfer_id = transfer['Transfer Name'];
                    new_item.actual_date = transfer['Posting Date'];
                    new_item.account_banked_to = transfer['Paid To'];
                    new_item.account_paid_from = transfer['Paid From'];
                    new_item.amount_banked = transfer['Paid Amount'];
                    // Add other relevant fields based on your data structure

                    frm.refresh_field('cash_transfers'); // Refresh the child table view after each item

                }
            } else {
                frappe.msgprint("No valid invoices found in response.");
            }
        },
        error: function (xhr, textStatus, error) {
            console.error('Error fetching transfers:', error);
            frappe.msgprint('Error fetching transfers. Please try again.');
        }
    });
}



function populateExpenditureTable344(frm) {
    frappe.call({
        method: 'petro_station_app.custom_api.invoice.get_expense_totals',
        args: {
            cost_center: frm.doc.station,
            posting_date: frm.doc.from_date,
        },
        callback: function (r) {
            // console.log(r);
            if (r.message && r.message.Expenses) {
                var expenses = r.message.Expenses;

                // Clear existing items before populating
                frm.clear_table('expenditures');

                // Loop through each expense in the response
                for (var i = 0; i < expenses.length; i++) {
                    var expense = expenses[i];
                    var items = expense.Items; // Assuming Items is an array

                    // Loop through each item in the expense
                    for (var j = 0; j < items.length; j++) {
                        var item = items[j];
                        var new_item = frm.add_child('expenditures'); // Create a new child row

                        // Set values from item to new item fields
                        new_item.expense_id = expense['Expense Name'];
                        new_item.actual_date = expense['Posting Date'];
                        new_item.account_paid_from = item['Amount'];
                        new_item.description = item['Description'];
                        // Add other relevant fields based on your data structure

                        frm.refresh_field('expenditures'); // Refresh the child table view after each item
                    }
                }
            } else {
                frappe.msgprint("No valid expenses found in response.");
            }
        },
        error: function (xhr, textStatus, error) {
            console.error('Error fetching expenses:', error);
            frappe.msgprint('Error fetching expenses. Please try again.');
        }
    });
}


function populateInvoiceItemsStockEntry(frm) {
    // Clear specific fields in existing items
    frm.doc.items.forEach(item => {
        item.qty_based_on_sales = null;
        item.sales_based_on_invoices = null;
        item.pump_rate = null;
        item.sales_based_on_meter_reading = null;
        item.difference_amount = null;
    });

    let pumpOrTankList = frm.doc.items.map(item => item.pump_or_tank);

    frappe.call({
        method: "petro_station_app.custom_api.invoice_stock.get_total_qty_and_amount",
        args: {
            station: frm.doc.station,
            status: frm.doc.status,
            from_date: frm.doc.from_date,
            to_date: frm.doc.to_date,
            pump_or_tank_list: pumpOrTankList // Pass the list of pump_or_tank values
        },
        callback: function (response) {
            // console.log(response);
            if (response && response.message) {
                console.log(pumpOrTankList);
                if (Object.keys(response.message.warehouses).length === 0) {
                    frappe.msgprint(__('No Data Found'));
                } else {
                    // Update specific fields with new data
                    frm.doc.items.forEach(item => {
                        if (response.message.warehouses[item.pump_or_tank]) {
                            let warehouseData = response.message.warehouses[item.pump_or_tank];
                            item.qty_based_on_sales = warehouseData.qty;
                            item.sales_based_on_invoices = warehouseData.amount;
                            item.pump_rate = warehouseData.average_rate;
                            item.sales_based_on_meter_reading = item.pump_rate * item.qty_sold_on_meter_reading;
                            item.difference_amount = item.sales_based_on_meter_reading - item.sales_based_on_invoices;
                        } else {
                            item.qty_based_on_sales = null;
                            item.sales_based_on_invoices = null;
                            item.pump_rate = null;
                            item.sales_based_on_meter_reading = null;
                            item.difference_amount = null;
                        }
                    });

                    // Refresh the items table to reflect the changes
                    let percentaget_discount = ((response.message.additional_discount_amount / response.message.grand_total) * 100).toFixed(2) + '%';
                    // Set and refresh the specified fields
                    frm.set_value('total_discount', response.message.additional_discount_amount);
                    frm.refresh_field('total_discount');
                    frm.set_value('total_sales', response.message.grand_total);
                    frm.refresh_field('total_sales');
                    frm.set_value('total_credit_sales', response.message.outstanding_amount);
                    frm.refresh_field('total_credit_sales');
                    frm.set_value('total_cash_sales', response.message.total_payments);
                    frm.refresh_field('total_cash_sales');
                    frm.set_value('percentaget_discount', percentaget_discount);
                    frm.refresh_field('percentaget_discount');
                    frm.refresh_field("items");

                }
            } else {
                // Handle error or unexpected response
                frappe.msgprint(__('Error fetching data. Please try again later.'));
            }
        },
        error: function (err) {
            // Handle server call error
            console.log(err);
            frappe.msgprint(__('Error fetching data. Please try again later.'));
        }
    });
}

// new updates in sept 19/9/2024 --- 4:00am

function fetcheDippingLevels(frm) {
    // Get lists of tanks and items from the 'dipping_details' child table
    let TankList = frm.doc.dipping_details.map(item => item.tank);
    let ItemList = frm.doc.dipping_details.map(item => item.item);

    // Ensure there are tanks and items to process
    if (TankList.length > 0 && ItemList.length > 0) {
        // Loop through each item and tank combination
        for (let i = 0; i < ItemList.length; i++) {
            frappe.call({
                method: "erpnext.stock.doctype.stock_reconciliation.stock_reconciliation.get_stock_balance_for",
                args: {
                    item_code: ItemList[i],     // Single item code
                    warehouse: TankList[i],     // Single warehouse (tank)
                    posting_date: frm.doc.from_date,
                    posting_time: frm.doc.time,
                },
                callback: function (r) {
                    console.log(r)
                    if (r.message) {
                        // Find the existing row in the 'dipping_details' child table
                        let existing_row = frm.doc.dipping_details.find(d => d.item === ItemList[i] && d.tank === TankList[i]);
                        // If the row exists, update its values amount 
                        if (existing_row) {
                            existing_row.dipping_qty = r.message.qty;  // Update dipping quantity
                            existing_row.current_qty = r.message.qty;  // Update current quantity
                            existing_row.valuation_rate = r.message.rate;  // Update current quantity
                            existing_row.current_amount = r.message.qty * r.message.rate; 
                            existing_row.amount = r.message.qty * r.message.rate;

                            // tyry
  
                            // // Add any other fields that need to be updated
                        } else {
                            frappe.msgprint(`No matching row found for Item: ${ItemList[i]} and Tank: ${TankList[i]}`);
                        }

                        // Refresh the 'dipping_details' child table to display the updated data
                        frm.refresh_field('dipping_details');
                    } else {
                        frappe.msgprint(`No stock data found for Item: ${ItemList[i]} and Tank: ${TankList[i]}`);
                    }
                }
            });
        }
    } else {
        frappe.msgprint("Please ensure there are tanks and items available in the dipping details.");
    }
}
function postStockReconciliation(frm) {
    // Collect the data from the `dipping_details` child table
    let itemsData = frm.doc.dipping_details.map(item => ({
        item_code: item.item,       // Assuming 'item' is the field with the item code
        warehouse: item.tank,       // Assuming 'tank' is the field with the warehouse
        qty: item.dipping_qty,      // Assuming 'dipping_qty' is the field with quantity
        valuation_rate: item.valuation_rate || 0 // Assuming valuation rate exists (optional)
    }));

    // Check if all dipping_status are set to "Level Taken"
    let allStatusSetToLevelTaken = frm.doc.dipping_details.every(item => item.dipping_status === "Level Taken");

    // If any status is  set to "Level Taken", do not proceed with submission
    if (allStatusSetToLevelTaken) {
        frappe.msgprint("Cannot Take Diping Levels. All fuel dipping levels have been taken");
        return;
    }

    // Make sure there is data to send
    if (itemsData.length === 0) {
        frappe.msgprint("No items to reconcile.");
        return;
    }

    // Call the backend Python function to create the Stock Reconciliation
    frappe.call({
        method: "petro_station_app.custom_api.stock_dipping_levels.stock_reconsilation.create_stock_reconciliation",  // Replace with the correct path to your Python method
        args: {
            items_data: JSON.stringify(itemsData),  // Convert items data to a JSON string
            posting_date: frm.doc.from_date,
            posting_time: frm.doc.time,
            station: frm.doc.station,
            docname:frm.doc.name
        },
        callback: function (response) {
            if (response.message.status === "success") {
                // Optionally update dipping_status to "Level Taken" if needed
                frm.doc.dipping_details.forEach(item => {
                    item.dipping_status = "Level Taken";
                });
                frm.refresh_field('dipping_details'); // Refresh the child table to reflect changes
                frappe.msgprint(response.message.message);  // Show success message
            } else {
                frappe.msgprint("Failed: " + response.message.error);  // Show error message
            }
        }
    });
}


function fetchStockTransfersDraft(frm) {
    frappe.call({
        method: 'petro_station_app.custom_api.stock_dipping_levels.stock_trafers_draft.get_material_transfer_entries', // Make sure this path is correct
        args: {
            station: frm.doc.station, // Pass the station value from your form
        },
        callback: function (r) {
            // console.log(r)
            if (r.message) {
                var items = r.message.data; // Assign the returned items, assuming the response contains a `data` field

                if (items && Array.isArray(items)) {
                    // Clear existing items before populating (optional)
                    frm.clear_table('recieve_stock');

                    // Loop through each item in the response
                    for (var i = 0; i < items.length; i++) {
                        var entry = items[i]; // Get the current item

                        // Create a new child row
                        var new_item = frm.add_child('recieve_stock');

                        // Assuming `entry` contains the fields you need
                        new_item.date = entry.posting_date;  // Example: Assign posting date
                        new_item.time = entry.posting_time;  // Example: Assign posting time (ensure your API returns this)
                        new_item.item = entry.details[0].item_code;      // Example: Assign item code from details
                        new_item.tart_tank = entry.details[0].t_warehouse;    // Example: Assign cost center as tank
                        new_item.dipping_qty = entry.details[0].qty;      // Example: Assign quantity
                        new_item.status = "Draft";     // Example: Assign document status entry.status
                        new_item.voucher = entry.stock_entry;        // Example: Assign voucher number or name
                        new_item.source_tank = entry.details[0].s_warehouse;
                        // Add other relevant fields here if needed
                    }

                    frm.refresh_field('recieve_stock'); // Refresh the child table view after the loop
                } else {
                    frappe.msgprint("No items data found in response.");
                }
            }
        }
    });
}

function submitDraftStockEntries(frm) {
    // Collect all voucher details including received_date and time from the child table
    let voucherList = frm.doc.recieve_stock.map(item => ({
        voucher: item.voucher,             // Assuming 'voucher' is the correct field name
        received_date: item.received_date, // Add the received_date from the child table
        time_recieved: item.time_recieved   // Correct the field name for time
    }));
   
    // Check if any stock transfers are set to "Fuel Transferred"
    let allStatusSetFuelTransferred = frm.doc.recieve_stock.some(item => item.fuel_transfer_status === "Fuel Transferred");

    // If any status is set to "Fuel Transferred", do not proceed with submission
    if (allStatusSetFuelTransferred) {
        frappe.msgprint("Cannot transfer fuel. All fuel transfers have been done.");
        return;
    }

    // Make sure there is data to send
    if (voucherList.length === 0) {
        frappe.msgprint("No vouchers to submit.");
        return;
    }

    // Log the voucher list for debugging
    console.log("Voucher List: ", voucherList);

    // Call the backend function to submit draft stock entries
    frappe.call({
        method: 'petro_station_app.custom_api.stock_dipping_levels.submit_vouchers.submit_draft_stock_entries',
        args: {
            voucher_list: JSON.stringify(voucherList), // Send voucher details as a JSON string
            docname:frm.doc.name
        },
        callback: function (r) {
            if (r.message && r.message.status === "success") {
                // Update fuel_transfer_status to "Fuel Transferred" for all items
                frm.doc.recieve_stock.forEach(item => {
                    item.fuel_transfer_status = "Fuel Transferred";
                });
                frappe.msgprint(r.message.message); // Show success message
                frm.clear_table('recieve_stock');   // Optionally clear the table after submission
                frm.refresh_field('recieve_stock'); // Refresh the field to reflect changes
            } else {
                frappe.msgprint("Error: " + (r.message.error || "Unknown error occurred."));
            }
        },
        error: function(err) {
            frappe.msgprint("Error during submission: " + err.message); // Enhanced error handling
        }
    });
}



function calculateAmountOnDipping(frm, cdt, cdn) {

    // Get the specific child table row being edited
    let row = locals[cdt][cdn];

    // Calculate the quantity sold on meter reading for the current row difference_amount
    row.amount = row.dipping_qty * row.valuation_rate;
    row.quantity_difference = row.dipping_qty - row.current_qty;
    row.amount_difference = row.amount - row.current_amount;

    // Refresh the field in the current row
    frm.refresh_field('dipping_details');

    // Optionally, refresh only the specific row
    frm.refresh_field('amount', row.name);
    frm.refresh_field('quantity_difference', row.name);
    frm.refresh_field('amount_difference', row.name);
}

