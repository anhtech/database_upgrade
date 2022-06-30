from odoo import api, models, _, fields

class az_hr_holiday_status(models.Model):
    _inherit = 'hr.leave.type'

    leave_pay = fields.Selection([('full', 'Full Paid'), ('half', 'Half Paid'), ('not_paid', 'Not Paid')], string='Type', store=True, default='full', required=True)
