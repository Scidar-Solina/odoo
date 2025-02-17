# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import logging
import pytz

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import format_date

_logger = logging.getLogger(__name__)

class HrPerformance(models.Model):
    _name = "hr.performance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Appraisal"
    _order = 'state desc, id desc'
    _rec_name = 'employee_id'
    _mail_post_access = 'read'

    def _get_default_employee(self):
        if self.env.context.get('active_model') in ('hr.employee', 'hr.employee.public') and 'active_id' in self.env.context:
            return self.env.context.get('active_id')
        elif self.env.context.get('active_model') == 'res.users' and 'active_id' in self.env.context:
            return self.env['res.users'].browse(self.env.context['active_id']).employee_id
        if not self.env.user.has_group('hr_appraisal.group_hr_appraisal_user'):
            return self.env.user.employee_id

    active = fields.Boolean(default=True)
    employee_id = fields.Many2one(
        'hr.employee', required=True, string='Employee', index=True,
        default=_get_default_employee)
    next_appraisal_date = fields.Date(string="Next Appraisal Date")
    employee_user_id = fields.Many2one('res.users', string="Employee User", related='employee_id.user_id')
    company_id = fields.Many2one('res.company', related='employee_id.company_id', store=True)
    department_id = fields.Many2one(
        'hr.department', compute='_compute_department_id', string='Department', store=True)
    image_128 = fields.Image(related='employee_id.image_128')
    image_1920 = fields.Image(related='employee_id.image_1920')
    avatar_128 = fields.Image(related='employee_id.avatar_128')
    avatar_1920 = fields.Image(related='employee_id.avatar_1920')
    last_appraisal_id = fields.Many2one('hr.performance', related='employee_id.last_appraisal_id')
    last_appraisal_date = fields.Date(related='employee_id.last_appraisal_date')
    employee_appraisal_count = fields.Integer(related="employee_id.appraisal_count", store=True)
    uncomplete_goals_count = fields.Integer(related='employee_id.uncomplete_goals_count')

    date_close = fields.Date(
        string='Appraisal Date', help='Date of the appraisal, automatically updated when the appraisal is Done or Cancelled.', required=True, index=True,
        default=lambda self: datetime.date.today() + relativedelta(months=+1))
    state = fields.Selection(
        [('new', 'To Confirm'),
        ('pending', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', "Cancelled")],
        string='Status', tracking=True, required=True, copy=False,
        default='new', index=True, group_expand='_group_expand_states')
    manager_ids = fields.Many2many(
        'hr.employee', 'performance_manager_rel', 'hr_appraisal_id',
        context={'active_test': False},
        domain="[('id', '!=', employee_id), ('active', '=', 'True'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    manager_user_ids = fields.Many2many('res.users', string="Manager Users", compute='_compute_user_manager_rights')
    meeting_ids = fields.Many2many('calendar.event', string='Meetings')
    meeting_count_display = fields.Char(string='Meeting Count', compute='_compute_meeting_count')
    date_final_interview = fields.Date(string="Final Interview", compute='_compute_final_interview')
    is_manager = fields.Boolean(compute='_compute_user_manager_rights')
    employee_autocomplete_ids = fields.Many2many('hr.employee', compute='_compute_user_manager_rights')
    waiting_feedback = fields.Boolean(
        string="Waiting Feedback from Employee/Managers", compute='_compute_waiting_feedback')
    review_part_b_ids = fields.One2many(
        'hr.performance.review.part.b',
        'performance_id',
        string="Contributions & Feedback"
    )
    employee_feedback = fields.Html(compute='_compute_employee_feedback', store=True, readonly=False)
    show_employee_feedback_full = fields.Boolean(compute='_compute_show_employee_feedback_full')
    manager_feedback = fields.Html(compute='_compute_manager_feedback', store=True, readonly=False)
    show_manager_feedback_full = fields.Boolean(compute='_compute_show_manager_feedback_full')
    employee_feedback_published = fields.Boolean(string="Employee Feedback Published", default=True, tracking=True)
    manager_feedback_published = fields.Boolean(string="Manager Feedback Published", default=True, tracking=True)
    can_see_employee_publish = fields.Boolean(compute='_compute_buttons_display')
    can_see_manager_publish = fields.Boolean(compute='_compute_buttons_display')
    assessment_note = fields.Many2one('hr.performance.note', string="Final Rating", help="This field is not visible to the Employee.", domain="[('company_id', '=', company_id)]")
    note = fields.Html(string="Private Note", help="The content of this note is not visible by the Employee.")
    appraisal_plan_posted = fields.Boolean()
    appraisal_properties = fields.Properties("Properties", definition="department_id.appraisal_properties_definition", precompute=False)

    # New fields to match the performance review template structure
    goal_ids = fields.One2many('hr.performance.goal', 'performance_id')
    current_position = fields.Char(string="Current Position", help="Employee's current position as per review")
    last_promotion_date = fields.Date(string="Date of Last Promotion", help="Employee's last promotion date")
    rating_ids = fields.One2many(
        'hr.performance.rating',
        'performance_id',
        string="Ratings",
        default=lambda self: self._default_rating_ids()
    )
    prof_skills_id = fields.One2many(
        'hr.performance.profession',
        'performance_id', 
        string="Professionalism", 
        ondelete='cascade'
    )
    firm_skills_ids = fields.One2many(
        'hr.performance.firm.leadership',
        'performance_id', 
        string="Firm Leadership", 
        ondelete='cascade'
    )
    team_skills_id = fields.One2many(
        'hr.performance.team',
        'performance_id', 
        string="Team Leadership Skills", 
        ondelete='cascade'
    )
    comms_skills_id = fields.One2many(
        'hr.performance.communication',
        'performance_id', 
        string="Communication Skills", 
        ondelete='cascade'
    )
    work_skills_id = fields.One2many(
        'hr.performance.product.work',
        'performance_id', 
        string="Productivity and Work Output", 
        ondelete='cascade'
    )

    computer_skills_id = fields.One2many(
        'hr.performance.computer.skills',
        'performance_id', 
        string="Computer Skills", 
        ondelete='cascade'
    )
    
    problem_solving_id = fields.Many2one(
        'hr.performance.problem.solving', 
        string="Problem Solving Section", 
        ondelete='cascade'
    )
    overall_employee_rating = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Overall Employee Rating", help="Employee's overall self-rating")
    overall_reviewer_rating = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Overall Reviewer Rating", help="Reviewer's overall rating")
    major_contributions = fields.Html(string="Major Contributions", help="Major contributions and deliverables in the review cycle")
    development_objectives = fields.Html(string="Development Objectives", help="Development objectives for the next review cycle")
    first_supervisor_comments = fields.Html(string="First Supervisor Comments", help="Comments from the first supervisor")
    second_supervisor_comments = fields.Html(string="Second Supervisor Comments", help="Comments from the second supervisor")
    principals_comments = fields.Html(string="Principal's Comments", help="FInal Comments from the Principal")
    first_supervisor_id = fields.Many2one('res.users', string="First Supervisor", help="First Supervisor/Reviewer's user")
    second_supervisor_id = fields.Many2one('res.users', string="Second Supervisor", help="Second Supervisor/Reviewer's user")
    overall_rating = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Overall Rating", help="Overall rating for the performance review")

    @api.model
    def _default_rating_ids(self):
        """Automatically create default lines for the Quantitative column."""
        lines = []
        # 1) Grab the competency record for 'Quantitative Reasoning' if that’s how you have named it:
        quantitative_competency = self.env['hr.performance.competency'].search(
            [('name', '=', 'Problem Solving')],  # adapt to however you name that competency
            limit=1
        )

        print(quantitative_competency)
       
        # 2) Build the default line(s).  For example, we can just create one line with defaults:
        if quantitative_competency:
            print(quantitative_competency.id)
            lines.append(
                (0, 0, {
                    'competency_id': quantitative_competency.id,
                    'description': 'data_analytics',   # or whichever selection value you want
                    'employee_rating': '3',            # default rating
                    'reviewer_rating': '3',            # default rating
                    'comments': '',                    # can also prefill comments if desired
                })
            )
        return lines

    @api.depends('employee_id')
    def _compute_department_id(self):
        for appraisal in self:
            if appraisal.employee_id:
                appraisal.department_id = appraisal.employee_id.department_id
            else:
                appraisal.department_id = False

    @api.depends_context('uid')
    @api.depends('employee_id', 'manager_ids')
    def _compute_buttons_display(self):
        new_appraisals = self.filtered(lambda a: a.state == 'new')
        new_appraisals.update({
            'can_see_employee_publish': False,
            'can_see_manager_publish': False,
        })
        user_employee = self.env.user.employee_id
        is_manager = self.env.user.user_has_groups('hr_appraisal.group_hr_appraisal_user')
        for appraisal in self:
            appraisal.can_see_employee_publish = (user_employee == appraisal.employee_id) or \
                (user_employee.id in appraisal.manager_ids.ids and appraisal.state == 'new')
            appraisal.can_see_manager_publish = user_employee.id in appraisal.manager_ids.ids
        for appraisal in self - new_appraisals:
            if is_manager and not appraisal.can_see_employee_publish and not appraisal.can_see_manager_publish:
                appraisal.can_see_employee_publish, appraisal.can_see_manager_publish = True, True

    @api.depends_context('uid')
    @api.depends('manager_ids', 'employee_id', 'employee_id.parent_id')
    def _compute_user_manager_rights(self):
        self.employee_autocomplete_ids = self.env.user.get_employee_autocomplete_ids()
        for appraisal in self:
            appraisal.manager_user_ids = appraisal.manager_ids.user_id
            appraisal.is_manager =\
                self.user_has_groups('hr_appraisal.group_hr_appraisal_user')\
                or self.env.user.employee_id in (appraisal.manager_ids | appraisal.employee_id.parent_id)

    @api.depends_context('uid')
    @api.depends('employee_id', 'employee_feedback_published')
    def _compute_show_employee_feedback_full(self):
        for appraisal in self:
            is_appraisee = appraisal.employee_id.user_id == self.env.user
            appraisal.show_employee_feedback_full = is_appraisee and not appraisal.employee_feedback_published

    @api.depends_context('uid')
    @api.depends('manager_ids', 'manager_feedback_published')
    def _compute_show_manager_feedback_full(self):
        for appraisal in self:
            is_appraiser = self.env.user in appraisal.manager_ids.user_id
            appraisal.show_manager_feedback_full = is_appraiser and not appraisal.manager_feedback_published

    # @api.depends('department_id')
    # def _compute_employee_feedback(self):
    #     for appraisal in self.filtered(lambda a: a.state in ['new', 'pending']):
    #         employee_template = appraisal.department_id.employee_feedback_template if appraisal.department_id.custom_appraisal_templates \
    #             else appraisal.company_id.appraisal_employee_feedback_template
    #         if appraisal.state == 'new':
    #             appraisal.employee_feedback = employee_template
    #         else:
    #             appraisal.employee_feedback = appraisal.employee_feedback or employee_template

    # @api.depends('department_id')
    # def _compute_manager_feedback(self):
    #     for appraisal in self.filtered(lambda a: a.state in ['new', 'pending']):
    #         manager_template = appraisal.department_id.manager_feedback_template if appraisal.department_id.custom_appraisal_templates \
    #             else appraisal.company_id.appraisal_manager_feedback_template
    #         if appraisal.state == 'new':
    #             appraisal.manager_feedback = manager_template
    #         else:
    #             appraisal.manager_feedback = appraisal.manager_feedback or manager_template

    @api.depends('department_id', 'company_id')
    def _compute_feedback_templates(self):
        for appraisal in self:
            appraisal.employee_feedback_template = appraisal.department_id.employee_feedback_template if appraisal.department_id.custom_appraisal_templates \
                else appraisal.company_id.appraisal_employee_feedback_template
            appraisal.manager_feedback_template = appraisal.department_id.manager_feedback_template if appraisal.department_id.custom_appraisal_templates \
                else appraisal.company_id.appraisal_manager_feedback_template

    @api.depends('employee_feedback_published', 'manager_feedback_published')
    def _compute_waiting_feedback(self):
        for appraisal in self:
            appraisal.waiting_feedback = not appraisal.employee_feedback_published or not appraisal.manager_feedback_published

    @api.depends_context('uid')
    @api.depends('meeting_ids.start')
    def _compute_final_interview(self):
        today = fields.Date.today()
        user_tz = self.env.user.tz or self.env.context.get('tz')
        user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc
        with_meeting = self.filtered('meeting_ids')
        (self - with_meeting).date_final_interview = False
        for appraisal in with_meeting:
            all_dates = appraisal.meeting_ids.mapped('start')
            min_date, max_date = min(all_dates), max(all_dates)
            if min_date.date() >= today:
                appraisal.date_final_interview = min_date.astimezone(user_pytz)
            else:
                appraisal.date_final_interview = max_date.astimezone(user_pytz)

    @api.depends_context('lang')
    @api.depends('meeting_ids')
    def _compute_meeting_count(self):
        today = fields.Date.today()
        for appraisal in self:
            count = len(appraisal.meeting_ids)
            if not count:
                appraisal.meeting_count_display = _('No Meeting')
            elif count == 1:
                appraisal.meeting_count_display = _('1 Meeting')
            elif appraisal.date_final_interview >= today:
                appraisal.meeting_count_display = _('Next Meeting')
            else:
                appraisal.meeting_count_display = _('Last Meeting')

    def _group_expand_states(self, states, domain, order):
        return [key for key, val in self._fields['state'].selection]

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self = self.sudo()  # fields are not on the employee public
        if self.employee_id:
            manager = self.employee_id.parent_id
            self.manager_ids = manager if manager != self.employee_id else False
            self.department_id = self.employee_id.department_id

    def subscribe_employees(self):
        for appraisal in self:
            partners = appraisal.manager_ids.mapped('related_partner_id') | appraisal.employee_id.related_partner_id
            appraisal.message_subscribe(partner_ids=partners.ids)

    def send_appraisal(self):
        for appraisal in self:
            confirmation_mail_template = appraisal.company_id.appraisal_confirm_mail_template
            mapped_data = {
                **{appraisal.employee_id: confirmation_mail_template},
                **{manager: confirmation_mail_template for manager in appraisal.manager_ids}
            }
            for employee, mail_template in mapped_data.items():
                if not employee.work_email or not self.env.user.email or not mail_template:
                    continue
                ctx = {
                    'employee_to_name': appraisal.employee_id.name,
                    'recipient_users': employee.user_id,
                    'url': '/mail/view?model=%s&res_id=%s' % ('hr.performance', appraisal.id),
                }
                mail_template = mail_template.with_context(**ctx)
                subject = mail_template._render_field('subject', appraisal.ids)[appraisal.id]
                body = mail_template._render_field('body_html', appraisal.ids)[appraisal.id]
                mail_values = {
                    'email_from': self.env.user.email_formatted,
                    'author_id': self.env.user.partner_id.id,
                    'model': None,
                    'res_id': None,
                    'subject': subject,
                    'body_html': body,
                    'auto_delete': True,
                    'email_to': employee.work_email
                }
                template_ctx = {
                    'model_description': self.env['ir.model']._get('hr.performance').display_name,
                    'message': self.env['mail.message'].sudo().new(dict(body=mail_values['body_html'], record_name=_("Appraisal Request"))),
                    'company': self.env.company,
                }
                body = self.env['ir.qweb']._render('mail.mail_notification_light', template_ctx, minimal_qcontext=True, raise_if_not_found=False)
                if body:
                    mail_values['body_html'] = self.env['mail.render.mixin']._replace_local_links(body)
                else:
                    _logger.warning('QWeb template mail.mail_notification_light not found when sending appraisal confirmed mails. Sending without layouting.')

                self.env['mail.mail'].sudo().create(mail_values)

                from_cron = 'from_cron' in self.env.context
                if employee.user_id and not from_cron:
                    appraisal.activity_schedule(
                        'mail.mail_activity_data_todo', appraisal.date_close,
                        summary=_('Appraisal Form to Fill'),
                        note=_('Fill appraisal for %s', appraisal.employee_id._get_html_link()),
                        user_id=employee.user_id.id)

    def action_cancel(self):
        self.state = 'cancel'

    @api.model_create_multi
    def create(self, vals_list):
        appraisals = super().create(vals_list)
        appraisals_to_send = self.env['hr.performance']
        current_date = datetime.date.today()
        for appraisal, vals in zip(appraisals, vals_list):
            if vals.get('state') and vals['state'] == 'pending':
                appraisals_to_send |= appraisal
            if vals.get('state') and vals['state'] == 'new':
                appraisal.employee_id.sudo().write({
                    'last_appraisal_id': appraisal.id,
                    'last_appraisal_date': current_date,
                })
        appraisals_to_send.send_appraisal()
        appraisals.subscribe_employees()
        return appraisals

    def _check_access(self, fields):
        fields = set(fields)
        if {'manager_feedback', 'manager_feedback_published'} & fields:
            if not all(a.can_see_manager_publish for a in self):
                raise UserError(_('The manager feedback cannot be changed by an employee.'))
        if {'employee_feedback'} & fields:
            if not all(a.can_see_employee_publish for a in self):
                raise UserError(_('The employee feedback cannot be changed by managers.'))

    def write(self, vals):
        self._check_access(vals.keys())
        force_published = self.env['hr.performance']
        if vals.get('employee_feedback_published'):
            user_employees = self.env.user.employee_ids
            force_published = self.filtered(lambda a: (a.is_manager) and not (a.employee_feedback_published or a.employee_id in user_employees))
        current_date = datetime.date.today()
        if 'state' in vals and vals['state'] in ['pending', 'done']:
            for appraisal in self:
                appraisal.employee_id.sudo().write({
                    'last_appraisal_id': appraisal.id,
                    'last_appraisal_date': current_date,
                })
        if 'state' in vals and vals['state'] == 'pending':
            for appraisal in self:
                if appraisal.state != 'done':
                    vals['employee_feedback_published'] = False
                    vals['manager_feedback_published'] = False
                    appraisal.activity_feedback(['mail.mail_activity_data_meeting', 'mail.mail_activity_data_todo'])
                    appraisal.send_appraisal()
        if 'state' in vals and vals['state'] == 'done':
            vals['employee_feedback_published'] = True
            vals['manager_feedback_published'] = True
            vals['date_close'] = current_date
            self.activity_feedback(['mail.mail_activity_data_meeting', 'mail.mail_activity_data_todo'])
            self._appraisal_plan_post()
            body = _("The appraisal's status has been set to Done by %s", self.env.user.name)
            appraisal.message_notify(
                body=body,
                subject=_("Your Appraisal has been completed"),
                partner_ids=appraisal.message_partner_ids.ids,
            )
            appraisal.message_post(body=body)
        if 'state' in vals and vals['state'] == 'cancel':
            self.meeting_ids.unlink()
            self.activity_unlink(['mail.mail_activity_data_meeting', 'mail.mail_activity_data_todo'])
        previous_managers = {}
        if 'manager_ids' in vals:
            previous_managers = {x: y for x, y in self.mapped(lambda a: (a.id, a.manager_ids))}
        result = super(HrPerformance, self).write(vals)
        if force_published:
            for appraisal in force_published:
                role = _('Manager') if self.env.user.employee_id in appraisal.manager_ids else _('Appraisal Officer')
                appraisal.message_post(body=_('%(user)s decided, as %(role)s, to publish the employee\'s feedback', user=self.env.user.name, role=role))
        if 'manager_ids' in vals:
            self._sync_meeting_attendees(previous_managers)
        return result

    def _appraisal_plan_post(self):
        return True

    def _generate_activities(self):
        today = fields.Date.today()
        for appraisal in self:
            employee = appraisal.employee_id
            managers = appraisal.manager_ids
            last_appraisal_months = employee.last_appraisal_date and (
                today.year - employee.last_appraisal_date.year)*12 + (today.month - employee.last_appraisal_date.month)
            if employee.user_id:
                if employee.appraisal_count == 1:
                    months = (appraisal.date_close.year - employee.create_date.year) * \
                        12 + (appraisal.date_close.month - employee.create_date.month)
                    note = _("You arrived %s months ago. Your appraisal is created and you can fill it here.", months)
                else:
                    note = _("Your last appraisal was %s months ago. Your appraisal is created and you can fill it here.", last_appraisal_months)
                appraisal.with_context(mail_activity_quick_update=True).activity_schedule(
                    'mail.mail_activity_data_todo', today,
                    summary=_('Appraisal to fill'),
                    note=note, user_id=employee.user_id.id)
                for manager in managers.filtered('user_id'):
                    if employee.appraisal_count == 1:
                        note = _(
                            "The employee %s arrived %s months ago. The appraisal is created and you can fill it here.",
                            employee._get_html_link(), months)
                    else:
                        note = _(
                            "The last appraisal of %s was %s months ago. The appraisal is created and you can fill it here.",
                            appraisal.employee_id._get_html_link(), last_appraisal_months)
                    appraisal.with_context(mail_activity_quick_update=True).activity_schedule(
                        'mail.mail_activity_data_todo', today,
                        summary=_('Appraisal for %s to fill', employee.name),
                        note=note, user_id=manager.user_id.id)

    def _sync_meeting_attendees(self, manager_ids):
        for appraisal in self.filtered('meeting_ids'):
            previous_managers = manager_ids.get(appraisal.id, self.env['hr.employee'])
            to_add = self.manager_ids - previous_managers
            to_del = previous_managers - self.manager_ids
            if to_add or to_del:
                appraisal.meeting_ids.write({
                    'partner_ids': [
                        *[(3, x) for x in to_del.mapped('related_partner_id').ids],
                        *[(4, x) for x in to_add.mapped('related_partner_id').ids],
                    ]
                })

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancel(self):
        if any(appraisal.state not in ['new', 'cancel'] for appraisal in self):
            raise UserError(_("You cannot delete appraisal which is not in draft or canceled state"))

    def read(self, fields=None, load='_classic_read'):
        check_feedback = set(fields) & {'manager_feedback', 'employee_feedback'}
        check_notes = set(fields) & {'note', 'assessment_note'}
        if check_feedback:
            fields = fields + ['can_see_employee_publish', 'can_see_manager_publish', 'employee_feedback_published', 'manager_feedback_published']
        if check_notes:
            fields = fields + ['employee_id']
        records = super().read(fields, load)
        if check_feedback:
            for appraisal in records:
                if not appraisal['can_see_employee_publish'] and not appraisal['employee_feedback_published']:
                    appraisal['employee_feedback'] = _('Unpublished')
                if not appraisal['can_see_manager_publish'] and not appraisal['manager_feedback_published']:
                    appraisal['manager_feedback'] = _('Unpublished')
        if check_notes:
            for appraisal in records:
                if appraisal['employee_id'] == self.env.user.employee_id.id:
                    appraisal['note'] = _('Note')
                    appraisal['assessment_note'] = False
        return records

    @api.model
    def _read_group_check_field_access_rights(self, field_names):
        super()._read_group_check_field_access_rights(field_names)
        if {'manager_feedback', 'employee_feedback'}.intersection(field_names):
            raise UserError(_('Such grouping is not allowed.'))

    def mapped(self, func):
        if func and isinstance(func, str):
            self._check_access(set(func.split('.')))
        return super().mapped(func)

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        fields_list = {term[0] for term in domain if isinstance(term, (tuple, list))}
        self._check_access(fields_list)
        return super()._search(domain, offset, limit, order, access_rights_uid)

    def filtered_domain(self, domain):
        fields_list = {term[0] for term in domain if isinstance(term, (tuple, list))}
        self._check_access(fields_list)
        return super().filtered_domain(domain)

    def action_calendar_event(self):
        self.ensure_one()
        partners = self.manager_ids.mapped('related_partner_id') | self.employee_id.related_partner_id | self.env.user.partner_id
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context'] = {
            'default_partner_ids': partners.ids,
            'default_res_model': 'hr.performance',
            'default_res_id': self.id,
            'default_name': _('Appraisal of %s', self.employee_id.name),
        }
        return action

    def action_confirm(self):
        self.state = 'pending'

    def action_done(self):
        self.state = 'done'

    def action_back(self):
        self.state = 'new'

    def action_open_employee_appraisals(self):
        self.ensure_one()
        view_id = self.env.ref('hr_appraisal.hr_appraisal_view_tree_orderby_create_date').id
        return {
            'name': _('Previous Appraisals'),
            'res_model': 'hr.performance',
            'view_mode': 'tree,kanban,form,gantt,calendar,activity',
            'views': [(view_id, 'tree'), (False, 'kanban'), (False, 'form'), (False, 'gantt'), (False, 'calendar'), (False, 'activity')],
            'domain': [('employee_id', '=', self.employee_id.id)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'search_default_groupby_date_close': True,
            }
        }

    def action_open_goals(self):
        self.ensure_one()
        return {
            'name': _("%s's Goals", self.employee_id.name),
            'view_mode': 'kanban,tree,form,graph',
            'res_model': 'hr.performance.goal',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }

    def action_send_appraisal_request(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'request.appraisal',
            'target': 'new',
            'name': _('Appraisal Request'),
            'context': {'default_appraisal_id': self.id},
        }
    def subscribe_employees(self):
        for appraisal in self:
            # Get partners (managers and employee)
            partners = appraisal.manager_ids.filtered(lambda m: m.user_id).mapped('user_id.partner_id')
            if appraisal.employee_id.user_id:
                partners |= appraisal.employee_id.user_id.partner_id
            # Subscribe partners to the appraisal
            appraisal.message_subscribe(partner_ids=partners.ids)

    def action_generate_part_a_lines(self):
        """Create rating lines for each competency so user doesn't have to add them manually."""
        all_competencies = self.env['hr.performance.competency'].search([])
        for comp in all_competencies:
            self.env['hr.performance.rating'].create({
                'performance_id': self.id,
                'employee_rating': '3',  # default?
                'reviewer_rating': '3', # default?
            })
        return True
    

class HrPerformanceRating(models.Model): 
    _name = "hr.performance.rating" 
    _description = "Performance Competency Rating"

    res_model = fields.Char(string="Related Model", default="hr.performance", readonly=True)
    competency_id = fields.Many2one('hr.performance.competency', string="Quantitavive Reasoning", required=False)
    problem_solving_id = fields.Many2one(
        'hr.performance.problem.solving',
        string="Problem Solving Reference"
    )
    objectives = fields.Char(
        string="Specific Objectives",
        readonly=True
    ) 
    performance_id = fields.Many2one('hr.performance', string="Performance Review", required=True, ondelete='cascade')
    # description = fields.Text(string="Quantitative reasoning", help="Placeholder description of what's expected.")

    description = fields.Selection([
        ('quantitative_reasoning', 'Quantitative Reasoning'),
        ('analytical_reasoning', 'Analytical reasoning'),
        ('accuracy_detail_mindedness', 'Accuracy & Detail Mindedness'),
        ('thought_structuring', 'Thought Structuring'),
    ], string="Competency", required=True)
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


    @api.onchange('description')
    def _onchange_description(self):
        # Map competencies to specific objectives
        competency_objectives_map = {
            'quantitative_reasoning': 'Routinely solves basic arithmetic/algebra on his/her feet and appropriately applies same to his/her work.',
            'analytical_reasoning': 'Understands complex concepts quickly and can establish implications for his/her work.',
            'accuracy_detail_mindedness': 'Completes work output with NO arithmetical, typographical, or formatting errors.',
            'thought_structuring': 'Consistently applies logical structure to thoughts by breaking complex problems into fragments and solving them individually.',
        }
        if self.description:
            self.objectives = competency_objectives_map.get(self.description, '')
        else:
            self.objectives = ''
    # @api.depends('problem_solving_id.quantiObjectives')
    # def _compute_objectives(self):
    #     for record in self:
    #         if record.problem_solving_id:
    #             record.objectives = record.problem_solving_id.quantiObjectives
    #         else:
    #             record.objectives = False  # Clear the field if no reference is set



class HrPerformanceRatingCategory(models.Model):
    _name = 'hr.performance.rating.category'
    _description = 'Rating Category for Performance Review'

    name = fields.Char(string="Category Name", required=True)
    description = fields.Text(string="Description", help="Short placeholder for expected outcomes.")
    sequence = fields.Integer(string="Sequence", default=10)
    # competency_ids = fields.One2many('hr.performance.competency', 'category_id', string="Competencies")


class HrPerformanceCompetency(models.Model):
    _name = 'hr.performance.competency'
    _description = 'Performance Competency'

    name = fields.Char(string="Competency Name", required=True)
    category_id = fields.Many2one('hr.performance.rating.category', string="Category", required=True)
    description = fields.Text(string="Expected Outcome", help="Placeholder description of what's expected.")
    sequence = fields.Integer(string="Sequence", default=10)


class HrPerformanceReviewPartB(models.Model):
    _name = 'hr.performance.review.part.b'
    _description = 'Part B: Major Contributions and Manager Feedback'

    performance_id = fields.Many2one(
        'hr.performance',
        string="Performance Review",
        required=True,
        ondelete='cascade'
    )
    contributions = fields.Text(
        string="Major Contributions & Deliverables",
        required=True,
        help="Highlight significant contributions across workstreams within the organisation since your last review."
    )
    assignment_details = fields.Text(
        string="Assignment Details",
        help="For each assignment, specify the activities and output delivered (include specific examples where applicable)."
    )
    development_objectives = fields.Text(
        string="Development Objectives for Next Review Cycle",
        help="Document specific and measurable on-the-job and personal goals/objectives for the new review cycle."
    )
    reviewee_comments = fields.Text(
        string="Reviewee Comments",
        help="Comments on the performance appraisal process by the reviewee."
    )
    first_reviewer_id = fields.Many2one(
        'hr.employee',
        string="First Reviewer",
        required=True,
        help="The direct surpervisor who performs the review ."
    )
    first_reviewer_comments = fields.Text(
        string="First Reviewer Comments",
        help="Manager’s initial comments on the contributions."
    )
    first_reviewer_overall_rating = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="First Overall Rating", required=True)
    second_reviewer_comments = fields.Text(
        string="Second Reviewer Comments",
        help="Additional manager comments (second review)."
    )
    second_reviewer_overall_rating = fields.Selection([
        ('1', '1: Unsatisfactory'),
        ('2', '2: Needs Improvement'),
        ('3', '3: Meets Expectation'),
        ('4', '4: Exceeds Expectation'),
        ('5', '5: Exceptional'),
    ], string="Second Overall Rating", required=True)
    second_reviewer_id = fields.Many2one(
        'hr.employee',
        string="Second Reviewer",
        required=True,
        help="The manager who performs the review."
    )
    capacity_development_needs = fields.Text(
        string="Capacity Development Needs",
        help="Identify specific capacity development needs and suggest options (e.g., cross-training, developmental assignments, projects, informal/formal training) for improvement."
    )