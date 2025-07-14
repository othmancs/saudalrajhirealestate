# -*- coding: utf-8 -*-

import math
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

units = [('day', 'Days'),
         ('week', 'Weeks'),
         ('month', 'Months'),
         ('year', 'Years')]

PERIOD_RATIO = {
    'hour': 1,
    'day': 24,
    'week': 24 * 7
}


class RentRentalPricing(models.Model):
    _name = 'rental.pricing'
    _description = 'Rental Pricing'
    unit = fields.Selection(units, string='Unit', required='true')

    def _compute_price(self, duration, unit):
        """Compute the price for a specified duration of the current pricing rule.

        :param float duration: duration in hours
        :param str unit: duration unit (hour, day, week)
        :return float: price
        """
        self.ensure_one()
        if duration <= 0 or self.duration <= 0:
            return self.price
        if unit != self.unit:
            if unit == 'month' or self.unit == 'month':
                raise ValidationError(_("Conversion between Months and another duration unit are not supported!"))
            converted_duration = math.ceil((duration * PERIOD_RATIO[unit]) / (self.duration * PERIOD_RATIO[self.unit]))
        else:
            converted_duration = math.ceil(duration / self.duration)
        return self.price * converted_duration

    def _compute_duration_vals(self, pickup_date, return_date):
        duration = return_date - pickup_date
        vals = dict(hour=(duration.days * 24 + duration.seconds / 3600))
        vals['day'] = math.ceil(vals['hour'] / 24)
        vals['week'] = math.ceil(vals['day'] / 7)
        duration_diff = relativedelta(return_date, pickup_date)
        months = 1 if duration_diff.days or duration_diff.hours or duration_diff.minutes else 0
        months += duration_diff.months
        months += duration_diff.years * 12
        vals['month'] = months
        years = 1 if duration_diff.months or duration_diff.days or duration_diff.hours or duration_diff.minutes else 0
        years += duration_diff.years
        vals['year'] = years
        return vals
