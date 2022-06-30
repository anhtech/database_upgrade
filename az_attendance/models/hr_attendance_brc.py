# -*- coding: utf-8 -*-
# This module is using Asia/Bahrain as a fixed timezone (line 35)

from odoo import models, fields, api, tools
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
import pytz

def to_tz(datetime, tz_name):
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)

def correctMinutesRounding(hours_minutes_string):
    if ":" in hours_minutes_string:
        splited = hours_minutes_string.split(":", 1)
        minutes = int(splited[1])
        if minutes == 60:
            minutes = 59
        return '{0:02.0f}:{1:02.0f}'.format(float(splited[0]),float(minutes))
    return False

def correctHoursShifting(hours_minutes_string):
    if ":" in hours_minutes_string:
        splited = hours_minutes_string.split(":", 1)
        hours = int(splited[0])
        days = 0
        while(hours>=24):
            hours = hours-24
            days += 1
        return '{0:02.0f}:{1:02.0f}'.format(float(hours),float(splited[1])), days
    return False, False

def round_total_hours(total_hours_in, rounding_ids_in, allow_overtime_rounding_in):
    total_hours_out = total_hours_in
    #print("Before Hours: " + str(total_hours_out))
    only_minutes = (total_hours_out - int(total_hours_out)) * 60.0
    #print("only_minutes from s2tart: " + str(only_minutes))
    only_minutes_and_hours = False
    # ===================================
    if allow_overtime_rounding_in:
        operator1 = []  # <
        operator2 = []  # <=
        operator3 = []  # =
        operator4 = []  # !=
        operator5 = []  # >
        operator6 = []  # >=
        for line in rounding_ids_in:
            if line.operator == "<":
                operator1.append(line)
        operator1.sort(key=sortOperator)  # Check the smaller first !
        for line in rounding_ids_in:
            if line.operator == "<=":
                operator2.append(line)
        operator2.sort(key=sortOperator)  # Check the smaller first !
        for line in rounding_ids_in:
            if line.operator == "=":
                operator3.append(line)
        operator3.sort(key=sortOperator)  # No need to sort actually, not complex
        for line in rounding_ids_in:
            if line.operator == "!=":
                operator4.append(line)
        operator4.sort(key=sortOperator)  # No need to sort actually, not complex
        for line in rounding_ids_in:
            if line.operator == ">":
                operator5.append(line)
        operator5.sort(key=sortOperator, reverse=True)  # Check greater first
        for line in rounding_ids_in:
            if line.operator == ">=":
                operator6.append(line)
        operator6.sort(key=sortOperator, reverse=True)  # Check greater first
        for line in operator1:
            if line.hour_from > 1:  # Means rounding for hours also !
                only_minutes_and_hours = (total_hours_out) * 60.0
            if only_minutes_and_hours == False:
                hour_from = line.hour_from * 60.0
                if only_minutes < hour_from:
                    only_minutes = line.hour_to * 60.0
                    #print("Rounded 1 !")
                    break
            else:
                hour_from = line.hour_from * 60.0
                if only_minutes_and_hours < hour_from:
                    only_minutes = line.hour_to * 60.0
                    break
                only_minutes_and_hours = False
        for line in operator2:
            if line.hour_from > 1:  # Means rounding for hours also !
                only_minutes_and_hours = (total_hours_out) * 60.0
            if only_minutes_and_hours == False:
                hour_from = line.hour_from * 60.0
                if only_minutes <= hour_from:
                    only_minutes = line.hour_to * 60.0
                    #print("OT2: Rounded 2 !")
                    break
            else:
                hour_from = line.hour_from * 60.0
                if only_minutes_and_hours <= hour_from:
                    only_minutes = line.hour_to * 60.0
                    break
                only_minutes_and_hours = False
        for line in operator3:
            if line.hour_from > 1:  # Means rounding for hours also !
                only_minutes_and_hours = (total_hours_out) * 60.0
            if only_minutes_and_hours == False:
                hour_from = line.hour_from * 60.0
                if only_minutes == hour_from:
                    only_minutes = line.hour_to * 60.0
                    #print("OT2: Rounded 3 !")
                    break
            else:
                hour_from = line.hour_from * 60.0
                if only_minutes_and_hours == hour_from:
                    only_minutes = line.hour_to * 60.0
                    break
                only_minutes_and_hours = False
        for line in operator4:
            if line.hour_from > 1:  # Means rounding for hours also !
                only_minutes_and_hours = (total_hours_out) * 60.0
            if only_minutes_and_hours == False:
                hour_from = line.hour_from * 60.0
                if only_minutes != hour_from:
                    only_minutes = line.hour_to * 60.0
                    #print("OT2: Rounded 4 !")
                    break
            else:
                hour_from = line.hour_from * 60.0
                if only_minutes_and_hours != hour_from:
                    only_minutes = line.hour_to * 60.0
                    break
                only_minutes_and_hours = False
        for line in operator5:
            if line.hour_from > 1:  # Means rounding for hours also !
                only_minutes_and_hours = (total_hours_out) * 60.0
            if only_minutes_and_hours == False:
                hour_from = line.hour_from * 60.0
                if only_minutes > hour_from:
                    only_minutes = line.hour_to * 60.0
                    #print("OT2: Rounded 5 !")
                    break
            else:
                hour_from = line.hour_from * 60.0
                if only_minutes_and_hours > hour_from:
                    only_minutes = line.hour_to * 60.0
                    break
                only_minutes_and_hours = False
        for line in operator6:
            if line.hour_from > 1:  # Means rounding for hours also !
                only_minutes_and_hours = (total_hours_out) * 60.0
            if only_minutes_and_hours == False:
                hour_from = line.hour_from * 60.0
                if only_minutes >= hour_from:
                    only_minutes = line.hour_to * 60.0
                    #print("OT2: Rounded 6 !")
                    break
            else:
                hour_from = line.hour_from * 60.0
                if only_minutes_and_hours >= hour_from:
                    only_minutes = line.hour_to * 60.0
                    break
                only_minutes_and_hours = False
    # ===================================
    total_hours_out = int(total_hours_out) + (only_minutes / 60.0)
    #print("After Hours: " + str(total_hours_out))
    return total_hours_out

