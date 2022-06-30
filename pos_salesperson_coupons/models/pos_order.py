# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    salesperson_id = fields.Many2one('sales.person', "Salesperson")
    coupon_id = fields.Many2one('pos.coupon.salesperson', "Coupon")

    @api.model
    def _order_fields(self, ui_order):
        result = super(PosOrder, self)._order_fields(ui_order)
        if ui_order['coupon']:
            result['coupon_id'] = ui_order['coupon']['id']
        if ui_order['salesperson_id']:
            result['salesperson_id'] = ui_order['salesperson_id']['id']
        return result

    @api.model
    def _process_order(self, pos_order):
        order_id = super(PosOrder, self)._process_order(pos_order)
        if order_id.coupon_id:
            order_id.coupon_id.number_of_used += 1
            self.env['pos.coupon.used'].create({
                'coupon_id': order_id.coupon_id.id,
                'salesperson_id': order_id.salesperson_id.id,
                'pos_order_id': order_id.id,
            })
        return order_id
