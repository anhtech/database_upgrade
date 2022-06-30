# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    indemnity_years = fields.Integer(store=True, readonly=True)
    social_allowance = fields.Many2one('hr.salary.rule', store=True)

