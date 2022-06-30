# -*- coding: utf-8 -*-

from odoo import models

class LeavesFix(models.Model):
    _inherit = 'hr.leave'

    def _get_number_of_days(self, date_from, date_to, employee_id):
        days_count = super(LeavesFix, self)._get_number_of_days(date_from, date_to, employee_id)
        if self.request_unit_half:
            if days_count==1.0: # Make use of actual _get_number_of_days function, to check whether this day is a holiday or not (1.0 means it is not a holiday, 0.0 means it is a holiday)
                # If it is a holiday then,
                # Both values should be the same '0'
                return 0.5 # Return a constant value since the employee can select only one date to take a half day holiday
        return days_count
