from odoo import models, fields, api, _
import json

class AccountInvoice_payments(models.Model):
    _inherit = 'account.invoice'


    has_payment = fields.Boolean(string="Is Invoice Has Payment", compute='_compute_has_payment')

    def _compute_has_payment(self):
        for record in self:
            payment_ids = []
            print(record.payments_widget)
            payments = json.loads(record.payments_widget)
            if payments:
                for payment in payments["content"]:
                    payment_ids.append(payment["account_payment_id"])
                if len(payment_ids)>0:
                    record.has_payment = True
                else:
                    record.has_payment = False
            else:
                record.has_payment = False

    @api.multi
    def button_payments(self):
        if self.has_payment:
            payment_ids = []
            for payment in json.loads(self.payments_widget)["content"]:
                payment_ids.append(payment["account_payment_id"])
            action = {'name': _("Invoice's payments"), 'view_type': 'form', 'view_mode': 'tree,form',
                      'res_model': 'account.payment', 'view_id': False, 'type': 'ir.actions.act_window',
                      'domain': [('id', 'in', [id for id in payment_ids])],
                      'views': [(self.env.ref('account.view_account_payment_tree').id, 'tree'),
                                (self.env.ref('account.view_account_payment_form').id, 'form')]}
            return action