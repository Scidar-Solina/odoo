# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    # Default feedback templates for employees and managers

    def _get_default_appraisal_confirm_mail_template(self):
        return self.env.ref('hr_appraisal.mail_template_appraisal_confirm', raise_if_not_found=False)

    # Automated appraisal settings
    appraisal_plan = fields.Boolean(string="Automatically Generate Appraisals", default=True)
    assessment_note_ids = fields.One2many('hr.performance.note', 'company_id', string="Assessment Notes")
    appraisal_confirm_mail_template = fields.Many2one(
        'mail.template', string="Appraisal Confirmation Email",
        domain="[('model', '=', 'hr.performance')]",
        default=_get_default_appraisal_confirm_mail_template
    )
    
    # Appraisal scheduling settings
    duration_after_recruitment = fields.Integer(string="Initial Appraisal (Months)", default=6)
    duration_first_appraisal = fields.Integer(string="First Appraisal After (Months)", default=6)
    duration_next_appraisal = fields.Integer(string="Subsequent Appraisals After (Months)", default=12)

    _sql_constraints = [(
        'positive_number_months',
        'CHECK(duration_after_recruitment > 0 AND duration_first_appraisal > 0 AND duration_next_appraisal > 0)',
        "The duration must be at least 1 month."
    )]

    @api.model
    def _get_default_assessment_note_ids(self):
        return [
            (0, 0, {'name': _('Needs Improvement'), 'sequence': 1}),
            (0, 0, {'name': _('Meets Expectations'), 'sequence': 2}),
            (0, 0, {'name': _('Exceeds Expectations'), 'sequence': 3}),
            (0, 0, {'name': _('Strongly Exceeds Expectations'), 'sequence': 4}),
        ]

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        default_notes = self._get_default_assessment_note_ids()
        res.sudo().write({
            'assessment_note_ids': default_notes,
            'appraisal_employee_feedback_template': self._get_default_employee_feedback_template(),
            'appraisal_manager_feedback_template': self._get_default_manager_feedback_template(),
        })
        return res

    def _create_new_appraisal(self, employees):
        """Create appraisals automatically based on scheduling rules."""
        days_in_advance = int(self.env['ir.config_parameter'].sudo().get_param(
            'hr_appraisal.appraisal_create_in_advance_days', 8
        ))
        appraisal_values = [{
            'company_id': employee.company_id.id,
            'employee_id': employee.id,
            'date_close': employee.next_appraisal_date + relativedelta(days=days_in_advance),
            'manager_ids': [(4, employee.parent_id.id)] if employee.parent_id else False,
            'state': 'pending',
            'employee_feedback_published': False,
            'manager_feedback_published': False,
        } for employee in employees]
        return self.env['hr.performance'].create(appraisal_values)

    @api.model
    def _get_employee_start_date_field(self):
        """Defines which field determines an employee’s start date."""
        self.ensure_one()
        return 'create_date'

    def _run_employee_appraisal_plans(self):
        """Scheduled CRON job for auto-generating appraisals."""
        companies = self.env['res.company'].search([('appraisal_plan', '=', True)])
        current_date = fields.Date.today()
        all_employees = self.env['hr.employee'].search([
            ('next_appraisal_date', '<=', current_date),
            ('company_id', 'in', companies.ids)
        ])
        if all_employees:
            appraisals = self._create_new_appraisal(all_employees)
            for appraisal in appraisals:
                appraisal.employee_id.sudo().write({
                    'last_appraisal_id': appraisal.id,
                    'last_appraisal_date': current_date,
                })
            appraisals._generate_activities()
