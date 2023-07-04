from odoo import models, fields, api
from odoo.exceptions import UserError


class ItiStudent(models.Model):
    _name = "iti.student"

    name = fields.Char(required=True)
    email = fields.Char()
    salary = fields.Float()
    tax = fields.Float(compute="calc_salary", store=True)
    net_salary = fields.Float(compute="calc_salary", store=True)
    birthday = fields.Date()
    address = fields.Text()
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female')]
    )
    details = fields.Html()
    login_time = fields.Datetime()
    image = fields.Binary()
    track_id = fields.Many2one("iti.track")
    track_capacity = fields.Integer(related="track_id.capacity")
    skills_ids = fields.Many2many("iti.skills")
    grade = fields.One2many("iti.student.course.line", "student_ids")
    state = fields.Selection(
        [
            ("applied", "Applied"),
            ("first", "First Interview"),
            ("second", "Second Interview"),
            ("passed", "Passed"),
            ("rejected", "rejected"),

        ], default='applied')

    def ChangeState(self):
        if self.state == 'applied':
            self.state = 'first'
        elif self.state == 'first':
            self.state = 'second'
        elif self.state in ['passed', 'rejected']:
            self.state = 'applied'

    def SetPassed(self):
        if self.state == 'second':
            self.state = 'passed'

    def SetRejected(self):
        if self.state == 'second':
            self.state = 'rejected'

    @api.onchange("gender")
    def _on_change_gender(self):
        domain = {'track_id': []}
        if not self.gender:
            self.gender = 'm'
            return {}
        if self.gender == 'm':
            domain = {'track_id': [('is_open', '=', True)]}
            self.salary = 10000
        else:
            self.salary = 5000
        return {
            'warning': {
                'title': 'Hello',
                'message': 'you are change the gender'
            },
            'domain': domain
        }

    @api.model
    def create(self, vals):
        name_split = vals['name'].split()
        vals['email'] = f"{name_split[0][0]}{name_split[1]}@gmail.com"
        search_email = self.search([('email', '=', vals['email'])])
        if search_email:
            raise UserError('email already exist')
        track = self.env['iti.track'].browse(vals['track_id'])
        if track.is_open is False:
            raise UserError('Selected Track Is Close')
        return super().create(vals)


    def write(self, vals):
        if "name" in vals:
            name_split = vals['name'].split()
            vals['email'] = f"{name_split[0][0]}{name_split[1]}@gmail.com"
            search_email = self.search([('email', '=', vals['email'])])
            if search_email:
                raise UserError('email already exist')
        super().write(vals)

    def unlink(self):
        for record in self:
            if record.state in ['passed', 'rejected']:
                raise UserError("You Can't Delete Passed/Rejected Student")
        super().unlink()

    _sql_constraints = [
        ("UniqueName", "UNIQUE(name)", "Name Already Exist")
    ]

    @api.constrains('salary', 'track_id')
    def Check_Salary_Track_id(self):
        for record in self:
            if record.salary > 10000:
                raise UserError('Salary Bigger Than 10000')
        track_count = len(record.track_id.student_ids)
        track_capacity = record.track_id.capacity
        if track_count > track_capacity:
            raise UserError('Track Is Full')

    @api.depends('salary')
    def calc_salary(self):
        for record in self:
            record.tax = record.salary * 0.20
            record.net_salary = record.salary - record.tax


class Course(models.Model):
    _name = "iti.course"
    name = fields.Char()


class StudentCourseGrade(models.Model):
    _name = "iti.student.course.line"
    student_ids = fields.Many2one("iti.student")
    course_ids = fields.Many2one("iti.course")
    grades = fields.Selection([
        ('g', "Good"),
        ('vg', "Very Good")
    ])
