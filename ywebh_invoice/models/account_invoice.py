from odoo import models, fields

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    req_ref = fields.Char(string="Request Reference")
