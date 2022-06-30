# -*- coding: utf-8 -*-
{
    'name': "(Accounting-Ywe) Design of Customer Receipt",
    'summary': "The design of Customer Receipt for Ywebh company.",
    'description': "The design of Customer Receipt for Ywebh company.",
    'author': "Sayed Ahmed Abbas",
    'website': "",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['ywebh_quotation', 'account'],
    'data': [
        # 'security/ir.model.access.csv',
        'reports/payment_receipt_template.xml',
        'views/account_invoice_views.xml',
        'views/account_payment_views.xml',
        'views/paperformats.xml',
    ],
}