from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    isCheque = fields.Boolean('is Cheque?', default=False)
