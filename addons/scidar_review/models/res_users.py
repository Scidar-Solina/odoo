# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    next_appraisal_date = fields.Date(related='employee_id.next_appraisal_date', string="Next Appraisal Date", store=True)
    last_appraisal_date = fields.Date(related='employee_id.last_appraisal_date', string="Last Appraisal Date", store=True)
    last_appraisal_id = fields.Many2one(related='employee_id.last_appraisal_id', string="Last Appraisal", store=True)

    def get_employee_autocomplete_ids(self):
        """Fetches employees for auto-completion based on the user's role."""
        self.ensure_one()
        Employee = self.env['hr.employee']
        if self.user_has_groups('hr_appraisal.group_hr_appraisal_user'):
            return Employee.search([('company_id', 'in', self.env.companies.ids)])
        user_employees = Employee.search([('user_id', '=', self.env.user.id)])
        children = Employee
        if user_employees:
            children = Employee.search([
                ('id', 'child_of', user_employees.ids),
                ('company_id', 'in', self.env.companies.ids),
            ])
        return children | self.env.user.employee_ids

    @property
    def SELF_READABLE_FIELDS(self):
        """Extends Odoo’s readable fields to include appraisal-related data."""
        return super().SELF_READABLE_FIELDS + [
            'next_appraisal_date',
            'last_appraisal_date',
            'last_appraisal_id',
        ]

    def action_send_appraisal_request(self):
        """Redirects user to create a new appraisal request."""
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'request.appraisal',  # Updated to match our new model
            'name': 'Appraisal Request',
            'context': self.env.context,
        }

    def action_open_last_appraisal(self):
        """Opens the last completed appraisal for the user."""
        self.ensure_one()
        if not self.last_appraisal_id:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'view_mode': 'form',
            'res_model': 'hr.performance',  # Updated from 'hr.appraisal' to match our model
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.last_appraisal_id.id,
        }
