from odoo import models

class PublisherWarrantyContract(models.AbstractModel):
    _inherit = "publisher_warranty.contract"

    def update_notification(self, cron_mode=True):
        return False
        # if version_info[5] == "e":
        return super(PublisherWarrantyContract, self).update_notification(
            cron_mode=cron_mode
        )
