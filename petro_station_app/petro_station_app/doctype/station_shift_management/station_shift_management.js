// Copyright (c) 2024, Mututa Paul and contributors  
// For license information, please see license.txt  


frappe.ui.form.on('Station Shift Management', {
    station: function(frm) {
        frappe.call({
            method: 'petro_station_app.custom_api.api.get_details_cost_center',
            args: {
                station: frm.doc.station,
            },
            callback: function(r) {
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
                        console.log("No items data found in response.");
                    }
                }
            }
        });

        frappe.call({
            method: 'petro_station_app.custom_api.api.get_details_employee',
            args: {
                station: frm.doc.station,
            },
            callback: function(r) {
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
                        console.log("No items data found in response.");
                    }
                }
            }
        });

        frappe.call({
            method: 'petro_station_app.custom_api.api.get_gl_acount_withoutdate',
            args: {
                station: frm.doc.station,
            },
            callback: function(r) {
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
                    console.log("No accounts data found in response.");
                }
            }
        });
        


    },
    get_pump_details: function(frm) {
        fetchSalesDetails(frm);
    },
    get_bankings_and_cash: function(frm) {
        getBankingandCash(frm);
    },

    before_submit: function(frm) {
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
      
     
    get_calculations: function(frm) {
        CalculateTotal(frm);
    },

    before_load: function(frm) {
        // Set the from_date to the day before today when creating a new document
        if (frm.is_new()) {
            let today = frappe.datetime.get_today();
            let from_date = frappe.datetime.add_days(today, -1);
            frm.set_value('from_date', from_date);
        }
    }
    
});







frappe.ui.form.on('Station Shift Management item', {
    opening_meter_reading: function(frm, cdt, cdn) {
        calculateQtySold(frm, cdt, cdn);
      },
    closing_meter_reading: function(frm, cdt, cdn) {
        calculateQtySold(frm, cdt, cdn);
        updateTheCurentReading(frm, cdt, cdn)
    },
    pump_rate: function(frm, cdt, cdn) {
        calculateQtySold(frm, cdt, cdn);
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
            from_date:frm.doc.from_date // Pass the list of pump_or_tank values
        },
        callback: function(response) {
            if(response.message){
                row.current_reading_value = response.message;
                if(row.closing_meter_reading !== row.current_reading_value){

                    frappe.msgprint(__('Last Meter Reading not equal to your Closing Meter Reading, You Might be missing to enter some sells in the System Please enter them'));
                }
                // Refresh the field in the current row
                frm.refresh_field('items');
                // Optionally, refresh only the specific row
                frm.refresh_field('current_reading_value', row.name);
                
            }
        
          },
        error: function(err) {
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
        callback: function(response) {
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
        error: function(err) {
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
        callback: function(response) {
            if (response && response.message) {
                console.log(response.message);
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
        error: function(err) {
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
            callback: function(r) {
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
                    console.log("No accounts data found in response.");
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
                }else {
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

