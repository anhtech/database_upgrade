# -*- coding: utf-8 -*-
{
    'name': "(Sales-Ywe) Design of Quotation/Sale Order for Tamkeen",
    'summary': "The design of Quotation/Sale Order (Tamkeen Edition) for Ywebh company.",
    'description': "The design of Quotation/Sale Order (Tamkeen Edition) for Ywebh company.",
    'author': "Sayed Ahmed Abbas",
    'website': "",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['sale', 'om_account_accountant', 'ywebh_module', 'report_qweb_pdf_watermark', 'sale_stock', 'sale_management', 'mail'],
    'data': [
        'reports/terms_page_template.xml',
        'reports/payment_schdule_page_template.xml',
        'reports/cover_page_template.xml',
        'reports/quotation_template_inherit.xml',
        'views/paperformats.xml',
    ],
}