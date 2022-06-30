from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    banks_information = fields.One2many('res.company.bank', 'related_company_id', string='Bank Information')

class CompanyBankInformation(models.Model):
    _name = "res.company.bank"

    related_company_id = fields.Many2one('res.company')
    name = fields.Char(string='Bank Name', store=True, required=True)
    iban = fields.Char(string='IBAN', store=True, required=True)
    account_number = fields.Char(string='A/C No', store=True, required=True)
    account_name = fields.Char(string='Account Name', store=True, required=True)
    country_id = fields.Many2one('res.country', string='Country', store=True, required=True)
    swift_code = fields.Char(string='Swift', store=True, required=True)
