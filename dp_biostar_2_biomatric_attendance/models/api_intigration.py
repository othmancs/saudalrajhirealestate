import base64
from odoo import api, fields, models, _
from collections import defaultdict
from odoo.addons.base.models.res_partner import _tz_get
import pytz
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import re
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class BiostarApi(models.Model):
    _name = "biostar.api"
    _description = "Biostar 2 Api"


class BioStarDeviceSync(models.Model):
    _name = "biostar.device.sync"
    _description = "BioStar Device Synchronization"

    name = fields.Char(string="Name", required=True)
    ip = fields.Char(string="Device IP")
    port = fields.Integer(string="Port")
    device_id = fields.Char(string="Device Id", null=True, blank=True)
    serial_number = fields.Char("Serial Number")
    device_password = fields.Char(string="Device Password", null=True, blank=True)
    time_zone = fields.Selection(
        _tz_get, string="Timezone", default=lambda self: self.env.user.tz or "GMT"
    )
    state = fields.Selection(
        [("not_connected", "Not Connected"), ("connected", "Connected")],
        default="not_connected",
    )
    bs_session_id = fields.Text(string="bs session id")
    last_sync_time = fields.Datetime(
        string="Last Sync Time", help="Last time attendance data was synced"
    )

    def send_api_request(self, method, endpoint, payload=None, headers=None):
        url = f"https://{self.ip}:{self.port}/api{endpoint}"
        default_headers = {"Content-Type": "application/json; charset=utf-8"}
        if headers:
            default_headers.update(headers)
        try:
            response = requests.request(
                method, url, headers=default_headers, json=payload, verify=False
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise UserError(_("API Request failed: %s") % str(e))

    def authenticate(self):
        payload = {
            "User": {"login_id": self.device_id, "password": self.device_password}
        }
        response = self.send_api_request("POST", "/login", payload)

        bs_session_id = response.headers.get("bs-session-id")
        if not bs_session_id:
            raise UserError(
                _("Authentication successful but 'bs-session-id' is missing.")
            )

        self.write({"bs_session_id": bs_session_id, "state": "connected"})

    def fetch_and_store_data(
        self,
        endpoint,
        model_name,
        key_collection,
        mapping,
        convert_boolean=None,
        transform_func=None,
        payload=None,
        method=None,
    ):
        self.authenticate()
        response = self.send_api_request(
            method,
            endpoint,
            headers={"bs-session-id": self.bs_session_id},
            payload=payload,
        )
        body = response.json()
        # Check if the key_collection exists
        if key_collection not in body:
            raise UserError(
                _("Invalid response structure: missing '%s' key") % key_collection
            )

        records = (
            body[key_collection]["rows"] if not transform_func else body[key_collection]
        )
        # Ensure records is always a list
        if not isinstance(records, list):
            records = [records]
        primary_key = next(iter(mapping))  # Get the first key (should be id)

        primary_key_field = next(
            (field for field in mapping.keys() if field != "id"), None
        )
        for record in records:
            # Apply transformation if a transform function is provided
            record_data = {}
            for field, api_field in mapping.items():
                value = record.get(api_field)
                # Apply boolean conversion for relevant fields
                if field.startswith("is_"):
                    value = convert_boolean(value)
                record_data[field] = value
                if transform_func:
                    record_attend = transform_func(record)
                    record_data["attendance_ids"] = record_attend["attendance_ids"]

            if not record_data.get(primary_key):
                continue  # Skip if primary key is missing

            existing_record = self.env[model_name].search(
                [(primary_key_field, "=", record_data[primary_key])], limit=1
            )
            if existing_record:
                existing_record.write(record_data)
            else:
                record_data[primary_key_field] = record_data.pop(
                    primary_key
                )  # Ensure correct field is used
                self.env[model_name].create(record_data)

    def sync_device_types(self):
        mapping = {
            "device_type_id": "id",
            "name": "name",
            "is_keypad": "keypad",
            "is_fingerprint": "fingerprint",
            "is_card": "card",
            "is_face": "face",
            "is_volume": "volume",
            "is_wifi": "wifi",
        }

        def convert_boolean(value):
            """Convert API string values ('true'/'false') to Python booleans"""
            return value.lower() == "true" if isinstance(value, str) else bool(value)

        print("Field Mapping:", mapping)
        self.fetch_and_store_data(
            "/device_types",
            "biostar.device.type",
            "DeviceTypeCollection",
            mapping,
            convert_boolean,
            method="GET",
        )

    def sync_devices(self):
        mapping = {"device_id": "id", "name": "name"}
        self.fetch_and_store_data(
            "/devices", "biostar.device", "DeviceCollection", mapping, method="GET"
        )

    def sync_schedule(self):
        self.authenticate()
        response = self.send_api_request(
            "GET", "/schedules", headers={"bs-session-id": self.bs_session_id}
        )
        rows = response.json().get("ScheduleCollection", {}).get("rows", [])
        total_schedule_ids = []
        for row in rows:
            if "daily_schedules" in row:
                total_schedule_ids.append(int(row.get("id")))
        mapping = {
            "sigma_schedule_id": "id",
            "name": "name",
            # 'description': 'description',
            "attendance_ids": "daily_schedules",
        }

        def convert_boolean(value):
            """Convert API string values ('true'/'false') to Python booleans"""
            return value.lower() == "true" if isinstance(value, str) else bool(value)

        def transform_schedule_data(record):
            """Transform daily_schedules into attendance_ids for resource.calendar"""
            attendance_ids = []
            daily_schedules = record.get("daily_schedules", [])

            # Mapping of day_index to day names
            day_name_map = {
                "0": "Sunday",
                "1": "Monday",
                "2": "Tuesday",
                "3": "Wednesday",
                "4": "Thursday",
                "5": "Friday",
                "6": "Saturday",
            }

            for daily in daily_schedules:
                # Convert to string for consistent mapping
                day_index = str(daily.get("day_index"))
                time_segments = daily.get("time_segments", [])

                # Skip days without time segments (e.g., weekends or holidays)
                if not time_segments:
                    continue

                for segment in time_segments:
                    start_time = (
                        int(segment.get("start_time")) / 60
                    )  # Convert minutes to hours
                    end_time = int(segment.get("end_time")) / 60

                    # Morning Segment
                    # if start_time <= morning_start < end_time:  # Covers or starts in the morning period
                    attendance_ids.append(
                        (
                            0,
                            0,
                            {
                                "name": f"{day_name_map[day_index]}",
                                "dayofweek": day_index,
                                "hour_from": start_time,
                                "hour_to": end_time,
                                "day_period": "morning",
                            },
                        )
                    )

            # Update the record with the transformed attendance_ids
            record["attendance_ids"] = attendance_ids
            return record

        # Call the fetch_and_store_data method with transformation function
        self.fetch_and_store_data(
            endpoint="/schedules/2",
            model_name="resource.calendar",
            key_collection="Schedule",
            mapping=mapping,
            convert_boolean=convert_boolean,
            # Pass the transformation function here
            transform_func=transform_schedule_data,
            method="GET",
        )

    def sync_attendance(self):
        """Fetch and sync attendance records since last sync time"""
        # Get record limit from settings
        # record_limit = int(self.env['ir.config_parameter'].sudo().get_param('attendance.record.limit', default=300))
        record_limit = 300000

        # Get last sync time from model
        if not self.last_sync_time:
            last_sync_time = fields.Datetime.now() - timedelta(
                days=1
            )  # Default to 1 day ago
        else:
            last_sync_time = self.last_sync_time

        # Convert to API format
        last_sync_time_str = last_sync_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        current_time = fields.Datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")

        all_records = []
        offset = 0
        while True:
            payload = {
                "Query": {
                    "limit": record_limit,
                    "offset": offset,  # <-- ADD OFFSET HERE
                    "conditions": [
                        {
                            "column": "datetime",
                            "operator": 3,
                            "values": [last_sync_time_str, current_time],
                        }
                    ],
                    "orders": [{"column": "datetime", "descending": False}],
                }
            }
            headers = {
                "Content-Type": "application/json",
                "bs-session-id": self.bs_session_id,
            }
            response = self.send_api_request("POST", "/events/search", payload, headers)
            data = response.json()

            new_records = data.get("EventCollection", {}).get("rows", [])
            if not new_records:
                break

            all_records.extend(new_records)
            offset += len(new_records)

            if len(new_records) < record_limit:
                break

        # Process and save attendance records
        for record in all_records:
            user_id = record.get("user_id", {}).get("user_id")
            device_id_num = record.get("device_id", {}).get("id")
            punching_time_str = record.get("datetime")

            if not user_id or not device_id_num or not punching_time_str:
                continue

            # Convert datetime format
            try:
                punching_time_str = punching_time_str.split(".")[0]
                punching_time_str = punching_time_str.replace("T", " ")
                punching_time = datetime.strptime(
                    punching_time_str, "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                continue

            # Find Employee
            employee = self.env["hr.employee"].search(
                [("sigma_bio_id", "=", user_id)], limit=1
            )
            if not employee:
                continue

            # Find Biostar Device
            device = self.env["biostar.device"].search(
                [("device_id", "=", device_id_num)], limit=1
            )
            if not device:
                continue
            # Determine Punch Type
            status = "0" if device.device_type == "check_in" else "1"

            # Create Attendance Log
            self.env["attendance.log"].create(
                {
                    "employee_id": employee.id,
                    "device": device.name,
                    "punching_time": punching_time,
                    "status": status,
                    "number": user_id,
                    "timestamp": int(punching_time.timestamp()),
                    "status_string": "Check In" if status == "0" else "Check Out",
                }
            )

            # # Create / Update Attendance
            # if status == "0":  # Check-In
            #     self.env["hr.attendance"].create(
            #         {"employee_id": employee.id, "check_in": punching_time}
            #     )
            # else:  # Check-Out
            #     last_attendance = self.env["hr.attendance"].search(
            #         [("employee_id", "=", employee.id)], order="check_in desc", limit=1
            #     )

            #     # Only update check_out if last_attendance exists and does not have a checkout time
            #     if last_attendance and not last_attendance.check_out:
            #         last_attendance.write({"check_out": punching_time})

        # Update last synced time in the model
        self.last_sync_time = fields.Datetime.now()


class BiostarAttendanceLog(models.Model):
    _name = "biostar.attendance.log"
    _description = "Biostar Attendance Log"

    device_id_num = fields.Char(
        string="Biometric Device ID", help="The ID of the Biometric Device"
    )
    punch_type = fields.Selection(
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
    # attendance_type = fields.Selection(
    #     [
    #         ("1", "Finger"),
    #         ("15", "Face"),
    #         ("2", "Type_2"),
    #         ("3", "Password"),
    #         ("4", "Card"),
    #         ("255", "Duplicate"),
    #     ],
    #     string="Category",
    #     help="Attendance detecting methods",
    # )
    punching_time = fields.Datetime(
        string="Punching Time", help="Punching time in the device"
    )


class BiostarDevices(models.Model):
    _name = "biostar.device"
    _description = "Devices"

    name = fields.Char("Device Name")
    device_id = fields.Char("Device ID", required=True, index=True)
    device_type = fields.Selection(
        [("check_in", "Check In"), ("check_out", "Check Out")]
    )

    @api.model
    def create(self, vals):
        res = super(BiostarDevices, self).create(vals)
        for rec in res:
            if rec.name and "IN" in rec.name:
                rec.device_type = "check_in"
            if rec.name and "Out" in rec.name:
                rec.device_type = "check_out"
        return res


class BiostarDevicesType(models.Model):
    _name = "biostar.device.type"
    _description = "Device Types"

    name = fields.Char("Device Type Name")
    device_type_id = fields.Char("Device Type ID", required=True, index=True)
    is_keypad = fields.Boolean("Is keypad Support")
    is_fingerprint = fields.Boolean("Is fingerprint Support")
    is_card = fields.Boolean("Is card Support")
    is_face = fields.Boolean("Is face Support")
    is_volume = fields.Boolean("Is volume Support")
    is_wifi = fields.Boolean("Is wifi Support")
