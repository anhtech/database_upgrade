# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrContractIndemnityLine(models.Model):
    _name = 'hr.contract.indemnity.line'
    _description = "This module will handle the variables for the indemnity record."

    indemnity_id = fields.Many2one('hr.contract.indemnity')
    employee_id = fields.Many2one(related='indemnity_id.employee_id')
    contract_id = fields.Many2one(related='indemnity_id.contract_id')
    currency_id = fields.Many2one(related='indemnity_id.currency_id')

    current_amount = fields.Monetary(string="Current Indemnity Amount", compute="_computeCurrentAmount", store=True)
    additional_amount = fields.Monetary(string="Additional Indemnity Amount", store=True, default=0, track_visibility='onchange')
    new_amount = fields.Monetary(string="New Indemnity Amount", compute="_computeNewAmount", store=True)

    @api.multi
    @api.depends('employee_id')
    def _computeCurrentAmount(self):
        for record in self:
            if record.employee_id:
                record.current_amount = record.employee_id.indemnity_amount
            else:
                record.current_amount = 0

    @api.multi
    @api.depends('current_amount', 'additional_amount')
    def _computeNewAmount(self):
        for record in self:
            new_amount = 0.0
            if record.current_amount:
                new_amount += record.current_amount
            if record.additional_amount:
                new_amount += record.additional_amount
            record.new_amount = new_amount
