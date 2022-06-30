# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_employee_indemnity_calculation = fields.Boolean(string="Indemnity Calculation", store=True)
    hr_employee_indemnity_auto_approve = fields.Boolean(string="Auto Approve", store=True)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            hr_employee_indemnity_calculation=self.env['ir.config_parameter'].sudo().get_param('bahrain_indemnity_com.hr_employee_indemnity_calculation'),
            hr_employee_indemnity_auto_approve=self.env['ir.config_parameter'].sudo().get_param('bahrain_indemnity_com.hr_employee_indemnity_auto_approve')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('bahrain_indemnity_com.hr_employee_indemnity_calculation', self.hr_employee_indemnity_calculation)
        self.env['ir.config_parameter'].sudo().set_param('bahrain_indemnity_com.hr_employee_indemnity_auto_approve', self.hr_employee_indemnity_auto_approve)
