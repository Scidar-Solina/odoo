# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class RequestAppraisal(models.Model):
    _name = "request.appraisal"
    _description = "Appraisal Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "state desc, request_date desc"

    name = fields.Char(string="Request Title", required=True, tracking=True)
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", required=True,
        default=lambda self: self.env.user.employee_id, tracking=True)
    manager_id = fields.Many2one('hr.employee', string="Manager", related='employee_id.parent_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string="Company", related='employee_id.company_id', store=True, readonly=True)
    request_date = fields.Date(string="Request Date", default=fields.Date.today, required=True)
    reason = fields.Text(string="Reason for Appraisal Request", required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string="Status", default="draft", tracking=True)

    appraisal_id = fields.Many2one('hr.performance', string="Linked Appraisal", readonly=True)

    def action_submit(self):
        """Move request to submitted state"""
        self.write({'state': 'submitted'})

    def action_approve(self):
        """Approve request and create a new performance appraisal"""
        appraisal = self.env['hr.performance'].create({
            'employee_id': self.employee_id.id,
            'company_id': self.company_id.id,
            'manager_ids': [(4, self.manager_id.id)] if self.manager_id else False,
            'state': 'pending',
            'date_close': fields.Date.today(),
        })
        self.write({'state': 'approved', 'appraisal_id': appraisal.id})

    def action_reject(self):
        """Reject the appraisal request"""
        self.write({'state': 'rejected'})