def sortOperator(val):
    return val.hour_from

class az_brc_hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    def is_on_leave_BRC(self,calendar_id,current_working_date_object):
        leaves = calendar_id.leave_ids
        for leave in leaves:
            if ((current_working_date_object >= leave.date_from) and
                    ((current_working_date_object <= (leave.date_to)))):
                return True
        global_leave_ids = calendar_id.leave_ids
        for leave in global_leave_ids:
            if ((current_working_date_object >= leave.date_from) and (current_working_date_object <= leave.date_to)):
                return True
        return False

    real_normal_attendance = fields.Float(string="Real Normal Hours", default=0.00, compute="_compute_normal_attendance", store=True)
    normal_attendance = fields.Float(string="Normal Hours", default=0.00, compute="_compute_normal_attendance",store=True)
    real_OT1_attendance = fields.Float(string="Real Overtime", default=0.00, compute="_compute_OT1_attendance", store=True)
    OT1_attendance = fields.Float(string="Overtime", default=0.00, compute="_compute_OT1_attendance",store=True)
    # real_OT2_attendance = fields.Float(string="Real Overtime 2", default=0.00, compute="_compute_OT2_attendance", store=True)
    # OT2_attendance = fields.Float(string="Overtime 2", default=0.00, compute="_compute_OT2_attendance",store=True)
    # real_morning_lateness = fields.Float(string="Real Late Login", default=0.00, compute="_compute_real_morning_lateness",store=True)
    # real_evening_lateness = fields.Float(string="Real Early Logout", default=0.00, compute="_compute_real_evening_lateness",store=True)
    lateness = fields.Float(string="Lateness", default=0.00, compute="_compute_lateness",store=True)
    # evening_lateness = fields.Float(string="Early Logout", default=0.00, compute="_compute_evening_lateness",store=True)
    allowed_leave = fields.Boolean(string="Allow Leave", default=False, help="This option will allow the employee to leave ealry and it will be calculated as leaving on time.")
    tz_name = fields.Char(string="Timezone",default="Asia/Bahrain",readonly=True,store=True)
    working_shift = fields.Many2one('resource.calendar', string='Working Hours', compute="_set_shift", store=True)
    special_working_shift = fields.Many2one('special.attendance', string='Special Working Hours', compute="_set_shift", store=True)
    is_special = fields.Boolean(string="Is Special", default=False, compute="_set_shift", store=True)
    #============== Digisphere Customizations (start) ==============#

    check_in_date = fields.Date(string="Check In (Date)", compute="_set_checkin_date_and_time", store=True)
    check_in_time = fields.Char(string="Check In (Time)", compute="_set_checkin_date_and_time", store=True)
    check_out_date = fields.Date(string="Check Out (Date)", compute="_set_checkout_date_and_time", store=True)
    check_out_time = fields.Char(string="Check Out (Time)", compute="_set_checkout_date_and_time", store=True)
    check_in_timezone = fields.Datetime(string="Check In (GMT +3)", compute="_set_check_timezone", store=True)
    check_out_timezone = fields.Datetime(string="Check Out (GMT +3)", compute="_set_check_timezone", store=True)

    auto_adjust = fields.Float(string="Auto Adjust (in minutes)", default=0.00, compute="_compute_real_morning_lateness",store=True)

    weekday_num = fields.Integer('Weekday from working hours', default=0, compute="_compute_weekday", store=True) # Was used, now only for future use !
    attendance_id = fields.Many2one('resource.calendar.attendance', compute="_compute_weekday", store=True)
    special_attendance_id = fields.Many2one('special.attendance.attendance', compute="_compute_weekday", store=True)

    @api.one
    @api.depends('check_in', 'check_out', 'allowed_leave','working_shift','special_working_shift','is_special')
    def _compute_weekday(self):
        if self.check_out:
            last_real_normal_attendance_v = 0
            selected_attendance_id = False
            selected_counter = 0
            real_normal_attendance_v = 0
            if not self.is_special:
                attendance_ids = self.working_shift.attendance_ids
                lunch_state = self.working_shift.lunch_state
                working_shift = self.working_shift
            else:
                attendance_ids = self.special_working_shift.attendance_ids
                lunch_state = self.special_working_shift.lunch_state
                working_shift = self.special_working_shift
            counter = 0
            attendance_temp = False
            for attendance_id in attendance_ids:
                check_in_fulldate = to_tz(self.check_in, self.tz_name)
                check_out_fulldate = to_tz(self.check_out, self.tz_name)
                if (str(attendance_id.dayofweek) == str(check_in_fulldate.weekday())):
                    counter = counter + 1
                    attendance_temp = attendance_id
                    if not (attendance_id.holiday_box):
                        check_in_date = datetime.strptime(datetime.strftime(check_in_fulldate, "%d/%m/%Y"), "%d/%m/%Y")
                        check_out_date = datetime.strptime(datetime.strftime(check_out_fulldate, "%d/%m/%Y"), "%d/%m/%Y")
                        dates_delta = check_out_date-check_in_date
                        check_out_time = datetime.strptime(datetime.strftime(check_out_fulldate, "%H:%M:%S"), "%H:%M:%S")+dates_delta
                        check_in_time = datetime.strptime(datetime.strftime(check_in_fulldate, "%H:%M:%S"), "%H:%M:%S")
                        lunch_break_from_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(attendance_id.lunch_break_from) * 60, 60))
                        lunch_break_from_time = datetime.strptime(lunch_break_from_time_string, "%H:%M")
                        lunch_break_to_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(attendance_id.lunch_break_to) * 60, 60))
                        lunch_break_to_time = datetime.strptime(lunch_break_to_time_string, "%H:%M")
                        if working_shift.dynamic_working:
                            if self.auto_adjust < 0:
                                minutes_to_shift = self.auto_adjust
                                total_hours = float(attendance_id.hour_from)
                                while (minutes_to_shift < 0):
                                    minutes_to_shift += 60
                                    total_hours -= 1.00
                                actual_starting_time_string = (datetime.now().replace(hour=0, minute=0, second=0) + timedelta(hours=total_hours, minutes=minutes_to_shift)).strftime("%H:%M")
                                actual_starting_time = datetime.strptime(actual_starting_time_string, "%H:%M")
                            else:
                                actual_starting_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod((float(attendance_id.hour_from) + (self.auto_adjust / 60.0))* 60, 60))
                                actual_starting_time_string = correctMinutesRounding(actual_starting_time_string)
                                actual_starting_time = datetime.strptime(actual_starting_time_string, "%H:%M")
                        else:
                            actual_starting_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod((float(attendance_id.hour_from)) * 60, 60))
                            actual_starting_time_string = correctMinutesRounding(actual_starting_time_string)
                            actual_starting_time = datetime.strptime(actual_starting_time_string, "%H:%M")
                        actual_ending_time_with_lunch_state = float(attendance_id.hour_to)
                        if (lunch_state):
                            if ((attendance_id.lunch_break_from == 0.00) and (attendance_id.lunch_break_to == 0.00)):
                                # No change, No lunch break
                                # actual_ending_time_with_lunch_state = actual_ending_time_with_lunch_state
                                pass
                            elif (check_out_time<lunch_break_from_time):
                                # No lunch break
                                pass
                            elif (check_out_time>=lunch_break_from_time):
                                if (check_out_time>=lunch_break_to_time):
                                    lunch_hours = attendance_id.lunch_break_to - attendance_id.lunch_break_from
                                    actual_ending_time_with_lunch_state = actual_ending_time_with_lunch_state - lunch_hours
                                else: # Here where the check out is between the lunch break from and to
                                    lunch_hours_delta = check_out_time-lunch_break_from_time
                                    lunch_hours_hours = (lunch_hours_delta.total_seconds()/3600)
                                    actual_ending_time_with_lunch_state = actual_ending_time_with_lunch_state - lunch_hours_hours
                        if working_shift.dynamic_working:
                            if (float(actual_ending_time_with_lunch_state) + (self.auto_adjust / 60.0)) < 0:
                                minutes_to_shift = self.auto_adjust
                                total_hours = float(actual_ending_time_with_lunch_state)
                                while (minutes_to_shift < 0):
                                    minutes_to_shift += 60
                                    total_hours -= 1.00
                                actual_ending_time_string = (datetime.now().replace(hour=0, minute=0, second=0) + timedelta(hours=total_hours, minutes=minutes_to_shift)).strftime("%H:%M")
                                actual_ending_time_string = correctMinutesRounding(actual_ending_time_string)
                                actual_ending_time_string, delta_days = correctHoursShifting(actual_ending_time_string)
                                actual_ending_time = datetime.strptime(actual_ending_time_string, "%H:%M") + timedelta(days=delta_days)
                            else:
                                # print(*divmod((float(actual_ending_time_with_lunch_state)+(self.auto_adjust/60.0)) * 60, 60))
                                actual_ending_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod((float(actual_ending_time_with_lunch_state)+(self.auto_adjust/60.0)) * 60, 60))
                                actual_ending_time_string = correctMinutesRounding(actual_ending_time_string)
                                actual_ending_time_string, delta_days = correctHoursShifting(actual_ending_time_string)
                                # print(actual_ending_time_string)
                                actual_ending_time = datetime.strptime(actual_ending_time_string, "%H:%M") + timedelta(days=delta_days )
                        else:
                            # print(*divmod((float(actual_ending_time_with_lunch_state)) * 60, 60))
                            actual_ending_time_string = '{0:02.0f}:{1:02.0f}'.format(*divmod((float(actual_ending_time_with_lunch_state)) * 60, 60))
                            actual_ending_time_string = correctMinutesRounding(actual_ending_time_string)
                            actual_ending_time_string, delta_days = correctHoursShifting(actual_ending_time_string)
                            # print(actual_ending_time_string)
                            actual_ending_time = datetime.strptime(actual_ending_time_string, "%H:%M") + timedelta(days=delta_days)
                        if (check_in_time<=actual_starting_time):
                            check_in_final = actual_starting_time
                        else:
                            if (check_in_time<actual_ending_time):
                                check_in_final = check_in_time
                            else:
                                check_in_final = False
                        if (check_out_time>=actual_ending_time):
                            check_out_final=actual_ending_time
                        else:
                            check_out_final=check_out_time

                        if (check_in_final and check_out_final):
                            delta = check_out_final-check_in_final
                            total_hours = (delta.total_seconds() / 3600.0)
                            real_normal_attendance_v = total_hours
                        else:
                            real_normal_attendance_v = 0
                    else:
                        real_normal_attendance_v = 0
                if real_normal_attendance_v > last_real_normal_attendance_v:
                    last_real_normal_attendance_v = real_normal_attendance_v
                    selected_attendance_id = attendance_temp
                    selected_counter = counter
            if selected_attendance_id == False: #  This means the employee is working on a holiday
                for attendance_id in attendance_ids:
                    if attendance_id.holiday_box:
                        selected_attendance_id = attendance_id
                        break
            if not self.is_special:
                self.attendance_id = selected_attendance_id
            else:
                self.special_attendance_id = selected_attendance_id
            self.weekday_num = selected_counter
        else:
            self.weekday_num = 0

    @api.one
    @api.depends('check_in','check_out')
    def _set_check_timezone(self):
        if self.check_in:
            self.check_in_timezone = to_tz(self.check_in, self.tz_name)
        if self.check_out:
            self.check_out_timezone = to_tz(self.check_out, self.tz_name)

    @api.one
    @api.depends('check_out')
    def _set_checkout_date_and_time(self):
        if self.check_out:
            check_out_fulldate = to_tz(self.check_out, self.tz_name)
            check_out_time = datetime.strptime(datetime.strftime(check_out_fulldate, "%H:%M:%S"), "%H:%M:%S")
            check_out_date = datetime.strptime(datetime.strftime(check_out_fulldate, "%d/%m/%Y"), "%d/%m/%Y")
            self.check_out_time = check_out_time.time()
            self.check_out_date = check_out_date.date()

    @api.one
    @api.depends('check_in')
    def _set_checkin_date_and_time(self):
        if self.check_in:
            check_in_fulldate = to_tz(self.check_in, self.tz_name)
            check_in_time = datetime.strptime(datetime.strftime(check_in_fulldate, "%H:%M:%S"), "%H:%M:%S")
            check_in_date = datetime.strptime(datetime.strftime(check_in_fulldate, "%d/%m/%Y"), "%d/%m/%Y")
            self.check_in_time = check_in_time.time()
            self.check_in_date = check_in_date.date()

    # ============== Digisphere Customizations (end) ==============#

    @api.one
    @api.depends('employee_id','check_in')
    def _set_shift(self):
        if self.employee_id:
            self.working_shift = self.employee_id.resource_calendar_id
            attendance_special = self.employee_id.special_attendance
            if attendance_special != False:
                if self.employee_id.special_attendance.start_date and self.employee_id.special_attendance.end_date:
                    if (self.check_in >= self.employee_id.special_attendance.start_date and self.check_in <= self.employee_id.special_attendance.end_date):
                        self.is_special = True
                        self.special_working_shift = self.employee_id.special_attendance

    @api.one
    @api.depends('check_in', 'check_out', 'allowed_leave','working_shift','special_working_shift','is_special','auto_adjust','attendance_id', 'special_attendance_id')
    def _compute_OT1_attendance(self):
        if self.check_out:
            if not self.is_special:
                attendance_id = self.attendance_id
                rounding_ids = self.working_shift.ot_rules
                allow_overtime_rounding = self.working_shift.allow_overtime_rounding
                working_shift = self.working_shift
            else:
                attendance_id = self.special_attendance_id
                rounding_ids = self.special_working_shift.ot_rules
                allow_overtime_rounding = self.special_working_shift.allow_overtime_rounding
                working_shift = self.special_working_shift
            check_in_fulldate = to_tz(self.check_in, self.tz_name)
            check_out_fulldate = to_tz(self.check_out, self.tz_name)
            if not (attendance_id.holiday_box):
                # check_in_date = datetime.strptime(datetime.strftime(check_in_fulldate, "%d/%m/%Y"), "%d/%m/%Y")
                total_hours = check_out_fulldate - check_in_fulldate
                total_hours = (total_hours.total_seconds() / 3600)
                if total_hours > working_shift.hours_per_day:
                    overtime_hours = total_hours - working_shift.hours_per_day
                else:
                    overtime_hours = 0.00
                self.real_OT1_attendance = overtime_hours
                overtime_hours = round_total_hours(overtime_hours, rounding_ids, allow_overtime_rounding)  # Round Overtime
                self.OT1_attendance = overtime_hours
            else:
                self.OT1_attendance = 0.00
                self.real_OT1_attendance = 0.00
        else:
            self.OT1_attendance = 0.00
            self.real_OT1_attendance = 0.00

    @api.one
    @api.depends('check_in', 'check_out', 'allowed_leave','working_shift','special_working_shift','is_special','auto_adjust','attendance_id', 'special_attendance_id')
    def _compute_normal_attendance(self):
        if self.check_out:
            if not self.is_special:
                attendance_id = self.attendance_id
                rounding_ids = self.working_shift.nw_rules
                allow_normal_rounding = self.working_shift.allow_normal_rounding
                lunch_state = self.working_shift.lunch_state
                working_shift = self.working_shift
            else:
                attendance_id = self.special_attendance_id
                rounding_ids = self.special_working_shift.nw_rules
                allow_normal_rounding = self.special_working_shift.allow_normal_rounding
                lunch_state = self.special_working_shift.lunch_state
                working_shift = self.special_working_shift
            check_in_fulldate = to_tz(self.check_in, self.tz_name)
            check_out_fulldate = to_tz(self.check_out, self.tz_name)
            # print("Normal Attendance: (Day): "+str(attendance_id.name))
            # print("Normal Attendance: (work from): "+str(attendance_id.hour_from))
            # print("Normal Attendance: (work to): "+str(attendance_id.hour_to))
            # print("Auto Adjust: "+str(self.auto_adjust))
            if not (attendance_id.holiday_box):
                total_hours = check_out_fulldate - check_in_fulldate
                total_hours = (total_hours.total_seconds() / 3600)
                if total_hours > working_shift.hours_per_day:
                    normal_hours = working_shift.hours_per_day
                else:
                    normal_hours = total_hours
                self.real_normal_attendance = normal_hours
                total_hours = round_total_hours(normal_hours, rounding_ids, allow_normal_rounding)  # Round Normal Time
                self.normal_attendance = normal_hours
            else:
                self.normal_attendance = 0.00
                self.real_normal_attendance = 0.00
        else:
            self.normal_attendance = 0.00
            self.real_normal_attendance = 0.00

    @api.one
    @api.depends('check_in', 'check_out', 'allowed_leave','working_shift','special_working_shift','is_special','auto_adjust','attendance_id', 'special_attendance_id')
    def _compute_lateness(self):
        if self.check_out:
            if not self.is_special:
                attendance_id = self.attendance_id
                rounding_ids = self.working_shift.nw_rules
                allow_normal_rounding = self.working_shift.allow_normal_rounding
                lunch_state = self.working_shift.lunch_state
                working_shift = self.working_shift
            else:
                attendance_id = self.special_attendance_id
                rounding_ids = self.special_working_shift.nw_rules
                allow_normal_rounding = self.special_working_shift.allow_normal_rounding
                lunch_state = self.special_working_shift.lunch_state
                working_shift = self.special_working_shift
            check_in_fulldate = to_tz(self.check_in, self.tz_name)
            check_out_fulldate = to_tz(self.check_out, self.tz_name)
            # print("Normal Attendance: (Day): "+str(attendance_id.name))
            # print("Normal Attendance: (work from): "+str(attendance_id.hour_from))
            # print("Normal Attendance: (work to): "+str(attendance_id.hour_to))
            # print("Auto Adjust: "+str(self.auto_adjust))
            if not (attendance_id.holiday_box):
                total_hours = check_out_fulldate - check_in_fulldate
                total_hours = (total_hours.total_seconds() / 3600)
                if total_hours < working_shift.hours_per_day:
                    lateness_hours = working_shift.hours_per_day-total_hours
                else:
                    lateness_hours = 0.00
                self.lateness = lateness_hours
            else:
                self.lateness = 0.00
        else:
            self.lateness = 0.00

    def recalculateRecord(self):
        self._compute_weekday()
        self._compute_normal_attendance()
        self._compute_OT1_attendance()
        self._compute_lateness()
