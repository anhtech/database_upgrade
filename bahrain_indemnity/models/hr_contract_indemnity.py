# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class HrContractIndemnity(models.Model):
    _name = 'hr.contract.indemnity'
    _rec_name = 'employee_id'
    _description = "This module will handle the update for the indemnity amount."
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    employee_id = fields.Many2one('hr.employee', string="Employee", track_visibility='onchange')
    contract_id = fields.Many2one('hr.contract', string="Contract", track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string="Currency", compute="_computeCurrency")

    indemnity_years = fields.Integer(string="Indemnity Years", track_visibility='onchange', help="IMPORTANT: This field will show you the indemnity years for this contract only. You need to open the employee page to see the accrual indemnity years.")
    basic_salary = fields.Monetary(string="Basic Salary", default=0, required=True, track_visibility='onchange', help="IMPORTANT: This field will include the social allowance in case you assigned it in the contract.")

    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('cancel', 'Cancelled')], string="Status", readonly=True, track_visibility='onchange', default='draft')

    indemnity_line = fields.One2many('hr.contract.indemnity.line', 'indemnity_id', 'Indemnity Paramters', track_visibility='onchange')

    @api.multi
    def name_get(self):
        super(HrContractIndemnity, self).name_get()
        res = []
        for indemnity in self:
            employee_name = indemnity.employee_id.name
            creation_date = indemnity.create_date
            if creation_date:
                res_name = '(%s) %s' % (creation_date, employee_name)
            else:
                res_name = employee_name
            res.append((indemnity.id, res_name))
        return res

    @api.onchange('employee_id')
    def _onEmployeeChanged(self):
        if self.employee_id:
            self.contract_id = self.employee_id.contract_id
            if self.contract_id:
                self.indemnity_years = self.employee_id.contract_id.indemnity_years

    @api.onchange('contract_id')
    def _onContractChanged(self):
        if self.contract_id:
            self.basic_salary = self.contract_id.wage

    @api.multi
    @api.depends('contract_id')
    def _computeCurrency(self):
        for record in self:
            if record.contract_id:
                record.currency_id = record.contract_id.currency_id
            else:
                record.currency_id = False

    @api.multi
    def resetToDraft(self):
        for record in self:
            if record.state == 'approved':
                raise UserError(_("You can not reset to draft an approved record!"))
            record.state = 'draft'

    @api.multi
    def cancelIndemnity(self):
        for record in self:
            if record.state == 'approved':
                raise UserError(_("You can not cancel an approved record!"))
            record.state = 'cancel'

    @api.multi
    def approveIndemnity(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You need to reset to draft before approving!"))
            if not record.employee_id:
                raise UserError(_("Indemnity can not be approved without employee!"))
            if not record.indemnity_line:
                raise UserError(_("You can not approve an indemnity calculation without any variables (How did you do that???)"))
            elif len(record.indemnity_line.ids) != 1:
                raise UserError(_("You can not approve an indemnity calculation with two lines of variables (How did you do that???)"))
            if not record.basic_salary:
                raise UserError(_("Indemnity can not be approved with no basic salary!"))
            # if not record.indemnity_years:
            #     raise UserError(_("Indemnity can not be approved with no current indemnity years!"))
            indemnity_variables = record.indemnity_line[0]
            if not indemnity_variables.additional_amount:
                raise UserError(_("Additional amount can not be empty!"))
            if indemnity_variables.additional_amount < 0:
                raise UserError(_("Additional amount can not be less than zero!"))
            record.employee_id.indemnity_amount = indemnity_variables.new_amount
            record.employee_id.contract_id.indemnity_years = record.indemnity_years
            record.state = 'approved'

