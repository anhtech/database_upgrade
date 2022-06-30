# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    paid_with = fields.Many2many('account.journal', 'pos_order_account_journal_rel', 'pos_order_id', 'journal_id', compute="_findJournals")
    notpaid_with = fields.Many2many('account.journal', 'pos_order_account_journal2_rel', 'pos_order_id', 'journal_id', compute="_findJournals")
    currency_id = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")

    @api.multi
    @api.depends('config_id', 'statement_ids')
    def _findJournals(self):
        for record in self:
            paid_journal_ids = []
            notpaid_journal_ids = []
            for statement_line in record.statement_ids:
                if statement_line.journal_id.id not in paid_journal_ids:
                    paid_journal_ids.append(statement_line.journal_id.id)
            for journal_id in record.config_id.journal_ids:
                if journal_id.id not in paid_journal_ids:
                    notpaid_journal_ids.append(journal_id.id)
            record.paid_with = self.env['account.journal'].browse(paid_journal_ids)
            record.notpaid_with = self.env['account.journal'].browse(notpaid_journal_ids)
