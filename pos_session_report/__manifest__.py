# -*- coding: utf-8 -*-
{
    'name': "pos_session_report",
    'summary': "POS session report as a receipt",
    'description': "POS session report as a receipt",
    'author': "AZITConsultants",
    'website': 'http://www.azitconsultants.com',
    'category': 'Point of Sale',
    'version': '0.1',
    'depends': ['point_of_sale', 'pos_discount_amount'],
    'data': [
        "reports/session_report.xml",
        "reports/session_report_template.xml",
        "reports/z_report_template.xml",
        'views/pos_session_form_view.xml',
        'views/pos_config_form_view.xml',
        'security/ir.model.access.csv',
    ],
    'css': ['static/src/css/pos.css'],
}