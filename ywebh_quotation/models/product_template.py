from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_sale = fields.Html(
            'Sale Description', translate=True,
            help="A description of the Product that you want to communicate to your customers. "
                 "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note")

    @api.onchange('description_sale')
    def _onDescriptionChange(self):
        if self.description_sale:
            self.description_sale = self.description_sale.replace('<p>', '').replace('</p>', '<br/>')
