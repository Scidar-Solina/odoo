# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HrPerformanceGoal(models.Model):
    _name = "hr.performance.goal"
    _description = "Performance Goals"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "deadline asc, state desc"

    name = fields.Char(string="Goal Title", required=True, tracking=True)
    performance_id = fields.Many2one(
        'hr.performance', string="Performance Review", required=True, ondelete='cascade')
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", related="performance_id.employee_id", store=True, readonly=True)
    company_id = fields.Many2one(
        'res.company', string="Company", related="performance_id.company_id", store=True, readonly=True)
    description = fields.Text(string="Goal Description", required=True)
    deadline = fields.Date(string="Deadline", required=True, tracking=True)
    
    state = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default="not_started", tracking=True)

    progress = fields.Integer(string="Progress (%)", default=0, tracking=True)

    def action_start(self):
        """Mark goal as 'In Progress'"""
        self.write({'state': 'in_progress'})

    def action_complete(self):
        """Mark goal as 'Completed'"""
        self.write({'state': 'completed', 'progress': 100})

    def action_cancel(self):
        """Mark goal as 'Cancelled'"""
        self.write({'state': 'cancelled', 'progress': 0})
