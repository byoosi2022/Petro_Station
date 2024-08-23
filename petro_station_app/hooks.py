app_name = "petro_station_app"
app_title = "Petro Station App"
app_publisher = "mututa paul"
app_description = "For petro stations"
app_email = "mututapaul02@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/petro_station_app/css/petro_station_app.css"
# app_include_js = "/assets/petro_station_app/js/petro_station_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/petro_station_app/css/petro_station_app.css"
# web_include_js = "/assets/petro_station_app/js/petro_station_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "petro_station_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "petro_station_app/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "petro_station_app.utils.jinja_methods",
# 	"filters": "petro_station_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "petro_station_app.install.before_install"
# after_install = "petro_station_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "petro_station_app.uninstall.before_uninstall"
# after_uninstall = "petro_station_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "petro_station_app.utils.before_app_install"
# after_app_install = "petro_station_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "petro_station_app.utils.before_app_uninstall"
# after_app_uninstall = "petro_station_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "petro_station_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	# "*": {
# 	# 	"on_update": "method",
# 	# 	"on_cancel": "method",
# 	# 	"on_trash": "method"
# 	# },
#     "Sales Invoice": {
#         "on_submit": "petro_station_app.custom_api.meter_reading.create_pump_meter_reading",
#         # "befaore_submit": "petro_station_app.custom_api.stock_transfer.create_stock_transfer"
#     }
# }

doc_events = {
    # "*": {
    #     "on_update": "method",
    #     "on_cancel": "method",
    #     "on_trash": "method"
    # },
    "Sales Invoice": {
        "on_submit": [
            # "petro_station_app.custom_api.stock_transfer.create_stock_transfer_server",
            "petro_station_app.custom_api.meter_reading.create_pump_meter_reading",
            
        ],
        "on_cancel": "petro_station_app.custom_api.meter_reading.create_pump_meter_reading"
    },
    "Fuel Sales App": {
      
        "on_submit": "petro_station_app.custom_api.update_item_price.update_item_price"
    },
    
    "Purchase Management": {
      
        "on_update": "petro_station_app.custom_api.purchase_management.create_petro_currency_exchange"
    },
    
    "Stock Entry": {
      
        "on_submit": "petro_station_app.custom_api.meter_reading_stock_entry.create_pump_meter_reading",
        "on_cancel": "petro_station_app.custom_api.meter_reading_stock_entry.create_pump_meter_reading"
    },
    
    "Payment Entry": {
      
        "on_submit": "petro_station_app.custom_api.bank_deposits.update_bank_deposits",
        "on_cancel": "petro_station_app.custom_api.bank_deposits.update_bank_deposits"
        
    },
}
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"petro_station_app.tasks.all"
# 	],
# 	"daily": [
# 		"petro_station_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"petro_station_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"petro_station_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"petro_station_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "petro_station_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "petro_station_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "petro_station_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["petro_station_app.utils.before_request"]
# after_request = ["petro_station_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["petro_station_app.utils.before_job"]
# after_job = ["petro_station_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

fixtures = [
    {"dt": "Client Script", "filters": [["module", "=", "Petro Station App"]]},
    {"dt": "Custom Field", "filters": [["module", "=", "Petro Station App"]]}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"petro_station_app.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

