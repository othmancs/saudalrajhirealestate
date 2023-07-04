# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def create(self, vals):
        if 'parent_id' in vals and vals['parent_id'] and not self.env.user.user_has_groups('project_security.project_sub_task_create_group'):
            raise UserError(
                _('You do not have permission to create Sub-Task contact you administrator'))
        return super(ProjectTask, self).create(vals)


class ProjectProject(models.Model):
    _inherit = "project.project"


    def write(self, vals):
        result = super(ProjectProject, self).write(vals)
        if 'stage_id' in vals and vals['stage_id'] and not self.env.user.user_has_groups('project_security.project_update_state_group'):
                raise UserError(
                    _('You do not have permission to update stage contact you administrator'))
        return result
