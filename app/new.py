

from datetime import datetime, timedelta
import re
import time

# method to got the number in a string


def get_hours(string: str) -> int:
    return int(re.findall('\d+', string)[0])


def get_created_at(string: str) -> str:
    # Get the current date and time
    hours = get_hours(string)
    now = datetime.now() - timedelta(hours=hours)
    return now


def get_expired_at(created_at: datetime) -> datetime:
    # Get the current date and time
    hours = get_hours(created_at)
    now = datetime.now() + timedelta(days=7)
    return now


user_query_keywords = 'python,angular,python developer'
keywords = 'python'
list_of_keywords = keywords.split(',')
for keyword in list_of_keywords:
    if keyword in user_query_keywords.split(','):
        print(keyword)
    else:
        print('not found')
