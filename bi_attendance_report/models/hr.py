# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_TIME_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
import datetime
import pytz

def to_tz(datetime, tz_name):
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

class ReportWizard(models.TransientModel):
    _name = "report.wizard"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    is_this_month = fields.Boolean(string="This Month",defualt=False,help="If enabled, the reports will include attendances records from 1 to 26 of this month including the days from last month.", track_visibility='onchange')
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report')
    ], default="summary", required=True)
    early_logout = fields.Boolean(string="Early Log Out",defualt=False)
    late_login = fields.Boolean(string="Late Log In", defualt=False)
    missing_logout = fields.Boolean(string="Missing Log Out", defualt=False)
    absent_lookup = fields.Boolean(string="Show Absents", defualt=False)
    tz_name = fields.Char(string="Timezone",default="Asia/Bahrain",readonly=True)

    @api.onchange('is_this_month')
    def on_is_this_month_change(self):
        if (self.is_this_month): # disable start_date and end_date and assign them a new value
            today = datetime.date.today()
            first = today.replace(day=1)
            lastMonth = first - datetime.timedelta(days=1)
            self.start_date = lastMonth.replace(day=27)
            self.end_date = datetime.date.today().replace(day=26)
        else: # enable start_date and end_date and clear their value
            self.start_date = False
            self.end_date = False

    @api.multi
    def submit(self, form):
        employee_ids = self.env['hr.employee'].browse(form.get('active_ids'))
        emp_ids = [a.id for a in employee_ids]
        att_ids = self.env['hr.attendance'].search(
            [('employee_id', 'in', emp_ids), ('check_in', '>=', self.start_date), ('check_in', '<=', self.end_date)],order="check_in asc")
        attendance_ids = [a.id for a in att_ids]
        log_discrepancy = {
            "early_logout": self.early_logout,
            "late_login": self.late_login,
            "missing_logout": self.missing_logout,
            "absent_lookup": self.absent_lookup
        }
        printing_date = to_tz(datetime.datetime.now(), self.tz_name)
        datas = {
            'ids': attendance_ids,
            'model': 'hr.employee',
            'start_date': self.start_date,
            'end_date': self.end_date,
            'report_type': self.report_type,
            'log_discrepancy': log_discrepancy,
            'emp_ids': emp_ids,
            'printing_date': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_DATE_FORMAT),
            'printing_time': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_TIME_FORMAT),
        }
        return self.env.ref('bi_attendance_report.report_pdf_attendance').report_action(self, data=datas)

class GroupReportWizard(models.TransientModel):
    _name = "report.groupwizard"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    is_this_month = fields.Boolean(string="This Month",defualt=False,help="If enabled, the reports will include attendances records from 1 to 26 of this month including the days from last month.", track_visibility='onchange')
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report')
    ], default="summary", required=True)
    tz_name = fields.Char(string="Timezone", default="Asia/Bahrain", readonly=True)

    @api.onchange('is_this_month')
    def on_is_this_month_change(self):
        if (self.is_this_month): # disable start_date and end_date and assign them a new value
            today = datetime.date.today()
            first = today.replace(day=1)
            lastMonth = first - datetime.timedelta(days=1)
            self.start_date = lastMonth.replace(day=27)
            self.end_date = datetime.date.today().replace(day=26)
        else: # enable start_date and end_date and clear their value
            self.start_date = False
            self.end_date = False

    @api.multi
    def submit(self, form):
        department_ids = self.env['hr.department'].browse(form.get('active_ids'))
        departments = [a.id for a in department_ids]
        employee_ids = self.env['hr.employee'].search([('department_id', 'in', departments)])
        emp_ids = [a.id for a in employee_ids]
        if len(emp_ids) == 0:
            raise UserError(_("There is no employees in the chosen department !"))
        all_attendances = []
        for employee_id in emp_ids:
            att_ids_temp = self.env['hr.attendance'].search([('employee_id', '=', employee_id), ('check_in', '>=', self.start_date), ('check_in', '<=', self.end_date)])
            employee = self.env['hr.employee'].search([('id', '=', employee_id)])
            employee_id_name = employee.name
            if (len(att_ids_temp)>0):
                normalAttendanceTotal = sum(line.normal_attendance for line in att_ids_temp)
                OT1_Total = sum(line.OT1_attendance for line in att_ids_temp)
                OT2_Total = sum(line.OT2_attendance for line in att_ids_temp)
                latenessTotal = sum(line.morning_lateness for line in att_ids_temp)+sum(line.evening_lateness for line in att_ids_temp)
                attendance_JSON = {
                    'employee_id': employee_id_name,
                    'normalAttendanceTotal': normalAttendanceTotal,
                    'OT1_Total': OT1_Total,
                    'OT2_Total': OT2_Total,
                    'latenessTotal': latenessTotal,
                }
            else:
                attendance_JSON = {
                    'employee_id': employee_id_name,
                    'normalAttendanceTotal': 0.0,
                    'OT1_Total': 0.0,
                    'OT2_Total': 0.0,
                    'latenessTotal': 0.0,
                }
            all_attendances.append(attendance_JSON)
        if (len(all_attendances)==0):
            raise UserError(_("There is no attendance data !"))
        att_ids = self.env['hr.attendance'].search([('employee_id', 'in', emp_ids), ('check_in', '>=', self.start_date), ('check_in', '<=', self.end_date)],order="check_in asc")
        printing_date = to_tz(datetime.datetime.now(), self.tz_name)
        # attendance_ids = [a.id for a in att_ids]
        datas = {
            'model': 'hr.department',
            'start_date': self.start_date,
            'end_date': self.end_date,
            'department_ids': departments,
            'real_data': all_attendances,
            'report_type': self.report_type,
            'printing_date': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_DATE_FORMAT),
            'printing_time': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_TIME_FORMAT),
        }
        return self.env.ref('bi_attendance_report.group_report_pdf_attendance').report_action(self, data=datas)

