# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare, float_round, DEFAULT_SERVER_DATE_FORMAT
import datetime

ignored_cron = []

def get_next_weekday(startdate, weekday):
    d = datetime.datetime.strptime(datetime.date.strftime(startdate, DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
    t = datetime.timedelta((7 + weekday - d.weekday()) % 7)
    return (d + t).strftime(DEFAULT_SERVER_DATE_FORMAT)

class az__brc_attendance_working_hours(models.Model):
    _inherit = 'resource.calendar'

    lunch_state = fields.Boolean(string="Auto Lunch State",defualt=False,help="If enabled, this option will allow the employee to have a lunch break during his/her working time. (30 minutes will be taken of total working time for each day)", store=True)
    allow_overtime_rounding = fields.Boolean("Allow Overtime Rounding", compute="_compute_is_overtime_rounding",
                                             defualt=False, store=True)
    allow_normal_rounding = fields.Boolean("Allow Normal Rounding", compute="_compute_is_normal_rounding",
                                             defualt=False, store=True)
    dynamic_working = fields.Boolean("Is Dynamic Working Hours", defualt=False, store=True)
    is_weekly_group = fields.Boolean("Is Group Weekly Hours", defualt=False, store=True)
    weekly_group = fields.Many2one("resource.calendar", string="Another Group", copy=True, store=True)
    weekly_group_swap = fields.Many2one("resource.calendar", string="Swap(Don't Show)", copy=True)
    nextcall_weekly_group = fields.Date(string="Next call of weekly group", default=datetime.date.today(), store=True)

    @api.model
    def cron_weekly_group(self):
        pass
        # all_calanders = self.env['resource.calendar'].search([])
        # for line in all_calanders:
        #     # print("Start of shift changing !")
        #     if line.is_weekly_group:
        #         today = datetime.datetime.now().date()
        #         if line.nextcall_weekly_group:
        #             nextcall_weekly_group = datetime.datetime.strptime(datetime.date.strftime(line.nextcall_weekly_group, DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT).date()
        #             if nextcall_weekly_group.weekday()==6:
        #                 # print("The next call is already Sunday !")
        #                 if not today==nextcall_weekly_group:
        #                     if not line in ignored_cron:
        #                         # print("Do shift change")
        #                         line.weekly_group_swap = line
        #                         line.attendance_ids = line.weekly_group.attendance_ids
        #                         line.deduction_ids = line.weekly_group.deduction_ids
        #                         line.ot_rules = line.weekly_group.ot_rules
        #                         line.nw_rules = line.weekly_group.nw_rules
        #                         line.weekly_group.attendance_ids = line.weekly_group_swap.attendance_ids
        #                         line.weekly_group.deduction_ids = line.weekly_group_swap.deduction_ids
        #                         line.weekly_group.ot_rules = line.weekly_group_swap.ot_rules
        #                         line.weekly_group.nw_rules = line.weekly_group_swap.nw_rules
        #                         nextSunday_str = get_next_weekday(line.nextcall_weekly_group, 6)
        #                         line.nextcall_weekly_group = datetime.datetime.strptime(nextSunday_str,DEFAULT_SERVER_DATE_FORMAT).date()
        #                         ignored_cron.append(line)
        #                         ignored_cron.append(line.weekly_group)
        #                     else:
        #                         pass
        #                         # print("Ignore them, already shifted !")
        #                 else:
        #                     # print("Remove from ignored_cron")
        #                     if line in ignored_cron:
        #                         ignored_cron.remove(line)
        #                     if line.weekly_group in ignored_cron:
        #                         ignored_cron.remove(line.weekly_group)
        #             else:
        #                 # print("The next call is not sunday !")
        #                 if today.weekday()==6:
        #                     # print("Today is already sunday !")
        #                     line.nextcall_weekly_group = today
        #                 else:
        #                     # print("Today is not sunday !")
        #                     nextSunday_str = get_next_weekday(line.nextcall_weekly_group, 6)
        #                     line.nextcall_weekly_group = datetime.datetime.strptime(nextSunday_str,DEFAULT_SERVER_DATE_FORMAT).date()
        #         else:
        #             if datetime.datetime.now().date().weekday()==6:
        #                 line.nextcall_weekly_group = datetime.datetime.now().date()
        #                 print("The next call is not valid (next call) !")
        #             else:
        #                 nextSunday_str = get_next_weekday(datetime.datetime.strftime(datetime.datetime.now(),DEFAULT_SERVER_DATE_FORMAT), 6)
        #                 line.nextcall_weekly_group = datetime.datetime.strptime(nextSunday_str, DEFAULT_SERVER_DATE_FORMAT).date()
        #                 print("The next call is not valid (Postponed) !")

    @api.one
    @api.depends('is_weekly_group')
    def onWeeklyGroupBooleanChange(self):
        if not self.is_weekly_group:
            self.weekly_group = False
            self.nextcall_weekly_group = False

    @api.one
    @api.depends('hours_per_day')
    def change_auto_lunch_state(self):
        if (self.lunch_state):
            self.lunch_state = False
        else:
            self.lunch_state = True
        self._onchange_hours_per_day()

    @api.onchange('attendance_ids')
    def _onchange_hours_per_day(self):
        super(az__brc_attendance_working_hours, self)._onchange_hours_per_day()
        attendances = self.attendance_ids.filtered(
            lambda attendance: not attendance.date_from and not attendance.date_to)
        hour_count = 0.0
        for attendance in attendances:
            if self.lunch_state == True:
                lunch_time = attendance.lunch_break_to - attendance.lunch_break_from
                if ((attendance.hour_to - attendance.hour_from)-(lunch_time))>=0:
                    hour_count += (attendance.hour_to - attendance.hour_from)-(lunch_time)
            else:
                hour_count += attendance.hour_to - attendance.hour_from
        if attendances:
            self.hours_per_day = float_round(hour_count / float(len(set(attendances.mapped('dayofweek')))),
                                             precision_digits=2)

    def _get_default_attendance_ids(self):
        res = super(az__brc_attendance_working_hours,self).init()
        return [
            (0, 0, {'name': _('Saturday'), 'dayofweek': '5', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Saturday'), 'dayofweek': '5', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Sunday'), 'dayofweek': '6', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Sunday'), 'dayofweek': '6', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Monday'), 'dayofweek': '0', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Monday'), 'dayofweek': '0', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Tuesday'), 'dayofweek': '1', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Tuesday'), 'dayofweek': '1', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Wednesday'), 'dayofweek': '2', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Wednesday'), 'dayofweek': '2', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Thursday'), 'dayofweek': '3', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Thursday'), 'dayofweek': '3', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Friday'), 'dayofweek': '4', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 0.00, 'ot1_to': 0.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': True}),
            (0, 0, {'name': _('Friday'), 'dayofweek': '4', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in':10, 'grace_time_out':3, 'lunch_break_from':11.00, 'lunch_break_to':11.50, 'ot1_from': 0.00, 'ot1_to': 0.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': True}),
        ]

    attendance_ids = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', 'Working Time',
        copy=True, default=_get_default_attendance_ids)
    deduction_ids = fields.One2many('hr.attendance.deduction', 'calendar_id', string='Deduction Rules', copy=True)
    ot_rules = fields.One2many('hr.attendance.otrounding', 'calendar_id', string='Overtime Rounding', copy=True)
    nw_rules = fields.One2many('hr.attendance.nwrounding', 'calendar_id', string='Rounding', copy=True)

    @api.one
    @api.depends('ot_rules')
    def _compute_is_overtime_rounding(self):
        if self.ot_rules:
            if len(self.ot_rules)>0:
                self.allow_overtime_rounding = True
            else:
                self.allow_overtime_rounding = False
        else:
            self.allow_overtime_rounding = False

    @api.one
    @api.depends('nw_rules')
    def _compute_is_normal_rounding(self):
        if self.nw_rules:
            if len(self.nw_rules) > 0:
                self.allow_normal_rounding = True
            else:
                self.allow_normal_rounding = False
        else:
            self.allow_normal_rounding = False


