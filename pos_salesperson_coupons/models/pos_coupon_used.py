# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosCouponUsed(models.Model):
    _name = 'pos.coupon.used'
    _description = 'Used Coupon'
    _rec_name = 'coupon_id'

    company_id = fields.Many2one('res.company', related="coupon_id.company_id", readonly=True)
    currency_id = fields.Many2one('res.currency', related="coupon_id.currency_id", readonly=True)

    coupon_id = fields.Many2one('pos.coupon.salesperson', string="Coupon Code", required=True, readonly=True)
    used_datetime = fields.Datetime('Used on', default=fields.Datetime.now, readonly=True)
    salesperson_id = fields.Many2one('sales.person', "Salesperson", readonly=True)
    pos_order_id = fields.Many2one('pos.order', required=True, readonly=True)
    amount_total = fields.Float(string='Total', related="pos_order_id.amount_total", readonly=True)
    commission_amount = fields.Monetary(string='Commission', compute="_computeCommissionAmount", currency_field='currency_id')

    @api.multi
    @api.depends('coupon_id', 'amount_total')
    def _computeCommissionAmount(self):
        for record in self:
            if record.coupon_id:
                if record.coupon_id.salesperson_commission:
                    record.commission_amount = (record.coupon_id.salesperson_commission/100.0)*record.amount_total
                else:
                    record.commission_amount = 0
            else:
                record.commission_amount = 0
