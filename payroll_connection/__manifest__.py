# -*- coding: utf-8 -*-
{
    'name': "payroll_connection",
    'summary': "A connection between attendance module and payroll.",
    'description': "A connection between attendance module and payroll.",
    'author': "AZConsulting",
    'website': "http://www.azitconsultants.com/",
    'category': 'Employees',
    'version': '0.1',
    'depends': ['az_attendance', 'hr_attendance', 'hr_payroll'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_payslip_inherit.xml',
        'views/hr_holiday_status.xml',
        'data/hr_payroll_rules.xml',
    ],
}