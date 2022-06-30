# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.employee'

    currency_id = fields.Many2one(related='company_id.currency_id')
    indemnity_amount = fields.Monetary(string="Indemnity Amount", store=True, readonly=True, currency_field='currency_id')
    indemnity_years = fields.Integer(readonly=True, compute="_computeAccrual")
    eligible_indemnity = fields.Boolean(string="Eligible for Indemnity?", default=False, store=True)

    @api.multi
    @api.depends('contract_ids')
    def _computeAccrual(self):
        for record in self:
            sum = 0
            for contract_id in record.contract_ids:
                sum += contract_id.indemnity_years
            record.indemnity_years = sum
