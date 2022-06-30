# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import datetime
from datetime import time as datetime_time
import pytz

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

class az_brc_hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    normal_attendance = fields.Float(string="Normal Hours", compute="_share_working_hours",store=True,default=0.00)
    real_normal_attendance = fields.Float(string="Real Normal Hours", compute="_share_working_hours",store=True,default=0.00)
    OT1_attendance = fields.Float(string="Overtime", compute="_share_working_hours",store=True,default=0.00)
    OT2_attendance = fields.Float(string="Overtime 2",store=True,default=0.00)
    lateness = fields.Float(string="Lateness",store=True,default=0.00)
    real_morning_lateness = fields.Float(string="Real Late Login",store=True,default=0.00)
    real_evening_lateness = fields.Float(string="Real Early Logout", store=True,default=0.00)
    morning_lateness = fields.Float(string="Late Login", store=True,default=0.00)
    evening_lateness = fields.Float(string="Early Logout", store=True,default=0.00)
    number_of_days = fields.Float(string="# of Days (incl. leaves)", compute="_share_working_hours",store=True,default=0)
    number_of_days_excl_leaves = fields.Float(string="# of Days (excl. leaves)", compute="_share_working_hours", store=True, default=0)
    number_of_absent_days = fields.Float(string="# of Absent Days", compute="_share_working_hours", store=True,default=0)
    number_of_holiday_days = fields.Float(string="Holiday days (Only)", compute="_share_working_hours", store=True,default=0)
    number_of_leaves_days = fields.Float(string="Leaves days (Only)", compute="_share_working_hours", store=True,default=0)
    tz_name = fields.Char(string="Timezone", default="Asia/Bahrain", readonly=True, store=True)

    @api.onchange('line_ids')
    def onSlipCalculationChanged(self):
        netSalaryRules = self.line_ids.filtered(lambda x: x.code == 'NET')
        for netRule in netSalaryRules:
            total = 0
            for normalRule in self.line_ids.filtered(lambda x: x.code not in ['NET', 'GROSS', 'BASIC']):
                total += normalRule.total
            netRule.amount = total
            netRule.total = total

    @api.depends('number_of_days','number_of_days_excl_leaves','number_of_absent_days','normal_attendance')
    def get_worked_day_lines(self, contracts, date_from, date_to):
        ret_res = super(az_brc_hr_payslip,self).get_worked_day_lines(contracts, date_from, date_to) # ignore the results ! (This is just a theoretical results)
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.datetime.combine(fields.Date.from_string(date_from), datetime_time.min)
            day_to = datetime.datetime.combine(fields.Date.from_string(date_to), datetime_time.max)

            # compute leave days
            leaves = {}
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
            for day_intervals in day_leave_intervals:
                for interval in day_intervals:
                    holiday = interval[2]['leaves'].holiday_id
                    current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                        'name': holiday.holiday_status_id.name or _('Global Leaves'),
                        'sequence': 5,
                        'code': holiday.holiday_status_id.name or 'GLOBAL',
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'contract_id': contract.id,
                    })
                    # leave_time = (interval[1] - interval[0]).seconds / 3600
                    if holiday.holiday_status_id.leave_pay == 'full':
                        leave_time = (interval[2]['attendances'].hour_to - interval[2]['attendances'].hour_from)*holiday.number_of_days_temp
                        if contract.resource_calendar_id.lunch_state:
                            leave_time = leave_time - (interval[2]['attendances'].lunch_break_to-interval[2]['attendances'].lunch_break_from)
                    elif holiday.holiday_status_id.leave_pay == 'half':
                        leave_time = (interval[2]['attendances'].hour_to - interval[2]['attendances'].hour_from)*holiday.number_of_days_temp
                        if contract.resource_calendar_id.lunch_state:
                            leave_time = leave_time - (interval[2]['attendances'].lunch_break_to-interval[2]['attendances'].lunch_break_from)
                        leave_time = leave_time / 2.0
                    else:
                        leave_time = 0.00
                    current_leave_struct['number_of_hours'] += leave_time
                    leave_time = (interval[1] - interval[0]).seconds / 3600
                    work_hours = contract.employee_id.get_day_work_hours_count(interval[0].date(), calendar=contract.resource_calendar_id)
                    if work_hours:
                        current_leave_struct['number_of_days'] += leave_time / work_hours

            # compute worked days
            attendances = {
                # 'name': _("Normal Working Days paid at 100%"),
                'name': _("Normal Working Days"),
                'sequence': 1,
                'code': 'WORK100',
                # 'number_of_days': work_data['days'],
                'number_of_days': self.number_of_days_excl_leaves,
                # 'number_of_hours': work_data['hours'],
                'number_of_hours': self.normal_attendance,
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())
        return res

    @api.one
    @api.depends('employee_id', 'date_from', 'date_to')
    def _share_working_hours(self):
        if self.employee_id:
            att_ids = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id), ('check_in', '>=', self.date_from), ('check_out', '<=', self.date_to)])
            working_days_count = 0
            working_days_excl_leaves_count = 0
            absent_days_count = 0
            holiday_days_count = 0
            leaves_days_count = 0
            checked_dates = []
            for att in att_ids:
                check_in_as_date = att.check_in.date()
                if not check_in_as_date in checked_dates:
                    if att.normal_attendance > 0:
                        checked_dates.append(check_in_as_date)
                        working_days_count+=1
                        working_days_excl_leaves_count+=1
                        # print(att.check_in+" is working day "+str(working_days_count)+" !")
                    else:
                        if att.is_special:
                            attendance_ids = att.working_shift.attendance_ids
                        else:
                            attendance_ids = att.special_working_shift.attendance_ids
                        day_as_int = check_in_as_date.weekday()
                        is_holiday_in_working_hours = False
                        for attendance_id in attendance_ids:
                            if (str(attendance_id.dayofweek) == str(day_as_int)):
                                if attendance_id.holiday_box:
                                    working_days_count += 1
                                    working_days_excl_leaves_count += 1
                                    checked_dates.append(check_in_as_date)
                                    is_holiday_in_working_hours = True
                                    holiday_days_count+=1
                                    # print(att.check_in+" is working day "+str(working_days_count)+" (Holiday) !")
                                    break
                        if is_holiday_in_working_hours == False:
                            if att.allowed_leave:
                                checked_dates.append(check_in_as_date)
                                working_days_count += 1
                                working_days_excl_leaves_count += 1
                                # print(att.check_in + " is working day " + str(working_days_count) + " !")
                            else:
                                if not isThereAnotherRecordForTheSameDateByAttendanceIds(att_ids,checked_dates,check_in_as_date): # There is another record I need to check before deciding on this day ?
                                    actual_starting_time = None
                                    for attendance_id in attendance_ids:
                                        if (str(attendance_id.dayofweek) == str(day_as_int)):
                                            actual_starting_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(attendance_id.hour_from) * 60, 60))
                                            actual_starting_time = datetime.datetime.strptime(actual_starting_time_string, "%H:%M").time()
                                            break
                                    if actual_starting_time == None:
                                        current_date_as_datetime = datetime.datetime.combine(check_in_as_date,datetime.datetime.min.time())
                                    else:
                                        current_date_as_datetime = datetime.datetime.combine(check_in_as_date,actual_starting_time)
                                    holidays_from_leaves = self.env['hr.holidays'].search(
                                        [('employee_id', '=', self.employee_id.id), ('date_from', '<=', str(current_date_as_datetime)),
                                            ('date_to', '>=', str(current_date_as_datetime)), ('state', '=', 'validate')])
                                    if len(holidays_from_leaves)>0:
                                        is_paid = False
                                        is_half_paid = False
                                        is_not_paid = False
                                        for leave in holidays_from_leaves:
                                            if leave.holiday_status_id.leave_pay == 'full':
                                                is_paid = True
                                            elif leave.holiday_status_id.leave_pay == 'half':
                                                is_half_paid = True
                                            elif leave.holiday_status_id.leave_pay == 'not_paid':
                                                is_not_paid = True
                                        if is_paid:
                                            working_days_count += 1
                                            leaves_days_count += 1
                                            # print(att.check_in + " is working day (paid leave) " + str(working_days_count) + " !")
                                        elif is_half_paid:
                                            working_days_count += 0.5
                                            absent_days_count += 0.5
                                            leaves_days_count += 0.5
                                            # print(att.check_in + " is working day (half paid leave) " + str(working_days_count) + " !")
                                        elif is_not_paid:
                                            absent_days_count += 1
                                            # print(att.check_in + " is Absent day (unpaid leave) " + str(absent_days_count) + " !")
                                    else:
                                        # print("No leaves has been found! (Absent)")
                                        absent_days_count += 1
                                        # print(att.check_in + " is Absent day " + str(absent_days_count) + " !")
                                    checked_dates.append(check_in_as_date)
                                    # I need to increase working_days_count in case of paid leave (increase by 1.00, 0.75, 0.50, 0.25 depending on paid leave amount)
            current_looping_date = self.date_from
            end_looping_date = self.date_to
            while(current_looping_date<=end_looping_date):
                if current_looping_date in checked_dates:
                    pass # It is already checked !
                    # print(current_looping_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + " is already checked !")
                else:
                    if (self.employee_id.special_attendance==None) or (self.employee_id.special_attendance==False) or (len(self.employee_id.special_attendance)==0):
                        attendance_ids = self.employee_id.resource_calendar_id.attendance_ids
                    else:
                        attendance_ids = self.employee_id.special_attendance.attendance_ids
                    day_as_int = current_looping_date.weekday()
                    is_holiday_in_working_hours = False
                    for attendance_id in attendance_ids:
                        if (str(attendance_id.dayofweek) == str(day_as_int)):
                            if attendance_id.holiday_box:
                                working_days_count += 1
                                working_days_excl_leaves_count += 1
                                checked_dates.append(current_looping_date)
                                is_holiday_in_working_hours = True
                                holiday_days_count += 1
                                # print(current_looping_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + " is working day " + str(working_days_count) + " (Holiday) !")
                                break
                    if is_holiday_in_working_hours == False:
                        actual_starting_time = None
                        for attendance_id in attendance_ids:
                            if (str(attendance_id.dayofweek) == str(day_as_int)):
                                actual_starting_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(attendance_id.hour_from) * 60, 60))
                                actual_starting_time = datetime.datetime.strptime(actual_starting_time_string,"%H:%M").time()
                                break
                        if actual_starting_time == None:
                            current_date_as_datetime = datetime.datetime.combine(current_looping_date,datetime.datetime.min.time())
                        else:
                            current_date_as_datetime = datetime.datetime.combine(current_looping_date,actual_starting_time)
                        holidays_from_leaves = self.env['hr.leave'].search(
                            [('employee_id', '=', self.employee_id.id),
                             ('date_from', '<=', str(current_date_as_datetime)),
                             ('date_to', '>=', str(current_date_as_datetime)),
                             ('state', '=', 'validate')])
                        if len(holidays_from_leaves) > 0:
                            is_paid = False
                            is_half_paid = False
                            is_not_paid = False
                            for leave in holidays_from_leaves:
                                if leave.holiday_status_id.leave_pay == 'full':
                                    is_paid = True
                                elif leave.holiday_status_id.leave_pay == 'half':
                                    is_half_paid = True
                                elif leave.holiday_status_id.leave_pay == 'not_paid':
                                    is_not_paid = True
                            if is_paid:
                                working_days_count += 1
                                leaves_days_count += 1
                                # print(current_looping_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + " is working day (paid leave) " + str(working_days_count) + " !")
                            elif is_half_paid:
                                working_days_count += 0.5
                                absent_days_count += 0.5
                                leaves_days_count += 0.5
                                # print(current_looping_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + " is working day (half paid leave) " + str(working_days_count) + " !")
                            elif is_not_paid:
                                absent_days_count += 1
                                # print(current_looping_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + " is Absent day (unpaid leave) " + str(absent_days_count) + " !")
                        else:
                            # print("No leaves has been found! (Absent)")
                            absent_days_count += 1
                            # print(current_looping_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + " is Absent day " + str(absent_days_count) + " !")
                        checked_dates.append(current_looping_date)
                current_looping_date = current_looping_date + datetime.timedelta(days=1)
            self.number_of_absent_days = absent_days_count
            self.number_of_days = working_days_count
            self.number_of_days_excl_leaves = working_days_excl_leaves_count
            self.number_of_leaves_days = leaves_days_count
            self.number_of_holiday_days = holiday_days_count
            self.normal_attendance = sum(line.normal_attendance for line in att_ids)
            self.real_normal_attendance = sum(line.real_normal_attendance for line in att_ids)
            self.OT1_attendance = sum(line.OT1_attendance for line in att_ids)
            # self.OT2_attendance = sum(line.OT2_attendance for line in att_ids)
            self.lateness = sum(line.lateness for line in att_ids)
            # self.real_evening_lateness = sum(line.real_evening_lateness for line in att_ids)
            # self.morning_lateness = sum(line.morning_lateness for line in att_ids)
            # self.evening_lateness = sum(line.evening_lateness for line in att_ids)
        else:
            self.number_of_absent_days = 0
            self.number_of_days = 0
            self.number_of_days_excl_leaves = 0
            self.number_of_leaves_days = 0
            self.number_of_holiday_days = 0
            self.normal_attendance = 0.00
            self.real_normal_attendance = 0.00
            self.OT1_attendance = 0.00
            # self.OT2_attendance = 0.00
            self.lateness = 0.00
            # self.real_evening_lateness = 0.00
            # self.morning_lateness = 0.00
            # self.evening_lateness = 0.00


    dd_this_month = fields.Integer(compute="_get_this_month_dd", store=True, default=0)

    @api.one
    @api.depends('date_to')
    def _get_this_month_dd(self):
        if self.date_to:
            dd = self.date_to.day
            self.dd_this_month = int(dd)