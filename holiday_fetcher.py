import requests
from datetime import date, timedelta

def get_upcoming_holidays(country_codes, days_ahead=2):
    target_date = (date.today() + timedelta(days=days_ahead)).isoformat()
    year = date.today().year
    upcoming = []

    for code in country_codes:
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{code}"
        response = requests.get(url)
        if response.status_code == 200:
            holidays = response.json()
            for holiday in holidays:
                if holiday["date"] == target_date:
                    upcoming.append((code, holiday["localName"], holiday["name"], holiday["date"]))
    return upcoming
