from odoo import api, fields, models, _


class HrPerformanceComms(models.Model): 
    _name = "hr.performance.communication" 
    _description = "Performance Competency Communication"

    res_model = fields.Char(string="Related Model", default="hr.performance", readonly=True)
    objectivesc = fields.Char(
        string="Specific Objectives",
        readonly=True
    ) 
    performance_id = fields.Many2one('hr.performance', string="Performance Review", required=True, ondelete='cascade')    # description = fields.Text(string="Quantitative reasoning", help="Placeholder description of what's expected.")

    descriptions = fields.Selection([
        ('clarity_conciseness', 'Clarity & Conciseness'),
        ('coherence_storylining', 'Coherence (Storylining)'),
        ('presence_confidence_public_speaking', 'Presence / Confidence / Public Speaking'),
    ], string="Competency", required=True)
    employee_ratingc = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Employee Rating", required=True)
    reviewer_ratingc = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Reviewer Rating", required=True)
    commentsc = fields.Html(string="Rating Comments")


    @api.onchange('descriptions')
    def _onchange_description(self):
        competency_objectives_map = {
            # New mappings for communication skills
            'clarity_conciseness': 'Identifies and corrects grammar, spelling, and syntax errors. Makes tangible effort in concise verbal and written communication (top-down communication).',
            'coherence_storylining': 'Makes tangible progress in developing logical and coherent storylines.',
            'presence_confidence_public_speaking': 'Shows presence in team and client meetings through participation, focus, and body language. Eager to speak up in public/team meetings. Asks intelligent questions and drives discussion workstreams.',
        }

        if self.descriptions:
            self.objectivesc = competency_objectives_map.get(self.descriptions, '')
        else:
            self.objectivesc = ''