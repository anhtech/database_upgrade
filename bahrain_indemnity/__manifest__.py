# -*- coding: utf-8 -*-
{
    'name': "(HR) Bahrain Indemnity System",
    'summary': "A system to calculate the indemnity according to Bahrain Rules.",
    'description': "A system to calculate the indemnity according to Bahrain Rules.",
    'author': "AZ Consulting",
    'website': "http://www.azitconsultants.com/",
    'category': 'Employees',
    'version': '0.1',
    'depends': ['account', 'hr', 'hr_payroll', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_contract_indemnity_views.xml',
        'views/menu_views.xml',
        'data/scheduler_data.xml',
    ],
}
