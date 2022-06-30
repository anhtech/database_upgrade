# -*- coding: utf-8 -*-
{
    'name': "Customizations for ywebh",
    'summary': "Customizations for ywebh | made by Sayed Ahmed Abbas",
    'description': "Customizations for ywebh | made by Sayed Ahmed Abbas (sayedahmed97bh@gmail.com)",
    'author': "Sayed Ahmed",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale', 'sale_management', 'om_account_accountant', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/form_inherit.xml',
        'views/invoice_inherit.xml',
        'views/product_template.xml',
        'views/res_company.xml',
        'views/res_company_bank.xml',
        'views/payment_schedule.xml',
        # 'views/templates.xml',
    ],
}