# -*- coding: utf-8 -*-
{
    'name': "(POS) Chat API Whatsapp on POS",
    'summary': "This module will use the Chat API solution.",
    'description': "This module will use the Chat API solution to send a whatsapp message to the customer of the POS.",
    'author': "Sayed Ahmed Abbas",
    'website': "",
    'category': 'Point of Sale',
    'version': '0.1',
    'depends': ['point_of_sale', 'web_notify', 'pos_order_print'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/pos_order_views.xml',
        'views/res_partner_views.xml',
    ],
}