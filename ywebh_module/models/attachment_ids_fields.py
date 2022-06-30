# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    selected_bank_information = fields.Many2one('res.company.bank', string='Bank Information', store=True)
    payment_schedule = fields.One2many('payment.schedule', 'related_sale_order', string='Payment Schedule')

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.company_id:
            if res.company_id.banks_information:
                bank_var = False
                for bank in res.company_id.banks_information:
                    bank_var = bank
                res.selected_bank_information = bank_var
        return res

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    selected_bank_information = fields.Many2one('res.company.bank', compute='getSelectedBankFromSaleOrder', readonly=False, string='Bank Information', store=True)

    @api.depends('origin')
    def getSelectedBankFromSaleOrder(self):
        for record in self:
            if record.origin:
                sale_order = record.env['sale.order'].search([('name', '=', record.origin)], limit=1)
                if sale_order:
                    record.selected_bank_information = sale_order.selected_bank_information

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

class JournalEntry(models.Model):
    _inherit = 'account.move'

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')