from odoo import models, fields, api, _

class EmployeeAssignWizard(models.TransientModel):
    _name = 'employee.assign.wizard'
    _description = 'Employee Assign Work Hours Wizard'

    @api.model
    def _get_employee_ids(self):
        return self.env['hr.employee'].search([('id', 'in', self.env.context.get('active_ids', []))])

    employee_ids = fields.Many2many('hr.employee', string='Employees to assign', default=_get_employee_ids, required=True)
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Hours')

    @api.multi
    def action_employee_assign(self):
        self.ensure_one()
        for employee in self.employee_ids:
            employee.resource_calendar_id = self.resource_calendar_id

class EmployeeAssignSpecialWizard(models.TransientModel):
    _name = 'employee.assign.wizard.special'
    _description = 'Employee Assign Special Work Hours Wizard'

    @api.model
    def _get_employee_ids(self):
        return self.env['hr.employee'].search([('id', 'in', self.env.context.get('active_ids', []))])

    employee_ids = fields.Many2many('hr.employee', string='Employees to assign', default=_get_employee_ids, required=True)
    resource_calendar_id = fields.Many2one('special.attendance', 'Special Working Hours')

    @api.multi
    def action_employee_assign_special(self):
        self.ensure_one()
        for employee in self.employee_ids:
            employee.special_attendance = self.resource_calendar_id