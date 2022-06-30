from odoo import models, fields, api, _
from odoo.tools import float_round
HOURS_PER_DAY = 8

class RamadanBaby(models.Model):
    _name = 'special.attendance'
    _description = 'Indicates which employee have a special attendance timing.'

    def _get_default_attendance_ids_special(self):
        return [
            (0, 0, {'name': _('Saturday'), 'dayofweek': '5', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in': 10, 'grace_time_out': 3, 'lunch_break_from': 11.00, 'lunch_break_to': 11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Sunday'), 'dayofweek': '6', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in': 10, 'grace_time_out': 3, 'lunch_break_from': 11.00, 'lunch_break_to': 11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Monday'), 'dayofweek': '0', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in': 10, 'grace_time_out': 3, 'lunch_break_from': 11.00, 'lunch_break_to': 11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Tuesday'), 'dayofweek': '1', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in': 10, 'grace_time_out': 3, 'lunch_break_from': 11.00, 'lunch_break_to': 11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Wednesday'), 'dayofweek': '2', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in': 10, 'grace_time_out': 3, 'lunch_break_from': 11.00, 'lunch_break_to': 11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Thursday'), 'dayofweek': '3', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in': 10, 'grace_time_out': 3, 'lunch_break_from': 11.00, 'lunch_break_to': 11.50, 'ot1_from': 15.51, 'ot1_to': 19.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': False}),
            (0, 0, {'name': _('Friday'), 'dayofweek': '4', 'hour_from': 7.00, 'hour_to': 15.50, 'grace_time_in': 10, 'grace_time_out': 3, 'lunch_break_from': 11.00, 'lunch_break_to': 11.50, 'ot1_from': 0.00, 'ot1_to': 0.00, 'ot2_from': 19.01, 'ot2_to': 23.00, 'night_shift_box': False, 'holiday_box': True})
        ]

    name = fields.Char(required=True)
    hours_per_day = fields.Float("Average hour per day", default=HOURS_PER_DAY, help="Average hours per day a resource is supposed to work with this calendar.")
    lunch_state = fields.Boolean(string="Auto Lunch State", defualt=False,
                                 help="If enabled, this option will allow the employee to have a lunch break during his/her working time. (30 minutes will be taken of total working time for each day)",
                                 store=True)
    dynamic_working = fields.Boolean("Is Dynamic Working Hours", defualt=False, store=True)
    allow_overtime_rounding = fields.Boolean("Allow Overtime Rounding", compute="_compute_is_overtime_rounding",
                                             defualt=False, store=True)
    allow_normal_rounding = fields.Boolean("Allow Normal Rounding", compute="_compute_is_normal_rounding",
                                           defualt=False, store=True)
    attendance_ids = fields.Many2many('special.attendance.attendance', string='Working Time', copy=True, default=_get_default_attendance_ids_special)
    deduction_ids = fields.One2many('special.attendance.deduction', 'calendar_id', string='Deduction Rules', copy=True)
    ot_rules = fields.One2many('special.attendance.otrounding', 'calendar_id', string='Overtime Rounding', copy=True)
    nw_rules = fields.One2many('special.attendance.nwrounding', 'calendar_id', string='Rounding', copy=True)
    start_date = fields.Datetime('Start Date', default=fields.Datetime.now, required=True, store=True)
    end_date = fields.Datetime('End Date', required=True, store=True)

    @api.onchange('attendance_ids')
    def _onchange_hours_per_day(self):
        attendances = self.attendance_ids
        hour_count = 0.0
        for attendance in attendances:
            hour_count += attendance.hour_to - attendance.hour_from
        if attendances:
            self.hours_per_day = float_round(hour_count / float(len(set(attendances.mapped('dayofweek')))), precision_digits=2)

    @api.one
    def change_auto_lunch_state(self):
        if (self.lunch_state):
            self.lunch_state = False
        else:
            self.lunch_state = True

    @api.one
    @api.depends('ot_rules')
    def _compute_is_overtime_rounding(self):
        if self.ot_rules:
            if len(self.ot_rules) > 0:
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

class RamadanBabyAttendance(models.Model):
    _name = "special.attendance.attendance"
    _description = "Work Detail"
    _order = 'dayofweek, hour_from'

    name = fields.Char(required=True)
    date_from = fields.Date(string='Starting Date')
    date_to = fields.Date(string='End Date')
    hour_from = fields.Float(string='Work from', required=True, index=True,
        help="Start and End time of working.\n"
             "A specific value of 24:00 is interpreted as 23:59:59.999999.")
    hour_to = fields.Float(string='Work to', required=True)
    lunch_break_from = fields.Float(string='Lunch From', help="Lunch break to decide when the employee is having the lunch break.", required=True, index=True, default=0.00)
    lunch_break_to = fields.Float(string='Lunch To', help="Lunch break to decide when the employee is having the lunch break.", required=True, default=0.00)
    ot1_from = fields.Float(string='OT1 From', help="Overtime 1 will be calculated as 1.25 of the original normal working hours.", required=True, index=True)
    ot1_to = fields.Float(string='OT1 To', help="Overtime 1 will be calculated as 1.25 of the original normal working hours.", required=True)
    ot2_from = fields.Float(string='OT2 From', help="Overtime 2 will be calculated as 1.50 of the original normal working hours.", required=True, index=True)
    ot2_to = fields.Float(string='OT2 To', help="Overtime 2 will be calculated as 1.50 of the original normal working hours.", required=True)
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

class RamadanBabyDeductionRules(models.Model):
    _name = "special.attendance.deduction"
    _description = "Deduction Rules"
    _order = 'hour_from'

    log_type = fields.Selection([
        ('0', 'Check In'),
        ('1', 'Check Out')
        ], 'Log Type', required=True, index=True, default='0')
    hour_from = fields.Float(string='From', required=True)
    hour_to = fields.Float(string='To', required=True)
    deduction_min = fields.Float(string="Deduction", required=True)
    calendar_id = fields.Many2one("special.attendance", string="Resource's Calendar", required=True, ondelete='cascade')

class RamadanBabyOvertimeRoundingRules(models.Model):
    _name = "special.attendance.otrounding"
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
    calendar_id = fields.Many2one("special.attendance", string="Resource's Calendar", required=True, ondelete='cascade')

class RamadanBabyNormalWorkingRoundingRules(models.Model):
    _name = "special.attendance.nwrounding"
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