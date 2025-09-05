from datetime import datetime , timezone , timedelta
def now():
    return datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
def now_offset(days=0, hours=0, minutes=0, seconds=0):
    """
    回傳台北時間，並根據偏移量調整時間
    可正可負
    """
    base = now()
    offset = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return base + offset
def now_str(format:str):
    return now().strftime(format)

def from_timestamp(time_stamp:datetime.timestamp):
    return datetime.fromtimestamp(time_stamp).astimezone(timezone(timedelta(hours=8)))

def duration_format( small:datetime , big :datetime , format):
    from datetime import timedelta
    delta:timedelta = big - small
    duration_seconds = delta.total_seconds()
    return format_total_seconds(duration_seconds , format)

def format_total_seconds(total_seconds:float , format:str):
    days = hours = m_remainder = minutes = seconds = 0
    if "%d" in format:
        days , h_remainder = divmod(total_seconds , 86400)
    else:
        h_remainder = total_seconds
    if "%H" in format:
        hours , m_remainder = divmod(h_remainder , 3600)
    else:
        m_remainder = total_seconds
    if "%M" in format:
        minutes , seconds = divmod(m_remainder , 60)
    
    return format.replace("%d" , str(int(days))).replace("%H" , str(int(hours))).replace("%M",str(int(minutes))).replace("%S",str(int(seconds)))
    

