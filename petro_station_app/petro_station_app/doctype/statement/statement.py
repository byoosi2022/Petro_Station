import frappe
from frappe.model.document import Document
from frappe import _

class Statement(Document):
    def validate(self):
        # Allow access to the child table field regardless of the Cost Center permissions
        self.allow_child_table_access()

    def allow_child_table_access(self):
        # Iterate through each row in the statement_details child table
        for detail in self.statement_details:
            # Bypass permission checks for the station_inv field
            if detail.station_inv:
                # Bypass the permission check for the Cost Center
                cost_center = frappe.get_value('Cost Center', detail.station_inv, 'name')
                if not self.has_permission(cost_center):
                    # Log an attempt to access restricted Cost Center
                    frappe.log_error(
                        f"User {frappe.session.user} attempted to access restricted Cost Center: {cost_center}",
                        "Cost Center Permission"
                    )
                    frappe.msgprint(
                        _("Access to the Cost Center has been bypassed for this operation."),
                        alert=True
                    )
    
    def has_permission(self, cost_center):
        # Always allow save and print regardless of the cost center restrictions
        return True

# Custom function to validate print permissions specifically for the Statement doctype
def custom_validate_print_permission(doc):
    # Bypass permission check for Statement documents
    if doc.doctype == 'Statement':
        return
    # For other doctypes, call the standard validate_print_permission function
    frappe.www.printview._original_validate_print_permission(doc)

# Set the custom validate print permission method only for the Statement doctype
def set_custom_validate_print_permission():
    # Save the original validate_print_permission method to use it for other doctypes
    if not hasattr(frappe.www.printview, '_original_validate_print_permission'):
        frappe.www.printview._original_validate_print_permission = frappe.www.printview.validate_print_permission
    
    # Override the validate_print_permission method
    frappe.www.printview.validate_print_permission = custom_validate_print_permission

# Hook this setup function to be called when Frappe starts up or when necessary
set_custom_validate_print_permission()
