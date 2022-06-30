from odoo import api, models, _, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT

# class az_hr_holidays_dates(models.Model):
#     _inherit = 'hr.holidays'
#
#     @api.onchange('date_from')
#     def _onchange_date_from(self):
#         super(az_hr_holidays_dates, self)._onchange_date_from()
#         if self.type=="remove" and self.date_from and self.date_to:
#             date_from_fulldate = datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT).replace(hour=21, minute=00, second=00)-relativedelta(days=1)
#             date_from_new = date_from_fulldate.replace(hour=21, minute=00, second=00)
#             self.date_from = date_from_new
#
#     @api.onchange('date_to')
#     def _onchange_date_to(self):
#         super(az_hr_holidays_dates, self)._onchange_date_to()
#         if self.type=="remove" and self.date_from and self.date_to:
#             date_to_fulldate = datetime.strptime(self.date_to, DEFAULT_SERVER_DATETIME_FORMAT)
#             date_to_new = date_to_fulldate.replace(hour=20, minute=59, second=59)
#             self.date_to = date_to_new

