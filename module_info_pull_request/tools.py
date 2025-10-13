# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import pytz


def naive_dt(datetime_with_timezone):
    if datetime_with_timezone:
        return datetime_with_timezone.astimezone(pytz.utc).replace(tzinfo=None)
    else:
        return None