class ActionGroupReport(models.TransientModel): # Summary group attendance report in action
    _name = 'bi_attendance_report.action_group_report'

    @api.model
    def _get_employee_ids(self):
        return self.env['hr.employee'].search([('id', 'in', self.env.context.get('active_ids', []))])

    employee_ids = fields.Many2many('hr.employee', string='Employees to assign', default=_get_employee_ids, required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    is_this_month = fields.Boolean(string="This Month", defualt=False,
                                   help="If enabled, the reports will include attendances records from 1 to 26 of this month including the days from last month.",
                                   track_visibility='onchange')
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report')
    ], default="summary", required=True)
    tz_name = fields.Char(string="Timezone", default="Asia/Bahrain", readonly=True)

    @api.onchange('is_this_month')
    def on_is_this_month_change(self):
        if (self.is_this_month):  # disable start_date and end_date and assign them a new value
            today = datetime.date.today()
            first = today.replace(day=1)
            lastMonth = first - datetime.timedelta(days=1)
            self.start_date = lastMonth.replace(day=27)
            self.end_date = datetime.date.today().replace(day=26)
        else:  # enable start_date and end_date and clear their value
            self.start_date = False
            self.end_date = False

    @api.multi
    def action_group_report(self):
        emp_ids = [a.id for a in self.employee_ids]
        if len(emp_ids) == 0:
            raise UserError(_("There is no employees selected !"))
        if len(emp_ids) == 1:
            raise UserError(_("You need to select more than one employee !"))
        if self.report_type == "summary":
            all_attendances = []
            for employee_id in emp_ids:
                att_ids_temp = self.env['hr.attendance'].search(
                    [('employee_id', '=', employee_id), ('check_in', '>=', self.start_date),
                     ('check_in', '<=', self.end_date)], order="check_in asc")
                employee = self.env['hr.employee'].search([('id', '=', employee_id)])
                employee_id_name = employee.name
                if (len(att_ids_temp) > 0):
                    normalAttendanceTotal = sum(line.normal_attendance for line in att_ids_temp)
                    OT1_Total = sum(line.OT1_attendance for line in att_ids_temp)
                    OT2_Total = sum(line.OT2_attendance for line in att_ids_temp)
                    latenessTotal = sum(line.morning_lateness for line in att_ids_temp) + sum(
                        line.evening_lateness for line in att_ids_temp)
                    attendance_JSON = {
                        'employee_id': employee_id_name,
                        'normalAttendanceTotal': normalAttendanceTotal,
                        'OT1_Total': OT1_Total,
                        'OT2_Total': OT2_Total,
                        'latenessTotal': latenessTotal,
                    }
                else:
                    attendance_JSON = {
                        'employee_id': employee_id_name,
                        'normalAttendanceTotal': 0.0,
                        'OT1_Total': 0.0,
                        'OT2_Total': 0.0,
                        'latenessTotal': 0.0,
                    }
                all_attendances.append(attendance_JSON)
            if (len(all_attendances) == 0):
                raise UserError(_("There is no attendance data !"))
            printing_date = to_tz(datetime.datetime.now(), self.tz_name)
            datas = {
                'model': 'hr.department',
                'start_date': self.start_date,
                'end_date': self.end_date,
                'real_data': all_attendances,
                'report_type': self.report_type,
                'printing_date': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_DATE_FORMAT),
                'printing_time': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_TIME_FORMAT),
            }
            return self.env.ref('bi_attendance_report.group_summary_pdf_report').report_action(self, data=datas)
        elif self.report_type == "detailed":
            printing_date = to_tz(datetime.datetime.now(), self.tz_name)
            datas = {
                'model': 'hr.employee',
                'start_date': self.start_date,
                'end_date': self.end_date,
                'report_type': self.report_type,
                'emp_ids': emp_ids,
                'printing_date': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_DATE_FORMAT),
                'printing_time': datetime.datetime.strftime(printing_date, DEFAULT_SERVER_TIME_FORMAT),
            }
            return self.env.ref('bi_attendance_report.group_detailed_pdf_report').report_action(self, data=datas)
