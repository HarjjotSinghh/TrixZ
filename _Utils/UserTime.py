import datetime, pytz
from   _Utils import FuzzySearch

def getClockForTime(time_string):
	try:
		t = time_string.split(" ")
		if len(t) == 2:
			t = t[0].split(":")
		elif len(t) == 3:
			t = t[1].split(":")
		else:
			return time_string
		hour = int(t[0])
		minute = int(t[1])
	except:
		return time_string
	clock_string = ""
	if minute > 44:
		clock_string = str(hour + 1) if hour < 12 else "1"
	elif minute > 14:
		clock_string = str(hour) + "30"
	else:
		clock_string = str(hour)
	return time_string +" :clock" + clock_string + ":"

def getUserTime(member, settings, time = None, strft = "%Y-%m-%d %I:%M %p", clock = True, force = None):
	offset = force if force else settings.getGlobalUserStat(member,"TimeZone",settings.getGlobalUserStat(member,"UTCOffset",None))
	if offset == None:
		t = getClockForTime(time.strftime(strft)) if clock else time.strftime(strft)
		return { "zone" : 'UTC', "time" : t, "vanity" : "{} {}".format(t,"UTC") }
	t = getTimeFromTZ(offset, time, strft, clock)
	if t == None:
		t = getTimeFromOffset(offset, time, strft, clock)
	t["vanity"] = "{} {}".format(t["time"],t["zone"])
	return t

def getTimeFromOffset(offset, t = None, strft = "%Y-%m-%d %I:%M %p", clock = True):
	offset = offset.replace('+', '')
	try:
		hours, minutes = map(int, offset.split(':'))
	except:
		try:
			hours = int(offset)
			minutes = 0
		except:
			return None
	msg = 'UTC'
	if t == None:
		t = datetime.datetime.utcnow()
	if hours > 0:
		msg += '+{}'.format(offset)
		td = datetime.timedelta(hours=hours, minutes=minutes)
		newTime = t + td
	elif hours < 0:
		msg += '{}'.format(offset)
		td = datetime.timedelta(hours=(-1*hours), minutes=(-1*minutes))
		newTime = t - td
	else:
		newTime = t
	if clock:
		ti = getClockForTime(newTime.strftime(strft))
	else:
		ti = newTime.strftime(strft)
	return { "zone" : msg, "time" : ti }


def getTimeFromTZ(tz, t = None, strft = "%Y-%m-%d %I:%M %p", clock = True):
	zone = next((pytz.timezone(x) for x in pytz.all_timezones if x.lower() == tz.lower()),None)
	if zone == None:
		return None
	zone_now = datetime.datetime.now(zone) if t == None else pytz.utc.localize(t, is_dst=None).astimezone(zone)
	ti = getClockForTime(zone_now.strftime(strft)) if clock else zone_now.strftime(strft)
	return { "zone" : str(zone), "time" : ti}
