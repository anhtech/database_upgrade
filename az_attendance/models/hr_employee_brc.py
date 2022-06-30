# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee_inheirt(models.Model):
    _inherit = 'hr.employee'

    employee_religion = fields.Selection(string="Religion", selection=[('Muslim', 'Muslim'), ('Christian', 'Christian'), ('Hindu', 'Hindu'), ('Sikh', 'Sikh'), ('Buddhist', 'Buddhist')])
    special_attendance = fields.Many2one('special.attendance', 'Special Working Hours')
