from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type2 = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')], string='Product Type', default='service', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')

    @api.onchange('type2')
    def onTypeChange(self):
        self.type = self.type2
