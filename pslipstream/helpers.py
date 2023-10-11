from datetime import datetime
from typing import Optional

from dateutil.tz import tzoffset
from pycdlib.dates import VolumeDescriptorDate


def convert_iso_descriptor_date(vdd: VolumeDescriptorDate) -> Optional[datetime]:
    """
    Convert an ISO Descriptor Date to a DateTime object.
    ISO Descriptor Dates are offset from GMT in 15 minute intervals.
    This is offset to the user's timezone via tzoffset.
    Returns None if the Descriptor Date does not specify the year.
    It assumes a default for any other value missing from the Descriptor Date.
    """
    if not vdd.year:
        return None
    return datetime(
        year=vdd.year,
        month=vdd.month,
        day=vdd.dayofmonth,
        hour=vdd.hour,
        minute=vdd.minute,
        second=vdd.second,
        microsecond=vdd.hundredthsofsecond,
        tzinfo=tzoffset("GMT", (15 * vdd.gmtoffset) * 60)
    )
