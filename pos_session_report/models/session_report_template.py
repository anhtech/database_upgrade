# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _

class pos_session_receipt_template(models.AbstractModel):
    _name = 'report.pos_session_report.pos_session_receipt_template'

    @api.multi
    def _get_report_values(self, docids, data=None):
      docargs = {
                  'doc_ids': self.ids,
                  'data':data
                   }
      return docargs



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
