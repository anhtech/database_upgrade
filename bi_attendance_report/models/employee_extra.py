# -*- coding: utf-8 -*-
from odoo import api, fields, models

class employee_extra(models.Model):
    _name = 'hr.employee.extra'
    _inherit = 'hr.employee'

    loginState = fields.Selection(string="Login State", selection=[
                    ('early', 'Early'),
                    ('ontime', 'On Time'),
                    ('late', 'Late')])


