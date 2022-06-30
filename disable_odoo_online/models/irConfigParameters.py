from odoo import api, fields, models
from odoo.tools import config, ormcache, mute_logger, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import datetime

from dateutil.relativedelta import relativedelta
import uuid

_default_parameters2 = {
    "database.secret": lambda: str(uuid.uuid4()),
    "database.uuid": lambda: str(uuid.uuid1()),
    "database.create_date": fields.Datetime.now,
    "database.expiration_date": fields.Datetime.now,
    "web.base.url": lambda: "http://localhost:%s" % config.get('http_port'),
    "base.login_cooldown_after": lambda: 10,
    "base.login_cooldown_duration": lambda: 60,
}

class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    def init(self, force=False):
        self = self.with_context(prefetch_fields=False)
        for key, func in _default_parameters2.items():
            # force=True skips search and always performs the 'if' body (because ids=False)
            params = self.sudo().search([('key', '=', key)])
            if force or not params:
                params.set_param(key, func())




