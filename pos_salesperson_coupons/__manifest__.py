# -*- coding: utf-8 -*-
{
    'name': "(POS) Give the salespersons a coupon",
    'summary': "This module will allow you to create a MAFIA of salespersons :D",
    'description': "This module will allow you to create a MAFIA of salespersons :D",
    'author': "Sayed Ahmed Abbas",
    'website': "",
    'category': 'Point of Sale',
    'version': '0.1',
    'depends': ['point_of_sale', 'mail'],
    'qweb': ['static/src/xml/pos.xml'],
    'data': [
        'security/ir.model.access.csv',




        'views/sales_person_views.xml',
        'views/pos_coupon_salesperson_views.xml',
        'views/pos_coupon_used_views.xml',
        'views/menu_views.xml',
        'views/pos_assets.xml',
        # 'data/product_data.xml',
    ],
}