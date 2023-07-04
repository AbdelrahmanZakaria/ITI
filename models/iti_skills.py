from odoo import models, fields


class ItiSkills(models.Model):
    _name = "iti.skills"
    name = fields.Char()
