from odoo import models, fields, api, _

class SaleTerms(models.Model):
    _name = 'sale.terms'
    _description = 'Terms and Conditions'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Terms & Conditions Reference", store=True, required=True)
    terms_html = fields.Html(string='Description', store=True)
