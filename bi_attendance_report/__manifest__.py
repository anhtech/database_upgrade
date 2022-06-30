# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Employee Attendance sheet Report(sign in/sign out report) in odoo',
    'version': '12.0.0.2',
    'summary': 'This module helps to print Daily/Weekly/Monthly Attendance sheet report of Employee',
    'description': """
    Print Employee Attendance Report Attendance sheet 
    Print Daily Employee Attendance Report
    Print Weekly Employee Attendance Report , employee sheet , hr sheet , Attendance sheet of employee
    Print Monthly Employee Attendance Report , employee monthly sheet for attendance 

    Print Employee Attendance sheet Report
    Print Daily Employee Attendance sheet Report  sheet by Employee (Regular and Overtime Hours)
    Print Weekly Employee Attendance sheet Report
    Print Monthly Employee Attendance sheet Report

    Employee Attendance Report Print
    Daily Employee Attendance Report print
    Weekly Employee Attendance Report print
    Monthly Employee Attendance Report print
    Employee sign in/out report
    employee sign in/sign out report
    employee sign in-out  log report
    
    """,
    'price': 11,
    'currency': "EUR",
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base','hr_attendance','az_attendance','hr_holidays','payroll_connection'],
    'data': [
             "reports/attendance_report.xml",
             "reports/attendance_report_template.xml",
             "reports/attendance_group_report_template.xml",
             "reports/action_group_report_template.xml",
             "reports/action_group_d_report_template.xml",
             "views/hr_view.xml"
             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "live_test_url": "https://youtu.be/UsC480sfwCo",
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
