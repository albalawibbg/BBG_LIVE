# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

from datetime import datetime
from dateutil import relativedelta

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    af_job_id = fields.Many2one(
        'hr.job',
        string='المهنة ',
        tracking=True
    )
    af_employee_age = fields.Char(
        'عمر الموظف',
        compute='_compute_employee_age'
    )
    af_work_period = fields.Char(
        'مدة الخدمة',
        compute='_compute_work_period'
    )
    sanction_no = fields.Integer(
        'عدد الإنذرات'
    )
    insurance_type = fields.Char(
        'فئة التأمين'
    )
    job_lvl = fields.Char(
        'الدرجة الوظيفية'
    )
    kafeel_name = fields.Char(
        'Kafeel Name',
    )

    def _compute_employee_age(self):
        for employee in self:
            if employee.birthday:
                employee.af_employee_age = employee._get_age_details(employee.birthday)
            else:
                employee.af_employee_age = False

    def _get_age_details(self, birthday):
        if birthday:
            birth_date = datetime.strptime(str(birthday), "%Y-%m-%d")
            today = datetime.strptime(str(fields.date.today()), "%Y-%m-%d")
            difference = relativedelta.relativedelta(today, birth_date)
            years = difference.years
            months = difference.months
            days = difference.days
            age_display = ''
            if years > 0:
                age_display = "{0} {1} ".format(years, _("Years") if years > 1 else _("Year"))
            if months > 0:
                age_display += ",{0} {1} ".format(months, _("Months") if months > 1 else _("Month"))
            if days > 0:
                age_display += ",{0} {1} ".format(days, _("Days") if days > 1 else _("Day"))
            return age_display

    def _compute_work_period(self):
        for employee in self:
            work_period = ''
            if employee.contract_id.date_start:
                date_start = datetime.strptime(str(employee.contract_id.date_start), "%Y-%m-%d")
                today = datetime.strptime(str(fields.date.today()), "%Y-%m-%d")
                difference = relativedelta.relativedelta(today, date_start)
                years = difference.years
                months = difference.months
                days = difference.days
                if years > 0:
                    work_period = "{0} {1} ".format(years, _("Years") if years > 1 else _("Year"))
                if months > 0:
                    work_period += ",{0} {1} ".format(months, _("Months") if months > 1 else _("Month"))
                if days > 0:
                    work_period += ",{0} {1} ".format(days, _("Days") if days > 1 else _("Day"))
            employee.af_work_period = work_period


class HrEmployeeContract(models.Model):
    _inherit = 'hr.contract'

    af_chip_gasoline = fields.Char(
        ' شريحة البنزين'
    )
    af_chip_mobile = fields.Char(
        ' شريحة الجوال'
    )
    af_allowance_call_fee = fields.Float(
        'بدل الاتصال'
    )
    af_allowance_housing = fields.Float(
        'بدل السكن'
    )
    af_allowance_transport = fields.Float(
        'بدل النقل'
    )
    af_allowance_other = fields.Float(
        'بدلات اخرى'
    )


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    af_job_id = fields.Many2one(
        'hr.job',
        string='المهنة ',
        tracking=True
    )
    sanction_no = fields.Integer(
        'عدد الإنذرات'
    )
    insurance_type = fields.Char(
        'فئة التأمين'
    )
    job_lvl = fields.Char(
        'الدرجة الوظيفية'
    )
    kafeel_name = fields.Char(
        'Kafeel Name',
    )
