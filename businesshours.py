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

def periodize(events, P = timedelta(days=7)):
    """
    takes a list that represents a period of event and extend it with events
    e+P , e-P where P is the timedelta of the period. The Period defaults to
    1 week. Return a sorted result.

    EXAMPLE
    =======

    >>> hours = [(datetime(2000,1,15,9,0),'open')]
    >>> periodize(hours)
    [(datetime.datetime(2000, 1, 8, 9, 0), 'open'), (datetime.datetime(2000, 1, 15, 9, 0), 'open'), (datetime.datetime(2000, 1, 22, 9, 0), 'open')]

    """
    result = []
    for event in events:
        time_event_minus = event[0] - P
        time_event_plus = event[0] + P
        result.extend([(time_event_minus,event[1]),
                        event,
                        (time_event_plus,event[1])])

    result.sort()
    return result

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

def immediately_prior(H,d):
    """
    return the event in H that is immediately prior in time (or
    simultanously occuring) to d.

    EXAMPLE
    =======

    >>> H = [(datetime(2000, 1, 8, 9, 0), 'open'), (datetime(2000, 1, 15, 9, 0), 'open'), (datetime(2000, 1, 22, 9, 0), 'open')]
    >>> d = datetime(2000,1,15,8,0)
    >>> immediately_prior(H,d)
    (datetime.datetime(2000,1,8,9,0), 'open')
    """

    return (datetime(1999,1,1,1,1),'open')

def event_between(H, d1, d2):
    """
    return the events in H that are between the range [d1,d2[

    EXMAPLE
    =======

    >>> H = [(datetime(2000, 1, 8, 9, 0), 'open'), (datetime(2000, 1, 15, 9, 0), 'open'), (datetime(2000, 1, 22, 9, 0), 'open')]
    >>> d1 = datetime(2000,1,14,9,0)
    >>> d2 = datetime(2000,1,16,9,0)
    >>> event_between(H,d1,d2)
    [datetime.datetime(2000,1,15,9,0)]
    """
    return []


def opened_range(H,d1,d2):
    """
    return true if, for the given list of event H, there is a continuous
    open period between d1 and d2.

    EXAMPLE
    =======

    # opened inside the range.
    >>> h = periodize([(datetime(2000,1,15,23,0), 'close'), (datetime(2000,1,16,5,0), 'open')])
    >>> d1 = datetime(2000,1,16,9,0)
    >>> d2 = datetime(2000,1,16,10,0)
    >>> opened_range(h,d1,d2)
    True

    # closed inside the range.
    >>> h = periodize([(datetime(2000,1,15,20,0), 'close'), (datetime(2000,1,16,5,0), 'open')])
    >>> d1 = datetime(2000,1,15,21,0)
    >>> d2 = datetime(2000,1,15,22,0)
    >>> opened_range(h,d1,d2)
    False
    """

    prior = immediately_prior(H,d1)
    events_in = event_between(H, d1, d2)
    close_events_in = [e for e in events_in if e[1] == 'close']

    result = prior[1] == 'open' and len(close_events_in) == 0
    return result

if __name__ == '__main__':
    main()

