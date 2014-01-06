#!/usr/bin/env python3

import argparse
from datetime import datetime, timedelta

# globals
REF_YEAR = 2000
REF_MONTH = 1

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-t',
            '--test',
            help='run the doctest suite and exit(0).',
            action='store_true'
            )

    args = parser.parse_args()

    if args.test:
        import doctest
        doctest.testmod()
        exit(0)

    return

def periodize(hours, P = timedelta(days=7)):
    """
    takes a list that represents a period of event and extend it with events
    e+P , e-P where P is the timedelta of the period. The Period defaults to
    1 week. Return a sorted result.

    EXAMPLE
    =======

    >>> hours = [(datetime(2000,1,15,9,0),'open'),(datetime(2000,1,15,23,0),'close')]
    >>> periodize(hours)
    [(datetime(2000,1,15,9,0),'open'), (datetime(2000,1,15,23,0),'close')]


    """

def transform(elem):
    """
    transform an element of the form:
        ["mon_1_open", "09:00"]

    into
        (datetime(2000,01,15,9,0),"open")

    for further processing.

    EXAMPLE
    =======

    >>> transform(["mon_1_open", "09:00"])
    (datetime.datetime(2000, 1, 15, 9, 0), 'open')

    """
    weekday_to_num = {
            "mon":15,
            "tue":16,
            "wed":17,
            "thu":18,
            "fri":19,
            "sat":20,
            "sun":21
            }

    event = elem[0]
    full_hour = elem[1]

    event_components = event.split("_")
    weekday = event_components[0]
    day = weekday_to_num[weekday]
    state = event_components[-1]

    hour_component = full_hour.split(":")

    hour = int(hour_component[0])
    minutes = int(hour_component[-1])

    date = datetime(REF_YEAR, REF_MONTH, day, hour, minutes)

    result = (date,state)
    return result


if __name__ == '__main__':
    main()

