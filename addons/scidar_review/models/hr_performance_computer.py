from odoo import api, fields, models, _


class HrPerformanceComputer(models.Model): 
    _name = "hr.performance.computer.skills" 
    _description = "Performance Competency Communication"

    res_model = fields.Char(string="Related Model", default="hr.performance", readonly=True)
    objectivescom = fields.Char(
        string="Specific Objectives",
        readonly=True
    ) 
    performance_id = fields.Many2one('hr.performance', string="Performance Review", required=True, ondelete='cascade')    # description = fields.Text(string="Quantitative reasoning", help="Placeholder description of what's expected.")

    descriptionscom = fields.Selection([
        ('powerpoint', 'PowerPoint'),
        ('data_analytics_excel', 'Data Analytics, Excel and Chart'),
        ('word', 'Word'),
        ('other_relevant_software', 'Other Relevant Software'),
    ], string="Competency", required=True)
    employee_ratingcom = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Employee Rating", required=True)
    reviewer_ratingcom = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Reviewer Rating", required=True)
    commentscom = fields.Html(string="Rating Comments")


    @api.onchange('descriptionscom')
    def _onchange_description(self):
        competency_objectives_map = {
            # New mappings for communication skills
            'powerpoint': 'Makes SCIDaR standardized PowerPoint slides that meet specifications in SCIDaR PPT manual, with minimal need for edits in format, font, color.',
            'data_analytics_excel': 'Shows moderate excel analytical capabilities - has built a moderately complex model with use of routine functions such as vlookup, multiple page linkages etc. Models meet SCIDaR structure and formatting specifications. Uses thinkcell charting appropriately with minimal errors.',
            'word': 'Writes vertical documents that are appropriately laid out, formatted and reflect SCIDaR quality of finishing, with minimal formatting errors.',
            'other_relevant_software': 'Demonstrated interest and aptitude for rapidly learning usage of new software that is relevant to project / client work.',

        }

        if self.descriptionscom:
            self.objectivescom = competency_objectives_map.get(self.descriptionscom, '')
        else:
            self.objectivescom = ''