from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_advance = fields.Monetary(string='Advanced Amount', store=True, default=0)
    amount_advance_percentage = fields.Integer(compute="_computeAdvancePaymentPercentage")
    sales_term = fields.Many2one('sale.terms', string="Terms & Conditions", store=True)

    @api.multi
    @api.depends('amount_advance')
    def _computeAdvancePaymentPercentage(self):
        for record in self:
            if record.amount_advance > 0 and record.amount_total > 0:
                ratio = record.amount_advance/record.amount_total
                record.amount_advance_percentage = ratio*100
            else:
                record.amount_advance_percentage = 0

    @api.onchange('amount_advance')
    def _onAmountAdvanceChange(self):
        if self.amount_advance < 0:
            raise UserError(_('The advance payment amount can not be in negative!'))

