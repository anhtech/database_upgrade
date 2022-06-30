# -*- coding: utf-8 -*-
{
    'name': "AZ_attendance",

    'summary': "All attendance customizations are implemented here.",

    'description': "All attendance customizations are implemented here.",

    'author': "AZ Consulting",
    'website': "http://www.azitconsultants.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Employees',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance', 'to_attendance_device', 'to_base', 'to_safe_confirm_button'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendance_inherit.xml',
        'views/hr_employee_inherit.xml',
        'views/resource_calander_BRC.xml',
        'views/hr_special_attendance.xml',
        'wizard/employee_assign_work_hours.xml',
        'data/weekly_group_scheduler.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}