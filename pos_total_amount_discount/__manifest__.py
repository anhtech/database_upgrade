# -*- coding: utf-8 -*-
{
    'name': "POS Discount on Total Amount",
    'summary': "",
    'description': "",
    'author': "AZConsulting",
    'website': "http://www.azitconsultants.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'point_of_sale', 'product'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_assets.xml',
        'data/product_data.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
}