class az_brc_calander_attendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    lunch_break_from = fields.Float(string='Lunch From', help="Lunch break to decide when the employee is having the lunch break.", required=True, index=True, default=0.00)
    lunch_break_to = fields.Float(string='Lunch To', help="Lunch break to decide when the employee is having the lunch break.", required=True, default=0.00)
    ot1_from = fields.Float(string='OT1 From', help="Overtime 1 will be calculated as 1.25 of the original normal working hours.", required=True, index=True, default=0.00)
    ot1_to = fields.Float(string='OT1 To', help="Overtime 1 will be calculated as 1.25 of the original normal working hours.", required=True, default=0.00)
    ot2_from = fields.Float(string='OT2 From', help="Overtime 2 will be calculated as 1.50 of the original normal working hours.", required=True, index=True, default=0.00)
    ot2_to = fields.Float(string='OT2 To', help="Overtime 2 will be calculated as 1.50 of the original normal working hours.", required=True, default=0.00)
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], 'Day of Week', required=True, index=True, default='0')
    grace_time_in = fields.Integer(string='Grace In', default=10, help="Grace Time In (Minutes)", required=True, index=True)
    grace_time_out = fields.Integer(string='Grace Out', default=3, help="Grace Time Out (Minutes)", required=True)
    night_shift_box = fields.Boolean(string="Night Shift", default=False)
    holiday_box = fields.Boolean(string="Holiday", default=False)

class DeductionRules(models.Model):
    _name = "hr.attendance.deduction"
    _description = "Deduction Rules"
    _order = 'hour_from'

    log_type = fields.Selection([
        ('0', 'Check In'),
        ('1', 'Check Out')
        ], 'Log Type', required=True, index=True, default='0')
    hour_from = fields.Float(string='From', required=True)
    hour_to = fields.Float(string='To', required=True)
    deduction_min = fields.Float(string="Deduction", required=True)
    calendar_id = fields.Many2one("resource.calendar", string="Resource's Calendar", required=True, ondelete='cascade')

class OvertimeRoundingRules(models.Model):
    _name = "hr.attendance.otrounding"
    _description = "Overtime Rounding Rules"
    _order = 'hour_from'

    operator = fields.Selection([
        ('<', '<'),
        ('<=', '<='),
        ('=', '=='),
        ('!=', '!='),
        ('>', '>'),
        ('>=', '>=')
        ], 'Operator', required=True, index=True, default='>=')
    hour_from = fields.Float(string='From', required=True)
    hour_to = fields.Float(string='To', required=True)
    calendar_id = fields.Many2one("resource.calendar", string="Resource's Calendar", required=True, ondelete='cascade')

class NormalWorkingRoundingRules(models.Model):
    _name = "hr.attendance.nwrounding"
    _description = "Normal Hours Rounding Rules"
    _order = 'hour_from'

    operator = fields.Selection([
        ('<', '<'),
        ('<=', '<='),
        ('=', '=='),
        ('!=', '!='),
        ('>', '>'),
        ('>=', '>=')
        ], 'Operator', required=True, index=True, default='>=')
    hour_from = fields.Float(string='From', required=True)
    hour_to = fields.Float(string='To', required=True)
    calendar_id = fields.Many2one("resource.calendar", string="Resource's Calendar", required=True, ondelete='cascade')