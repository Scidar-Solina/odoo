# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrPerformanceNote(models.Model):
    _name = "hr.performance.note"
    _description = "Performance Assessment Note"
    _order = "sequence, id"

    name = fields.Char(required=True, string="Assessment Note")
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True,
        string="Company"
    )
