# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import base64
from odoo import SUPERUSER_ID


class AttendanceLog(models.Model):
    _name = "attendance.log"
    _description = "attendance log"
    _order = "punching_time desc"
    _rec_name = "punching_time"

    # status = fields.Selection([('0', 'Check In'),
    #                            ('1', 'Check Out'),
    #                            ('2', 'Punched')], string='Status')
    status = fields.Selection(
        [
            ("0", "Check In"),
            ("1", "Check Out"),
            ("2", "Break Out"),
            ("3", "Break In"),
            ("4", "Overtime In"),
            ("5", "Overtime Out"),
            ("255", "Duplicate"),
        ],
        string="Punching Type",
        help="Punching type of the attendance",
    )
    punching_time = fields.Datetime("Punching Time")
    device = fields.Char("Device")
    employee_id = fields.Many2one("hr.employee", string="Employee", store=True)
    employee_name = fields.Char(
        "Employee Name",
    )
    status_number = fields.Char("Status Number")
    number = fields.Char("Number")
    timestamp = fields.Char("Timestamp")
    status_string = fields.Char("Status String")
    is_synced = fields.Boolean("Synced")
    # is_calculated = fields.Boolean('Calculated', default=False)
    # company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.company)

    # def unlink(self):
    #     if any(self.filtered(lambda log: log.is_calculated == True)):
    #         raise UserError(('You cannot delete a Record which is already Calculated !!!'))
    #     return super(AttendanceLog, self).unlink()

    def action_calculate_attendance(self):
        self.create_attendance()


    def create_attendance(self):
        attendance_logs = self.search(
            [("is_synced", "!=", True)], order="punching_time asc"
        )

        grouped_attendance = defaultdict(lambda: defaultdict(list))
        for log in attendance_logs:
            if log.employee_id and log.punching_time:
                date_key = log.punching_time.date()
                grouped_attendance[log.employee_id.id][date_key].append(log)

        for employee_id, dates in grouped_attendance.items():
            employee = self.env["hr.employee"].with_user(SUPERUSER_ID).browse(employee_id)
            employee_company = employee.company_id

            # Use company context with admin rights (safe, controlled)
            hr_attendance_model = self.env["hr.attendance"].with_company(employee_company).with_user(SUPERUSER_ID)

            for date, logs in dates.items():
                check_in = None
                check_out = None

                for log in logs:
                    if log.status == "0":  # Check In
                        check_in = min(check_in, log.punching_time) if check_in else log.punching_time
                    elif log.status == "1":  # Check Out
                        check_out = max(check_out, log.punching_time) if check_out else log.punching_time

                if check_in and check_out and check_in < check_out:
                    # Look for open attendance (in company context)
                    open_attendance = hr_attendance_model.search([
                        ("employee_id", "=", employee_id),
                        ("check_out", "=", False)
                    ], limit=1)

                    if open_attendance:
                        open_attendance.write({"check_out": check_out})
                    else:
                        overlapping = hr_attendance_model.search([
                            ("employee_id", "=", employee_id),
                            ("check_in", "<", check_out),
                            ("check_out", ">", check_in)
                        ], limit=1)

                        if not overlapping:
                            hr_attendance_model.create({
                                "employee_id": employee_id,
                                "check_in": check_in,
                                "check_out": check_out,
                            })

            # Update log sync flags (your model likely doesn't need elevated rights here)
            logs_to_sync = self.env["attendance.log"].search([
                ("employee_id", "=", employee_id),
                ("punching_time", ">=", datetime.combine(date, datetime.min.time())),
                ("punching_time", "<=", datetime.combine(date, datetime.max.time())),
            ])
            logs_to_sync.write({"is_synced": True})


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    sigma_bio_id = fields.Integer("Sigma Bio ID")

    def _get_attendance_report(self):
        current_time = fields.Datetime.now()
        previous_time = current_time - relativedelta(days=7)
        for rec in self:
            attendance_data = self.env["hr.attendance"].search(
                [
                    ("employee_id", "=", rec.id),
                    ("check_out", "<=", current_time),
                    ("check_out", ">=", previous_time),
                ]
            )
            return attendance_data

    @api.model
    def check_checkout_and_notify_manager(self):
        now = fields.Datetime.now()

        # Get all employees with today's attendance and checked out
        attendances = self.env["hr.attendance"].search(
            [("check_in", ">=", now.date()), ("check_out", "!=", False)]
        )

        for attendance in attendances:
            employee = attendance.employee_id
            calendar = employee.resource_calendar_id
            if not calendar:
                continue  # Skip if no working schedule

            # Determine working intervals for today
            tz = employee.tz or "UTC"
            local_now = fields.Datetime.context_timestamp(self, now).astimezone()
            weekday = local_now.weekday()  # Monday=0
            work_intervals = calendar._work_intervals_batch(
                fields.Datetime.to_datetime(now.date()),
                fields.Datetime.to_datetime(now.date() + timedelta(days=1)),
                resource=employee.resource_id,
            ).get(employee.resource_id.id)

            # Skip if no working hours today
            if not work_intervals:
                continue

            # Check if now is within any work interval
            in_working_hours = any(
                interval[0] <= now <= interval[1] for interval in work_intervals
            )
            if not in_working_hours:
                continue

            # Check if checkout was more than 30 mins ago
            if (now - attendance.check_out) > timedelta(minutes=30):
                manager = employee.parent_id
                if manager and manager.work_email:
                    self.env["mail.mail"].create(
                        {
                            "subject": f"Employee {employee.name} checked out early",
                            "body_html": f"""
                            <p>Employee <strong>{employee.name}</strong> checked out at {attendance.check_out.strftime("%H:%M")} and it's still within their scheduled working hours.</p>
                            <p>It has been more than 30 minutes since checkout.</p>
                        """,
                            "email_to": manager.work_email,
                        }
                    ).send()

    def send_overtime_email_with_report(self):
        employees = self.search([])
        for employee in employees:
            manager = employee.parent_id  # Employee's manager
            if not employee.work_email:
                continue  # Skip if the employee has no email

            # Generate the report (Change the report name and model as per your case)
            report_template = self.env.ref(
                "dp_biostar_2_biomatric_attendance.action_attendance_report"
            )  # Replace with your report ID
            pdf_content, content_type = report_template._render_qweb_pdf([employee.id])

            # Encode PDF in base64
            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"Attendance_Report_{employee.name}.pdf",
                    "type": "binary",
                    "datas": base64.b64encode(pdf_content),
                    "res_model": "hr.employee",
                    "res_id": employee.id,
                    "mimetype": "application/pdf",
                }
            )

            # Email values
            email_values = {
                "subject": "Attendance Notification",
                "body_html": f"""
                    <p>Dear {employee.name},</p>
                    <p>Please find your Attendance report attached.</p>
                    <p>Regards,<br/>HR Team</p>
                """,
                "email_to": employee.work_email,
                "email_cc": manager.work_email
                if manager and manager.work_email
                else "",
                "attachment_ids": [(4, attachment.id)],  # Attach the generated report
            }

            mail = self.env["mail.mail"].create(email_values)
            mail.send()


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    sigma_schedule_id = fields.Integer("Sigma Schedule Id")


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    punch_date = fields.Date(string="Punch Date")
    overtime_hours = fields.Char(
        string="Overtime Hours", compute="_compute_overtime_shortfall"
    )
    shortfall_hours = fields.Char(
        string="Shortfall Hours", compute="_compute_overtime_shortfall"
    )
    classification = fields.Selection(
        [("overtime", "Overtime"), ("shortfall", "Shortfall"), ("normal", "Normal")],
        string="Attendance Classification",
        compute="_compute_overtime_shortfall",
    )

    @api.depends("worked_hours", "check_in")
    def _compute_overtime_shortfall(self):
        base_hours = 8  # Standard working hours per day

        for record in self:
            if not record.worked_hours or not record.check_in:
                record.overtime_hours = "00:00"
                record.shortfall_hours = "00:00"
                record.classification = "normal"
                continue

            # Convert worked hours into timedelta
            input_timedelta = timedelta(hours=record.worked_hours)
            base_time = timedelta(hours=base_hours)
            adjusted_timedelta = input_timedelta - base_time

            check_in_date = record.check_in
            is_friday = check_in_date.weekday() == 4  # 4 corresponds to Friday

            if is_friday:
                record.overtime_hours = f"{int(record.worked_hours):02}:00"
                record.shortfall_hours = "00:00"
                record.classification = "overtime"
                continue

            if adjusted_timedelta > timedelta(0):
                hours, remainder = divmod(adjusted_timedelta.seconds, 3600)
                minutes = remainder // 60
                record.overtime_hours = f"{hours:02}:{minutes:02}"
                record.shortfall_hours = "00:00"
                record.classification = "overtime"
            else:
                hours, remainder = divmod(abs(adjusted_timedelta).seconds, 3600)
                minutes = remainder // 60
                record.overtime_hours = "00:00"
                record.shortfall_hours = f"{hours:02}:{minutes:02}"
                record.classification = "shortfall"

    def compute_in_out_difference(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                check_in = datetime.strptime(
                    str(attendance.check_in), "%Y-%m-%d %H:%M:%S"
                )
                check_out = datetime.strptime(
                    str(attendance.check_out), "%Y-%m-%d %H:%M:%S"
                )
                diff1 = check_out - check_in
                total_seconds = diff1.seconds
                diff2 = total_seconds / 3600.0
                attendance.in_out_diff = diff2
            else:
                attendance.in_out_diff = 0

    in_out_diff = fields.Float("Difference", compute="compute_in_out_difference")

    def unlink(self):
        for record in self:
            domain = [
                ("employee_id", "=", record.employee_id.id),
                "|",
                ("punching_time", "=", record.check_in),
                ("punching_time", "=", record.check_out),
            ]
            attend_obj = self.env["attendance.log"].search(domain)
        # for log in attend_obj:
        #     log.is_calculated = False
        return super(HrAttendance, self).unlink()

    def get_attendance_summary(self):
        """Fetch attendance data for the last 7 days and generate a PDF report."""
        current_time = fields.Datetime.now()
        previous_time = current_time - relativedelta(days=7)

        attendance_data = self.search(
            [
                ("check_out", "<=", current_time),
                ("check_out", ">=", previous_time),
            ]
        )

        grouped_by_employee = defaultdict(list)
        for record in attendance_data:
            grouped_by_employee[record.employee_id].append(record)

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
