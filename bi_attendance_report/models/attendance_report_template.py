# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _, fields
import time
from datetime import datetime,date,timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_TIME_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from dateutil import parser
import collections
import operator
import pytz
import requests

def getAlreadyChecked(checked_dates,only_date):
    count=0
    for date in checked_dates:
        if only_date==date:
            count+=1
    return count

def isThereAnotherRecordForTheSameDateByAttendanceIds(att_ids,checked_dates,only_date):
    already_checked_int = getAlreadyChecked(checked_dates,only_date)
    count=0
    for att in att_ids:
        check_in_as_date = att.check_in.date()
        if check_in_as_date == only_date:
            count+=1
    if count>already_checked_int:
        return True
    return False

def to_tz(datetime, tz_name):
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

class attendance_report_template(models.AbstractModel):
    _name = 'report.bi_attendance_report.attendance_report_template'

    @api.multi
    def _get_report_values(self, docids, data=None):
        att_ids = self.env['hr.attendance'].browse(data.get('ids'))
        emp_ids = self.env['hr.employee'].browse(data.get('emp_ids'))
        new_att_ids = att_ids
        for attendance in new_att_ids:
            attendance.check_in_timezone = to_tz(attendance.check_in, attendance.tz_name)
            if attendance.check_out:
                attendance.check_out_timezone = to_tz(attendance.check_out, attendance.tz_name)
        docargs = {
                      'doc_ids': self.ids,
                      'data':data,
                      'docs':emp_ids,
                      'att_ids':new_att_ids,
                       }
        return docargs

class attendance_group_report_template(models.AbstractModel):
    _name = 'report.bi_attendance_report.attendance_group_report_template'


    @api.multi
    def _get_report_values(self, docids, data=None):
      dep_ids = self.env['hr.department'].browse(data.get('department_ids'))
      docargs = {
                  'doc_ids': self.ids,
                  'data':data,
                  'real_data': data.get('real_data'),
                  'docs':dep_ids
                }
      return docargs


class action_group_report_template(models.AbstractModel):
    _name = 'report.bi_attendance_report.action_group_report_template'


    @api.multi
    def _get_report_values(self, docids, data=None):
      # dep_ids = self.env['hr.department'].browse(data.get('department_ids'))
      docargs = {
                  'doc_ids': self.ids,
                  'data':data,
                  'real_data': data.get('real_data'),
                  # 'docs':dep_ids
                }
      return docargs

class action_group_d_report_template(models.AbstractModel):
    _name = 'report.bi_attendance_report.action_group_d_report_template'

    @api.multi
    def _get_report_values(self, docids, data=None):
        emp_ids = self.env['hr.employee'].browse(data.get('emp_ids'))
        records = []
        for employee_id in emp_ids:
            line = []
            line.append(employee_id)
            att_ids = self.env['hr.attendance'].search(
                [('employee_id', '=', employee_id.id), ('check_in', '>=', data.get('start_date')),
                 ('check_in', '<=', data.get('end_date'))], order="check_in asc")
            for attendance in att_ids:
                attendance.check_in_timezone = to_tz(attendance.check_in, attendance.tz_name)
                if attendance.check_out:
                    attendance.check_out_timezone = to_tz(attendance.check_out, attendance.tz_name)
            line.append(att_ids)
            records.append(line)
        docargs = {
            'self': self,
            'doc_ids': self.ids,
            'data': data,
            'records': records,
            'docs': emp_ids,
        }
        return docargs