# map the columns to display relavent Alias names
COLUMN_MAPPINGS = {
    'lo_customer_addresses': {
        'customer_id': 'Customer ID',
        'address': 'Address',
        'city_id': 'City ID',
        'state': 'State',
        'zipcode': 'Zipcode',
        'country': 'Country',
        'name' : 'Name',
        'address1' : 'First Address',
        'address2' : 'Second Address',
        'address3' : 'Third Address'
        # Add more mappings as needed
    },
    'lo_users': {
        'user_id': 'User ID',
        'username': 'Username',
        'email': 'Email',
        'created_at': 'Created At',
        'last_login': 'Last Login',
        'name' : 'Name',
        'address1' : 'First Address',
        'address2' : 'Second Address',
        'address3' : 'Third Address'
        # Add more mappings as needed
    },
    'lo_master_customers': {
        'customer_id': 'Customer ID',
        'name': 'Name',
        'email': 'Email',
        'phone_number': 'Phone Number',
        'is_active': 'Active Status',
        'created_at': 'Created At',
        # Add more mappings as needed
    },
    'lo_master_cities': {
        'id': 'City ID',
        'name': 'City Name',
        'state': 'State',
        'country': 'Country',
        # Add more mappings as needed
    },
    'lo_customer_order': {
        'order_id': 'Order ID',
        'customer_id': 'Customer ID',
        'order_date': 'Order Date',
        'status': 'Order Status',
        'total_amount': 'Total Amount',
        'order_no': 'Order Number',
        'delivery_date': 'Delivery Date',
        'amount': 'Amount',
        'total_order_value': 'Total Order Value'
        # Add more mappings as needed
    },
    'lo_user_roles': {
        'role_id': 'Role ID',
        'role_name': 'Role Name',
        # Add more mappings as needed
    },
    'lo_store_detail': {
        'store_name' : 'Store Name',
        'manager' : 'Store Owner'
    }
}


# Priorities of Columns to view
COLUMN_PRIORITIES = {
    'lo_customer_addresses': [
        'Customer ID', 'Address', 'City ID', 'State', 'Zipcode', 'Country'
    ],
    'lo_users': [
        'User ID', 'Username', 'Email', 'Created At', 'Last Login'
    ],
    'lo_master_customers': [
        'Customer ID', 'Name', 'Email', 'Phone Number', 'Active Status', 'Created At'
    ],
    'lo_master_cities': [
        'City ID', 'City Name', 'State', 'Country'
    ],
    'lo_customer_order': [
        'Order ID', 'Customer ID', 'Order Status', 
        'Total Amount', 'Order Number', 'Delivery Date', 'Amount', 'Total Order Value', 'Order Date'
    ],
    'lo_user_roles': [
        'Role ID', 'Role Name'
    ]
}


# Columns of tables which have to be visibile in visibility
# Columns of tables which have to be dropped in visibility
VISIBILITY = {
    'lo_store_detail': ['updated_by_id', 'created_by_id', 'updated_on', 'created_on', 'reference_by', 'is_agree', 'is_sponsored', 'is_searchable','is_confirm', 'is_deleted', 'is_active', 'is_verified', 'uid', 'demo_user', 'khata_user', 'is_register','started_access','gst_number','gst_certificate','address_proof','poster','banner','iso_code','timezone','longitude','latitude','order_balance','market_type','store_logo_thumb','store_logo','is_store_link_active','store_link','store_code'],
    # Add more tables and their columns as needed
}


# Exclude the tables to ignore the addition of flags like is_deleted, is_active...etc 
EXCLUDED_TABLES = {
   'lo_cart_combos', 'lo_cart_combo_details', 'lo_cart_reminder', 'lo_combo_items', 'lo_combo_item_details', 'lo_comcash_cron_log', 'lo_customer_carts',
    'lo_customer_carts_details', 'lo_customer_comcash_referances', 'lo_customer_sub_order', 'lo_dine_in_settings', 'lo_favourite_stores', 'lo_general_settings', 
    'lo_global_settings', 'lo_item_attributes', 'lo_item_category', 'lo_item_config', 'lo_item_tags', 'lo_khata_choices_addons', 'lo_khata_combo', 
    'lo_khata_combo_details', 'lo_khata_combo_details_choices_addons', 'lo_login_history', 'lo_master_banned_items_i18n', 'lo_master_collection_types', 
    'lo_master_contents_i18n', 'lo_master_default_category_i18n', 'lo_master_default_category_items_i18n', 'lo_master_delivery_location', 
    'lo_master_email_templates_i18n', 'lo_master_item_featured_list', 'lo_master_item_unit_i18n', 'lo_master_notifications_i18n', 'lo_master_order_tacking_details', 
    'lo_master_queries', 'lo_master_roles', 'lo_master_sms_i18n', 'lo_master_store_category', 'lo_master_store_category_type_i18n', 'lo_master_subscriptions_i18n', 
    'lo_master_unit_i18n', 'lo_master_view_access', 'lo_master_view_store_access', 'lo_offers_cart_details', 'lo_offers_customer_details', 'lo_offers_details', 
    'lo_offers_item_details', 'lo_order_cancellation', 'lo_order_channel', 'lo_order_choices_addons', 'lo_order_combo', 'lo_order_combo_choices_addons', 
    'lo_order_combo_details', 'lo_order_history', 'lo_order_items', 'lo_order_item_cancellation', 'lo_order_proof_of_delivery', 'lo_order_reason_list', 
    'lo_order_reviews', 'lo_order_tracking', 'lo_payment_cycle', 'lo_payment_requests', 'lo_price_change_requests', 'lo_recommended_items', 'lo_seller_bag_orders', 
    'lo_seller_modules', 'lo_seller_settings', 'lo_seller_subscriptions', 'lo_stock_transactions', 'lo_store_settings', 'lo_user_presences', 'lo_wallet_settings',
    'lo_user_roles'
}