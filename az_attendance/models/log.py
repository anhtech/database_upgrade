from odoo import models, fields, api, tools
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import pytz

class LogClass(models.Model):
    _name = 'hr.attendance.log'
    _description = 'It stores all the changes happened to attendance records.'

    who_change_it = fields.Many2one('hr.employee', string="Done By", readonly=True, store=True)
    to_who_it_changed = fields.Many2one('hr.employee', string="Employee", readonly=True, store=True)
    attendance_record = fields.Many2one('hr.attendance', string="Attendance Record", readonly=True, store=True)
    reason = fields.Char(string="Reason", store=True)
    changed_on = fields.Datetime('Changed on', default=fields.Datetime.now, readonly=True, store=True)


