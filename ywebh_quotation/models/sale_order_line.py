from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    name = fields.Html(string='Description', required=True,  translate=True)

    def get_sale_order_line_multiline_description_sale(self, product):
        if product.description_sale:
            return product.description_sale.replace('<p>', '').replace('</p></li>', '</li>').replace('</p>', '<br/>')
        else:
            res = super(SaleOrderLine, self).get_sale_order_line_multiline_description_sale(product)
            return res

