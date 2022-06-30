# -*- coding: utf-8 -*-
{
    'name': "ywe_profit_report",
    'summary': "",
    'description': "",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['stock', 'point_of_sale', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'report/stock_report_view.xml',
        'report/stock_report_template.xml',
        'views/views.xml',
    ],
}