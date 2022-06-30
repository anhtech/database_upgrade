# -*- coding: utf-8 -*-
{
    'name': "Ushk Website Reference Number",
    'summary': "Ask for Ushk Website Reference Number in POS",
    'description': "Ask for Ushk Website Reference Number in POS",
    'author': "Sayed Ahmed Abbas",
    'website': "",
    'category': 'Point of Sale',
    'version': '0.1',
    'depends': ['point_of_sale'],
    'qweb': ['static/src/xml/pos.xml'],
    'data': [
        'views/pos_order_views.xml',
        'views/pos_assets.xml',
    ],
}