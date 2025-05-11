# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
import base64
import os
import pytz
import math
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone, UTC
import io
from odoo.tools.misc import xlsxwriter
from collections import defaultdict


class AttendanceReportWizard(models.TransientModel):
    _name = "attendance.report.wizard"
    _description = "attendance report wizard"

    report_from = fields.Selection(
        [("attend", "From Attendance"), ("log", "From Log")],
        string="Report",
        required=True,
        default="attend",
    )
    date_from = fields.Datetime("From", required=True, default=datetime.today())
    date_to = fields.Datetime("To", required=True, default=datetime.today())
    report_file = fields.Binary("File", readonly=True)
    report_name = fields.Text(string="File Name")
    is_printed = fields.Boolean("Printed", default=False)
    employee_ids = fields.Many2many("hr.employee", string="Employee")
    add_time = fields.Boolean("Add Time", default=False)

    html_preview = fields.Html(
        string="Preview", readonly=True, help="Preview of the report data"
    )

    # New fields
    date_from_d = fields.Date("From")
    date_to_d = fields.Date("To")

    @api.onchange("date_from_d")
    def _onchange_date_from_d(self):
        if not self.add_time and self.date_from_d:
            self.date_from = f"{self.date_from_d} 00:00:00"
        elif self.add_time and self.date_from_d:
            pass

    @api.onchange("date_to_d")
    def _onchange_date_to_d(self):
        if not self.add_time and self.date_to_d:
            self.date_to = f"{self.date_to_d} 23:59:59"
        elif self.add_time and self.date_to_d:
            pass

    # @api.onchange('report_from')
    # def onchange_report(self):
    #     day = datetime.today().day
    #     date_from = datetime.today() + relativedelta(day=day - 1, hour=00, minute=00, second=00)
    #     date_to = datetime.today() + relativedelta(day=day - 1, hour=23, minute=59, second=59)
    #     self.date_from = date_from.strftime("%Y-%m-%d %H:%M:%S")
    #     self.date_to = date_to.strftime("%Y-%m-%d %H:%M:%S")

    def export_attendance_xlsx(self, fl=None):
        date_from = self.new_timezone(self.date_from)
        date_to = self.new_timezone(self.date_to)
        # domain = [('check_in', '>=', date_from), ('check_out', '<=', date_to)]

        if self.employee_ids:
            domain = [
                ("check_in", ">=", date_from),
                ("check_out", "<=", date_to),
                ("employee_id", "in", self.employee_ids.ids),
            ]
        else:
            employees = self.env["hr.employee"].sudo().search([])
            domain = [
                ("check_in", ">=", date_from),
                ("check_out", "<=", date_to),
                ("employee_id", "in", employees.ids),
            ]

        attendances = self.env["hr.attendance"].sudo().search(domain)
        # Group records by employee_id
        grouped_by_employee = defaultdict(list)
        for record in attendances:
            grouped_by_employee[record.employee_id].append(record)

        fl = self.print_attendance_records(grouped_by_employee)

        output = base64.encodebytes(fl[1])
        context = self.env.args
        ctx = dict(context[2])
        ctx.update({"report_file": output})
        ctx.update({"file": fl[0]})
        self.report_name = fl[0]
        self.report_file = ctx["report_file"]
        self.is_printed = True

        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "attendance.report.wizard",
            "target": "new",
            "context": ctx,
            "res_id": self.id,
        }

    def action_back(self):
        if self._context is None:
            self._context = {}
        self.is_printed = False
        result = {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "attendance.report.wizard",
            "target": "new",
        }
        return result

    def print_attendance_records(self, attendances):
        str_date1 = str(self.date_from)
        str_date1 = self.new_timezone(self.date_from)

        date1 = datetime.strptime(str_date1, "%Y-%m-%d %H:%M:%S").date()
        day1 = date1.strftime("%d")
        month1 = date1.strftime("%B")
        year1 = date1.strftime("%Y")
        str_date2 = str(self.date_to)
        str_date2 = self.new_timezone(self.date_to)
        date2 = datetime.strptime(str_date2, "%Y-%m-%d %H:%M:%S").date()
        day2 = date2.strftime("%d")
        month2 = date2.strftime("%B")
        year2 = date2.strftime("%Y")
        fl = (
            "Attendance from "
            + day1
            + "-"
            + month1
            + "-"
            + year1
            + " to "
            + day2
            + "-"
            + month2
            + "-"
            + year2
            + "("
            + str(datetime.today())
            + ")"
            + ".xlsx"
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        for employee, records in attendances.items():
            # for attendance in records:
            worksheet = workbook.add_worksheet(f"{employee.name}")
            worksheet.set_landscape()

            bold = workbook.add_format({"bold": True, "border": 1, "align": "center"})
            font_left = workbook.add_format(
                {"align": "left", "border": 1, "font_size": 12}
            )
            font_center = workbook.add_format(
                {"align": "center", "border": 1, "valign": "vcenter", "font_size": 12}
            )
            font_bold_center = workbook.add_format(
                {
                    "align": "center",
                    "border": 1,
                    "valign": "vcenter",
                    "font_size": 12,
                    "bold": True,
                }
            )
            border = workbook.add_format({"border": 1})

            # worksheet.set_column('O:XFD', None, None, {'hidden': True})
            worksheet.set_column("A:O", 20, border)
            worksheet.set_row(0, 20)
            worksheet.merge_range(
                "A1:L1",
                "Attendance sheet from"
                + day1
                + "-"
                + month1
                + "-"
                + year1
                + " to "
                + day2
                + "-"
                + month2
                + "-"
                + year2,
                bold,
            )

            row = 2
            col = 0
            worksheet.merge_range(
                row, col, row + 1, col + 1, "Name of Employee", font_bold_center
            )
            worksheet.merge_range(
                row, col + 2, row + 1, col + 2, "Check In Date", font_bold_center
            )
            worksheet.merge_range(
                row, col + 3, row + 1, col + 3, "Check In Time", font_bold_center
            )
            worksheet.merge_range(
                row, col + 4, row + 1, col + 4, "Check Out Date", font_bold_center
            )
            worksheet.merge_range(
                row, col + 5, row + 1, col + 5, "Check Out Time", font_bold_center
            )
            worksheet.merge_range(
                row, col + 6, row + 1, col + 6, "Difference", font_bold_center
            )
            worksheet.merge_range(
                row, col + 7, row + 1, col + 7, "Break Time", font_bold_center
            )
            worksheet.merge_range(
                row, col + 8, row + 1, col + 8, "Worked Hours", font_bold_center
            )
            worksheet.merge_range(
                row, col + 9, row + 1, col + 9, "Shift Hours", font_bold_center
            )
            worksheet.merge_range(
                row, col + 10, row + 1, col + 10, "Overtime Hours", font_bold_center
            )
            worksheet.merge_range(
                row, col + 11, row + 1, col + 11, "Shortfall Hours", font_bold_center
            )
            row += 2
            total_overtime = "00:00"
            for attendance in records:
                worksheet.merge_range(
                    row, col, row, col + 1, attendance.employee_id.name, font_left
                )
                if attendance.check_in:
                    check_in = self.new_timezone(attendance.check_in)
                    if isinstance(check_in, str):
                        check_in_dt = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S")
                    check_in_date = check_in_dt.strftime("%Y-%m-%d")
                    check_in_time = check_in_dt.strftime("%H:%M:%S")
                else:
                    check_in = "***No Check In***"
                    check_in_date = "***No Check In***"
                    check_in_time = "***No Check In***"
                worksheet.write(row, col + 2, check_in_date, font_center)
                worksheet.write(row, col + 3, check_in_time, font_center)
                if attendance.check_out:
                    check_out = self.new_timezone(attendance.check_out)
                    if isinstance(check_out, str):
                        check_out_dt = datetime.strptime(check_out, "%Y-%m-%d %H:%M:%S")
                    check_out_date = check_out_dt.strftime("%Y-%m-%d")
                    check_out_time = check_out_dt.strftime("%H:%M:%S")
                else:
                    check_out = "***No Check Out***"
                    check_out_date = "***No Check Out***"
                    check_out_time = "***No Check Out***"

                worksheet.write(row, col + 4, check_out_date, font_center)
                worksheet.write(row, col + 5, check_out_time, font_center)

                diff_hours = int(attendance.in_out_diff)
                diff_minutes = int((attendance.in_out_diff - diff_hours) * 60)
                diff = f"{diff_hours:02}:{diff_minutes:02}"
                worksheet.write(row, col + 6, diff, font_center)

                wrk_hours = int(attendance.worked_hours)
                wrk_minutes = int((attendance.worked_hours - wrk_hours) * 60)
                worked = f"{wrk_hours:02}:{wrk_minutes:02}"
                worksheet.write(row, col + 8, worked, font_center)

                break_time = datetime.strptime(diff, "%H:%M") - datetime.strptime(
                    worked, "%H:%M"
                )
                hours, remainder = divmod(break_time.seconds, 3600)
                minutes = remainder // 60
                formatted_break_time = f"{hours:02}:{minutes:02}"

                worksheet.write(row, col + 7, formatted_break_time, font_center)

                # Determine if the current day is Friday
                check_in_date = (
                    datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S")
                    if attendance.check_in
                    else None
                )
                is_friday = (
                    check_in_date and check_in_date.weekday() == 4
                )  # 4 corresponds to Friday

                # Write the shift hours based on whether it is Friday
                # if is_friday:
                #     worksheet.write(row, col + 7, "00:00", font_center)
                # else:
                worksheet.write(row, col + 9, "08:00", font_center)

                def calculate_time(input_time, check_in, base_hours=8):
                    cumulative_overtime = timedelta(0)
                    cumulative_shortfall = timedelta(0)

                    # Convert input_time to timedelta
                    hours, minutes = map(int, input_time.split(":"))
                    input_timedelta = timedelta(hours=hours, minutes=minutes)
                    base_time = timedelta(hours=base_hours)

                    # Convert check_in to a datetime object to determine the day of the week
                    check_in_date = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S")
                    is_friday = check_in_date.weekday() == 4  # 4 corresponds to Friday
                    # Calculate adjusted time

                    adjusted_timedelta = input_timedelta - base_time
                    if is_friday:
                        cumulative_overtime = input_time
                        classification = "Overtime"
                        return cumulative_overtime, classification

                    else:
                        # Update cumulative counters and classify
                        if adjusted_timedelta > timedelta(0) or is_friday:
                            cumulative_overtime += adjusted_timedelta
                            classification = "Overtime"
                        else:
                            cumulative_shortfall -= adjusted_timedelta  # Subtract because adjusted_timedelta is negative
                            classification = "Shortfall"

                        # Format the adjusted time for display
                        hours, remainder = divmod(abs(adjusted_timedelta).seconds, 3600)
                        minutes = remainder // 60
                        formatted_adjusted_time = f"{hours:02}:{minutes:02}"

                        return formatted_adjusted_time, classification

                # Function to format cumulative time for display
                def format_cumulative_time(timedelta_obj):
                    hours, remainder = divmod(timedelta_obj.seconds, 3600)
                    minutes = remainder // 60
                    return f"{hours:02}:{minutes:02}"

                # Example usage:
                adjusted_time, classification = calculate_time(
                    worked, check_in
                )  # Friday
                worksheet.write(
                    row,
                    col + 10,
                    adjusted_time if classification == "Overtime" else "00:00",
                    font_center,
                )
                hours1, minutes1 = map(int, total_overtime.split(":"))
                hours2, minutes2 = map(
                    int,
                    adjusted_time.split(":")
                    if classification == "Overtime"
                    else "00:00".split(":"),
                )

                time1_delta = timedelta(hours=hours1, minutes=minutes1)
                time2_delta = timedelta(hours=hours2, minutes=minutes2)
                # Add the two timedelta objects
                total_time = time1_delta + time2_delta

                # Convert back to "HH:MM" format
                total_hours, remainder = divmod(total_time.seconds, 3600)
                total_minutes = remainder // 60
                total_overtime = (
                    f"{total_time.days * 24 + total_hours:02}:{total_minutes:02}"
                )
                worksheet.write(
                    row,
                    col + 11,
                    adjusted_time if classification == "Shortfall" else "00:00",
                    font_center,
                )

                row += 1
            worksheet.write(row, 10, f"Total: {total_overtime}", font_center)
        workbook.close()
        xlsx_data = output.getvalue()

        return [fl, xlsx_data]

    def new_timezone(self, time):
        user_tz = self.env.user.tz or str(pytz.utc)
        local = pytz.timezone(user_tz)
        display_date_result = datetime.strftime(
            pytz.utc.localize(time, is_dst=0).astimezone(local), "%Y-%m-%d %H:%M:%S"
        )
        return display_date_result

    def to_naive_user_tz(self, datetime):
        tz_name = self.env.user.tz
        tz = tz_name and pytz.timezone(tz_name) or pytz.UTC
        x = (
            pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False)
            .astimezone(tz)
            .replace(tzinfo=None)
        )
        return x

    def to_naive_utc(self, datetime):
        tz_name = self.env.user.tz
        tz = tz_name and pytz.timezone(tz_name) or pytz.UTC
        y = (
            tz.localize(datetime.replace(tzinfo=None), is_dst=False)
            .astimezone(pytz.UTC)
            .replace(tzinfo=None)
        )
        return y

    def to_tz(self, datetime):
        tz_name = self.env.user.tz
        tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
        return (
            pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False)
            .astimezone(tz)
            .replace(tzinfo=None)
        )

    def convert_timezone(self, time):
        atten_time = datetime.strptime(str(time), "%Y-%m-%d %H:%M:%S")
        atten_time = datetime.strptime(
            atten_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
        )
        local_tz = pytz.timezone(self.env.user.tz or "GMT")
        local_dt = local_tz.localize(atten_time, is_dst=0)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
        atten_time = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
        atten_time = fields.Datetime.to_string(atten_time)
        return atten_time

    def print_attendance_logs(self, logs):
        str_date1 = str(self.date_from)
        date1 = datetime.strptime(str(str_date1), "%Y-%m-%d %H:%M:%S").date()
        day1 = date1.strftime("%d")
        month1 = date1.strftime("%B")
        year1 = date1.strftime("%Y")
        str_date2 = str(self.date_to)
        date2 = datetime.strptime(str(str_date2), "%Y-%m-%d %H:%M:%S").date()
        day2 = date2.strftime("%d")
        month2 = date2.strftime("%B")
        year2 = date2.strftime("%Y")
        fl = (
            "Attendance Log from "
            + day1
            + "-"
            + month1
            + "-"
            + year1
            + " to "
            + day2
            + "-"
            + month2
            + "-"
            + year2
            + "("
            + str(datetime.today())
            + ")"
            + ".xlsx"
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Sheet 1")
        worksheet.set_landscape()
        bold = workbook.add_format({"bold": True, "border": 1, "align": "center"})
        font_left = workbook.add_format({"align": "left", "border": 1, "font_size": 12})
        font_center = workbook.add_format(
            {"align": "center", "border": 1, "valign": "vcenter", "font_size": 12}
        )
        font_bold_center = workbook.add_format(
            {
                "align": "center",
                "border": 1,
                "valign": "vcenter",
                "font_size": 12,
                "bold": True,
            }
        )
        border = workbook.add_format({"border": 1})

        worksheet.set_column("E:XFD", None, None, {"hidden": True})
        worksheet.set_column("A:E", 20, border)
        worksheet.set_row(0, 20)
        worksheet.merge_range(
            "A1:E1",
            "Attendance Log from "
            + day1
            + "-"
            + month1
            + "-"
            + year1
            + " to "
            + day2
            + "-"
            + month2
            + "-"
            + year2,
            bold,
        )

        row = 2
        col = 0
        worksheet.merge_range(
            row, col, row + 1, col + 1, "Name of Employee", font_bold_center
        )
        worksheet.merge_range(
            row, col + 2, row + 1, col + 2, "Punching Time", font_bold_center
        )
        worksheet.merge_range(
            row, col + 3, row + 1, col + 3, "Status", font_bold_center
        )
        worksheet.merge_range(
            row, col + 4, row + 1, col + 4, "Device", font_bold_center
        )

        row += 2
        for log in logs:
            worksheet.merge_range(
                row, col, row, col + 1, log.employee_id.name, font_left
            )
            if log.punching_time:
                punching_time = self.new_timezone(log.punching_time)

            else:
                punching_time = "***No Status***"
            worksheet.write(row, col + 2, punching_time, font_center)
            if log.status == "0":
                status = "Check In"
            elif log.status == "1":
                status = "Check Out"
            else:
                status = "punched"
            worksheet.write(row, col + 3, status, font_center)
            worksheet.write(row, col + 4, log.device, font_center)
            row += 1

        workbook.close()
        xlsx_data = output.getvalue()

        return [fl, xlsx_data]

    def action_preview_attendance_report(self):
        """Generate and show a preview of the attendance report with all calculations."""

        date_from = self.new_timezone(self.date_from)
        date_to = self.new_timezone(self.date_to)

        if self.employee_ids:
            domain = [
                ("check_in", ">=", date_from),
                ("check_out", "<=", date_to),
                ("employee_id", "in", self.employee_ids.ids),
            ]
        else:
            employees = self.env["hr.employee"].sudo().search([])
            domain = [
                ("check_in", ">=", date_from),
                ("check_out", "<=", date_to),
                ("employee_id", "in", employees.ids),
            ]

        attendances = self.env["hr.attendance"].sudo().search(domain)

        # Group records by employee_id
        grouped_by_employee = defaultdict(list)
        for record in attendances:
            grouped_by_employee[record.employee_id].append(record)

        # Format the report date range
        str_date1 = self.new_timezone(self.date_from)
        date1 = datetime.strptime(str_date1, "%Y-%m-%d %H:%M:%S").date()
        day1, month1, year1 = (
            date1.strftime("%d"),
            date1.strftime("%B"),
            date1.strftime("%Y"),
        )

        str_date2 = self.new_timezone(self.date_to)
        date2 = datetime.strptime(str_date2, "%Y-%m-%d %H:%M:%S").date()
        day2, month2, year2 = (
            date2.strftime("%d"),
            date2.strftime("%B"),
            date2.strftime("%Y"),
        )

        # Start building the HTML preview
        preview_content = f"""
        <div style='font-size:18px; font-weight:bold;'>
            <span>Attendance Report from {day1}-{month1}-{year1} to {day2}-{month2}-{year2}</span>
        </div>
        <br/>
        <div style='font-size:22px; font-weight:bold; text-align:center;'>Employee Attendance Report</div>
        <br/>
        """

        if attendances:
            preview_content += """
            <table border='1' style='width:100%; border-collapse:collapse; font-size:14px;'>
                <thead>
                    <tr style='background-color:#38761d; color:white; text-align:center;'>
                        <th style='border: 1px solid #000; padding:5px;'>Employee</th>
                        <th style='border: 1px solid #000; padding:5px;'>Check In Date</th>
                        <th style='border: 1px solid #000; padding:5px;'>Check In Time</th>
                        <th style='border: 1px solid #000; padding:5px;'>Check Out Date</th>
                        <th style='border: 1px solid #000; padding:5px;'>Check Out Time</th>
                        <th style='border: 1px solid #000; padding:5px;'>Difference</th>
                        <th style='border: 1px solid #000; padding:5px;'>Break Time</th>
                        <th style='border: 1px solid #000; padding:5px;'>Worked Hours</th>
                        <th style='border: 1px solid #000; padding:5px;'>Shift Hours</th>
                        <th style='border: 1px solid #000; padding:5px;'>Overtime</th>
                        <th style='border: 1px solid #000; padding:5px;'>Shortfall</th>
                    </tr>
                </thead>
                <tbody>
            """

            for employee, records in grouped_by_employee.items():
                for attendance in records:
                    check_in = (
                        self.new_timezone(attendance.check_in)
                        if attendance.check_in
                        else "No Check In"
                    )
                    check_out = (
                        self.new_timezone(attendance.check_out)
                        if attendance.check_out
                        else "No Check Out"
                    )

                    check_in_dt = (
                        datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S")
                        if attendance.check_in
                        else None
                    )
                    check_out_dt = (
                        datetime.strptime(check_out, "%Y-%m-%d %H:%M:%S")
                        if attendance.check_out
                        else None
                    )

                    check_in_date = (
                        check_in_dt.strftime("%Y-%m-%d") if check_in_dt else "N/A"
                    )
                    check_in_time = (
                        check_in_dt.strftime("%H:%M:%S") if check_in_dt else "N/A"
                    )
                    check_out_date = (
                        check_out_dt.strftime("%Y-%m-%d") if check_out_dt else "N/A"
                    )
                    check_out_time = (
                        check_out_dt.strftime("%H:%M:%S") if check_out_dt else "N/A"
                    )

                    # Calculate difference
                    difference = attendance.in_out_diff
                    diff_hours = int(difference)
                    diff_minutes = int((difference - diff_hours) * 60)
                    formatted_difference = f"{diff_hours:02}:{diff_minutes:02}"

                    # Calculate worked hours
                    worked_hours = formatted_difference

                    # Calculate break time
                    diff_hours = int(attendance.in_out_diff)
                    diff_minutes = int((attendance.in_out_diff - diff_hours) * 60)
                    diff = f"{diff_hours:02}:{diff_minutes:02}"
                    wrk_hours = int(attendance.worked_hours)
                    wrk_minutes = int((attendance.worked_hours - wrk_hours) * 60)
                    worked = f"{wrk_hours:02}:{wrk_minutes:02}"
                    break_time = datetime.strptime(diff, "%H:%M") - datetime.strptime(
                        worked, "%H:%M"
                    )
                    hours, remainder = divmod(break_time.seconds, 3600)
                    minutes = remainder // 60
                    formatted_break_time = f"{hours:02}:{minutes:02}"

                    # Determine shift hours (default 8 hours)
                    shift_hours = "08:00"

                    # Calculate overtime and shortfall
                    adjusted_time, classification = self.calculate_time_p(
                        worked_hours, check_in
                    )

                    preview_content += f"""
                    <tr style='text-align:center;'>
                        <td style='border: 1px solid #000;'>{attendance.employee_id.name}</td>
                        <td style='border: 1px solid #000;'>{check_in_date}</td>
                        <td style='border: 1px solid #000;'>{check_in_time}</td>
                        <td style='border: 1px solid #000;'>{check_out_date}</td>
                        <td style='border: 1px solid #000;'>{check_out_time}</td>
                        <td style='border: 1px solid #000;'>{formatted_difference}</td>
                        <td style='border: 1px solid #000;'>{formatted_break_time}</td>
                        <td style='border: 1px solid #000;'>{worked_hours}</td>
                        <td style='border: 1px solid #000;'>{shift_hours}</td>
                        <td style='border: 1px solid #000;'>{adjusted_time if classification == "Overtime" else "00:00"}</td>
                        <td style='border: 1px solid #000;'>{adjusted_time if classification == "Shortfall" else "00:00"}</td>
                    </tr>
                    """

            preview_content += "</tbody></table><br/><br/>"

        else:
            preview_content += "<p>No data found for the selected filters.</p>"

        # Assign the generated HTML content to preview
        self.html_preview = preview_content

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def calculate_time_p(self, worked_hours, check_in):
        """Calculate overtime and shortfall based on worked hours."""
        base_hours = 8
        cumulative_overtime = timedelta(0)
        cumulative_shortfall = timedelta(0)

        hours, minutes = map(int, worked_hours.split(":"))
        input_timedelta = timedelta(hours=hours, minutes=minutes)
        base_time = timedelta(hours=base_hours)

        check_in_date = (
            datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S") if check_in else None
        )
        is_friday = (
            check_in_date and check_in_date.weekday() == 4
        )  # 4 corresponds to Friday

        adjusted_timedelta = input_timedelta - base_time

        if is_friday:
            return worked_hours, "Overtime"

        if adjusted_timedelta > timedelta(0):
            cumulative_overtime += adjusted_timedelta
            classification = "Overtime"
        else:
            cumulative_shortfall -= adjusted_timedelta
            classification = "Shortfall"

        hours, remainder = divmod(abs(adjusted_timedelta).seconds, 3600)
        minutes = remainder // 60
        formatted_adjusted_time = f"{hours:02}:{minutes:02}"

        return formatted_adjusted_time, classification
