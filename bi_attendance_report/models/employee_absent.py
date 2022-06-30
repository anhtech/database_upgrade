# -*- coding: utf-8 -*-
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

class EmployeeAbsents(models.Model):
    _inherit = 'hr.employee'

    def absent_lookup_function(self,att_ids,date_from,date_to):

        working_days_count = 0
        working_days_excl_leaves_count = 0
        absent_days_count = 0
        holiday_days_count = 0
        leaves_days_count = 0
        checked_dates = []
        absent_days = []
        for att in att_ids:
            check_in_as_date = att.check_in.date()
            if not check_in_as_date in checked_dates:
                if att.normal_attendance > 0:
                    checked_dates.append(check_in_as_date)
                    working_days_count += 1
                    working_days_excl_leaves_count += 1
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
                                holiday_days_count += 1
                                # print(att.check_in+" is working day "+str(working_days_count)+" (Holiday) !")
                                break
                    if is_holiday_in_working_hours == False:
                        if att.allowed_leave:
                            checked_dates.append(check_in_as_date)
                            working_days_count += 1
                            working_days_excl_leaves_count += 1
                            # print(att.check_in + " is working day " + str(working_days_count) + " !")
                        else:
                            if not isThereAnotherRecordForTheSameDateByAttendanceIds(att_ids, checked_dates,
                                                                                     check_in_as_date):  # There is another record I need to check before deciding on this day ?
                                actual_starting_time = None
                                for attendance_id in attendance_ids:
                                    if (str(attendance_id.dayofweek) == str(day_as_int)):
                                        actual_starting_time_string = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(attendance_id.hour_from) * 60, 60))
                                        actual_starting_time = datetime.strptime(actual_starting_time_string, "%H:%M").time()
                                        break
                                if actual_starting_time == None:
                                    current_date_as_datetime = datetime.combine(check_in_as_date, datetime.min.time())
                                else:
                                    current_date_as_datetime = datetime.combine(check_in_as_date, actual_starting_time)
                                holidays_from_leaves = self.env['hr.holidays'].search(
                                    [('employee_id', '=', self.id),
                                     ('date_from', '<=', str(current_date_as_datetime)),
                                     ('date_to', '>=', str(current_date_as_datetime)), ('state', '=', 'validate')])
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
                                        # print(att.check_in + " is working day (paid leave) " + str(working_days_count) + " !")
                                    elif is_half_paid:
                                        working_days_count += 0.5
                                        absent_days_count += 0.5
                                        leaves_days_count += 0.5
                                        # print(att.check_in + " is working day (half paid leave) " + str(working_days_count) + " !")
                                    elif is_not_paid:
                                        absent_days_count += 1
                                        absent_days.append(check_in_as_date.strftime("%d/%m/%Y"))
                                        # print(att.check_in + " is Absent day (unpaid leave) " + str(absent_days_count) + " !")
                                else:
                                    # print("No leaves has been found! (Absent)")
                                    absent_days_count += 1
                                    absent_days.append(check_in_as_date.strftime("%d/%m/%Y"))
                                    # print(att.check_in + " is Absent day " + str(absent_days_count) + " !")
                                checked_dates.append(check_in_as_date)
                                # I need to increase working_days_count in case of paid leave (increase by 1.00, 0.75, 0.50, 0.25 depending on paid leave amount)
        current_looping_date = datetime.strptime(date_from,DEFAULT_SERVER_DATE_FORMAT).date()
        end_looping_date = datetime.strptime(date_to,DEFAULT_SERVER_DATE_FORMAT).date()
        while (current_looping_date <= end_looping_date):
            if current_looping_date in checked_dates:
                pass  # It is already checked !
                # print(current_looping_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + " is already checked !")
            else:
                if (self.special_attendance == None) or (self.special_attendance == False) or (len(self.special_attendance) == 0):
                    attendance_ids = self.resource_calendar_id.attendance_ids
                else:
                    attendance_ids = self.special_attendance.attendance_ids
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
                            actual_starting_time_string = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(float(attendance_id.hour_from) * 60, 60))
                            actual_starting_time = datetime.strptime(actual_starting_time_string, "%H:%M").time()
                            break
                    if actual_starting_time == None:
                        current_date_as_datetime = datetime.combine(current_looping_date, datetime.min.time())
                    else:
                        current_date_as_datetime = datetime.combine(current_looping_date, actual_starting_time)
                    holidays_from_leaves = self.env['hr.leave'].search(
                        [('employee_id', '=', self.id),
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
                            absent_days.append(current_looping_date.strftime("%d/%m/%Y"))
                            # print(current_looping_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + " is Absent day (unpaid leave) " + str(absent_days_count) + " !")
                    else:
                        # print("No leaves has been found! (Absent)")
                        absent_days_count += 1
                        absent_days.append(current_looping_date.strftime("%d/%m/%Y"))
                        # print(current_looping_date.strftime(DEFAULT_SERVER_DATE_FORMAT) + " is Absent day " + str(absent_days_count) + " !")
                    checked_dates.append(current_looping_date)
            current_looping_date = current_looping_date + timedelta(days=1)
        return absent_days