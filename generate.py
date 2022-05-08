from icalendar import Calendar, Event
import re
from titlecase import titlecase
from datetime import datetime
import urllib.request
import pytz


with urllib.request.urlopen(
    "https://www.formula1.com/calendar/Formula_1_Official_Calendar.ics"
) as f:
    original_cal = Calendar.from_ical(f.read())


# vcal: https://datatracker.ietf.org/doc/html/rfc5545
c = Calendar()
# VERSION is required
c.add("version", "2.0")
# PRODID is required
# https://en.wikipedia.org/wiki/Formal_Public_Identifier
c.add("prodid", "+//IDN georgewitteman.com//Formula 1 Calendar//EN")
# Formula 1 color from their website
c.add("X-APPLE-CALENDAR-COLOR", "#E10600")
c.add("X-WR-CALNAME", original_cal["X-WR-CALNAME"])

locations = {
    "Austin": {
        "location": "Circuit of The Americas",
        "tz": "America/Chicago",
        "latitude": "30.1345808",
        "longitude": "-97.6358511",
    },
    "Baku": {
        "location": "Baku City Circuit",
        "tz": "Asia/Baku",
    },
    "Catalunya": {
        "location": "Circuit de Barcelona-Catalunya",
        "tz": "Europe/Madrid",
    },
    "Hungaroring": {
        "location": "Hungaroring",
        "tz": "Europe/Budapest",
    },
    "Imola": {
        "location": "Autodromo Enzo e Dino Ferrari",
        "tz": "Europe/Rome",
    },
    "Interlagos": {
        "location": "Autódromo José Carlos Pace",
        "tz": "America/Sao_Paulo",
    },
    "Jeddah": {
        "location": "Jeddah Corniche Circuit",
        "tz": "Asia/Riyadh",
    },
    "Melbourne": {
        "location": "Albert Park Circuit",
        "tz": "Australia/Melbourne",
    },
    "Mexico City": {
        "location": "Autódromo Hermanos Rodríguez",
        "tz": "America/Mexico_City",
    },
    "Miami": {
        "location": "Miami International Autodrome",
        "tz": "America/New_York",
    },
    "Monte Carlo": {
        "location": "Circuit de Monaco",
        "tz": "Europe/Berlin",
    },
    "Montreal": {
        "location": "Circuit Gilles-Villeneuve",
        "tz": "America/Toronto",
    },
    "Monza": {
        "location": "Autodromo Nazionale Monza",
        "tz": "Europe/Rome",
    },
    "Paul Ricard": {
        "location": "Circuit Paul Ricard",
        "tz": "Europe/Paris",
    },
    "Sakhir": {
        "location": "Bahrain International Circuit",
        "tz": "Asia/Bahrain",
    },
    "Silverstone": {
        "location": "Silverstone Circuit",
        "tz": "Europe/London",
    },
    "Singapore": {
        "location": "Marina Bay Street Circuit",
        "tz": "Asia/Singapore",
    },
    "Spa-Francorchamps": {
        "location": "Circuit de Spa-Francorchamps",
        "tz": "Europe/Brussels",
    },
    "Spielberg": {
        "location": "Red Bull Ring",
        "tz": "Europe/Vienna",
    },
    "Suzuka": {
        "location": "Suzuka International Racing Course",
        "tz": "Asia/Tokyo",
    },
    "Yas Marina Circuit": {
        "location": "Yas Marina Circuit",
        "tz": "Asia/Dubai",
    },
    "Zandvoort": {
        "location": "Circuit Zandvoort",
        "tz": "Europe/Amsterdam",
    },
}

for tz in [l["tz"] for l in locations.values()]:
    break
    with urllib.request.urlopen(f"https://static.tzurl.org/zoneinfo/{tz}.ics") as f:
        tz_cal = Calendar.from_ical(f.read())
        for vtimezone in tz_cal.walk("VTIMEZONE"):
            c.add_component(vtimezone)

timezones = set()
for event in original_cal.walk(name="VEVENT"):
    e = Event()
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.7.2
    e.add("dtstamp", event["dtstamp"])
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.4.3
    e.add("organizer", event["organizer"])
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.1.11
    e.add("status", event["status"])
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.4.7
    e.add("uid", event["uid"])
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.1.5
    e.add("description", event["description"])
    # https://docs.microsoft.com/en-us/openspecs/exchange_server_protocols/ms-oxcical/cd68eae7-ed65-4dd3-8ea7-ad585c76c736
    e.add("X-MICROSOFT-CDO-BUSYSTATUS", event["X-MICROSOFT-CDO-BUSYSTATUS"])
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.2.7
    e.add("transp", event["transp"])
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.7.4
    e.add("sequence", event["sequence"])

    if event.get("last-modified"):
        # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.7.3
        e.add("last-modified", event["last-modified"])

    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.1.12
    orig_summary = str(event["summary"]).lower()
    summary_without_prefix = orig_summary.removeprefix("formula 1").strip()
    event_name, session_name = summary_without_prefix.split(" - ", maxsplit=1)
    event_name_without_year = event_name.removesuffix(str(event["dtstart"].dt.year)).strip()
    e.add("summary", titlecase(f"{session_name} ({event_name_without_year})".lower()))

    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.4.6
    urls = re.findall(
        r"(https?://www.formula1.com/en/racing\S+)", str(event["description"]).strip()
    )
    if urls:
        e.add("url", urls[0])

    location_str = str(event["location"]).strip()
    location = locations[location_str]
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.1.7
    e.add("location", location["location"])
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.2.4
    e.add("dtstart", event["dtstart"].dt.astimezone(pytz.timezone(location["tz"])))
    # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.2.2
    e.add("dtend", event["dtend"].dt.astimezone(pytz.timezone(location["tz"])))

    if location.get("longitude") and location.get("latitude"):
        e.add("geo", (location["latitude"], location["longitude"]))

    c.add_component(e)


with open("full.ics", "wb") as f:
    f.write(c.to_ical(sorted=True))
