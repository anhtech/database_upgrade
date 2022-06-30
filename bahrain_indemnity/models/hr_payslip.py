# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    isBasicSalary = fields.Boolean(compute='_isBasicSalaryThere', help="Is basic salary there?")
    basicSalary = fields.Float(compute='_isBasicSalaryThere', help="Basic Salary if exists.")
    socialAllowance = fields.Float(compute='_isBasicSalaryThere', help="Social Allowance if exists.")

    @api.multi
    @api.depends('line_ids')
    def _isBasicSalaryThere(self):
        for record in self:
            if record.line_ids:
                isBasicSalary = False
                basicSalary = 0.0
                socialAllowance = 0.0
                for line in record.line_ids:
                    if line.category_id.name.lower() == "basic":
                        basicSalary = line.total
                        isBasicSalary = True
                    if line.salary_rule_id:
                        if line.salary_rule_id.id == record.contract_id.social_allowance.id:
                            socialAllowance = line.total
                record.isBasicSalary = isBasicSalary
                record.basicSalary = basicSalary
                record.socialAllowance = socialAllowance
            else:
                record.isBasicSalary = False
                record.basicSalary = 0.0
                record.socialAllowance = 0.0
