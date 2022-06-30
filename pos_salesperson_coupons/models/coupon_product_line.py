# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CouponProductLine(models.Model):
    _name = 'coupon.product.line'
    _description = 'Coupon Product Line'
    _rec_name = 'product_id'

    coupon_id = fields.Many2one('pos.coupon.salesperson', required=True)
    product_id = fields.Many2one('product.product', "Product", required=True)
    discount_per = fields.Float("Discount (%)", default=0, required=True)
