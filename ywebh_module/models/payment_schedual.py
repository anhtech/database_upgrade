from odoo import models, fields, api, _
import datetime

def get_years():
    year_list = []
    for i in range(2016, 2040):
        year_list.append((i, str(i)))
    return year_list

class PaymentSchdule(models.Model):
    _name = "payment.schedule"

    related_sale_order = fields.Many2one('sale.order')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    sequence = fields.Integer()

    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                              (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
                              (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'), ],
                             string='Month', store=True, required=True)
    year = fields.Selection(get_years(), default=datetime.datetime.now().year, string='Year', store=True, required=True)

    payment_date = fields.Date(string='Payment Date', store=True)
    amount = fields.Monetary(string='Amount', currency_field='currency_id', store=True)


