# File: models/hr_performance_problem_solving.py
# -*- coding: utf-8 -*-
from odoo import models, fields

class HrPerformanceProblemSolving(models.Model):
    _name = 'hr.performance.problem.solving'
    _description = 'Problem Solving Section'

    performance_id = fields.Many2one(
        'hr.performance', string="Performance Review", required=True, ondelete='cascade')
    employee_rating = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Employee Rating", required=True)

    reviewer_rating = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Reviewer Rating", required=True)
    comments = fields.Html(string="Rating Comments")

    quantiObjectives = fields.Char(
        string="Routinely solves basic arithmetic / algebra on his/her feet and appropriately applies same to his/her work.",
        readonly=True
    )