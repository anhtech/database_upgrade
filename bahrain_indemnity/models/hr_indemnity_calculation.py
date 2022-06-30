# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class HrIndemnityCalculation(models.TransientModel):
    _name = 'hr.indemnity.calculation'
    _description = "This module will calculate the indemnity amount."

    def cron_calculate_indemnity(self):
        employee_ids = self.env['hr.employee'].search([('eligible_indemnity', '=', True), ('contract_id', '!=', False)])
        for employee_id in employee_ids:
            contract_id = employee_id.contract_id
            # Unapproved years should be deleted and consider a new request instead of the old ones!
            unapproved_indemnity = self.env['hr.contract.indemnity'].search([('employee_id', '=', employee_id.id), ('contract_id', '=', contract_id.id), ('state', '=', 'draft')], order='create_date desc', limit=1)
            current_contract_years = contract_id.indemnity_years
            current_accrual_years = employee_id.indemnity_years
            isAutoApprove = self.env['ir.config_parameter'].sudo().get_param('bahrain_indemnity_com.hr_employee_indemnity_auto_approve')
            calculation_type = self.env['ir.config_parameter'].sudo().get_param('bahrain_indemnity_com.hr_employee_indemnity_calculation')  # Reminder: if calculation_type == true -> It means depending only on last salary.
            # print("calculation_type: "+str(calculation_type))
            if calculation_type == False:
                if unapproved_indemnity:
                    current_contract_years = unapproved_indemnity.indemnity_years
                    current_accrual_years -= contract_id.indemnity_years+unapproved_indemnity.indemnity_years

            total_contract_years = int(relativedelta(datetime.datetime.now().date(), datetime.datetime.strptime(contract_id.date_start, DEFAULT_SERVER_DATE_FORMAT).date()).years)
            # print(total_contract_years)
            # print(current_contract_years)
            if (total_contract_years - current_contract_years) <= 0:
                continue
            else:
                employee_payslip_id = self.env['hr.payslip'].search([('employee_id', '=', employee_id.id), ('isBasicSalary', '=', True)], order='date_to desc', limit=1)
                if employee_payslip_id:
                    if employee_payslip_id.basicSalary == 0.0:
                        salary = contract_id.wage
                    else:
                        salary = employee_payslip_id.basicSalary
                    if employee_payslip_id.socialAllowance == 0.0:
                        if contract_id.social_allowance:
                            if contract_id.social_allowance.amount_select == 'fix':
                                salary += contract_id.social_allowance.amount_fix * contract_id.social_allowance.quantity
                    else:
                        salary += employee_payslip_id.socialAllowance
                else:
                    salary = contract_id.wage
                    if contract_id.social_allowance:
                        if contract_id.social_allowance.amount_select == 'fix':
                            salary += contract_id.social_allowance.amount_fix * contract_id.social_allowance.quantity
                # if contract_id.social_allowance:
                #     if contract_id.social_allowance.amount_select == 'fix':
                #         salary += contract_id.social_allowance.amount_fix * contract_id.social_allowance.quantity
                total_years = total_contract_years - current_contract_years
                total_years_calc = total_years
                indemnity_amount = 0.0
                while(total_years_calc):
                    if current_accrual_years < 3:
                        indemnity_type = "Half"
                    else:
                        indemnity_type = "Full"
                    if indemnity_type == "Half":
                        indemnity_amount += salary/2.0
                    else:
                        indemnity_amount += salary
                    total_years_calc -= 1
                    current_accrual_years += 1
                indemnity_id = self.env['hr.contract.indemnity'].create({
                    'employee_id': employee_id.id,
                    'contract_id': contract_id.id,
                    'currency_id': contract_id.currency_id.id,
                    'indemnity_years': current_contract_years+total_years,
                    'basic_salary': salary,
                    'state': 'draft',
                })
                indemnity_line_id = self.env['hr.contract.indemnity.line'].create({
                    'indemnity_id': indemnity_id.id,
                    'employee_id': employee_id.id,
                    'contract_id': contract_id.id,
                    'currency_id': contract_id.currency_id.id,
                    'current_amount': employee_id.indemnity_amount,
                    'additional_amount': indemnity_amount,
                })
                indemnity_id.indemnity_line = indemnity_line_id
                if calculation_type:
                    for line in unapproved_indemnity:
                        line.unlink()
                else:
                    if isAutoApprove:
                        indemnity_id.approveIndemnity()

