from odoo import models, fields, api, _

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    name = fields.Html(string='Description', required=True,  translate=True)

    # A temporary fix for odoo stupid programmers
    def _get_invoice_line_name_from_product(self):
        if self.product_id:
            if self.product_id.description_sale:
                return self.product_id.description_sale.replace('<p>', '').replace('</p></li>', '</li>').replace('</p>', '<br/>')
        res = super(AccountInvoiceLine, self)._get_invoice_line_name_from_product()
        return res
