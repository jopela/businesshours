#!/usr/bin/env python3

import argparse
from datetime import datetime, timedelta

# globals
REF_YEAR = 2000
REF_MONTH = 1
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
WEEKDAY_TO_NUM = {
                    "mon":15,
                    "tue":16,
                    "wed":17,
                    "thu":18,
                    "fri":19,
                    "sat":20,
                    "sun":21
                 }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            'hours',
            help='the opening hours string. The linker app thing requires'\
                    'them to be formatted like this: [ ["mon_1_open","09:00"]'\
                    ' ... ].'
            )

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


    # NOTE: user input are trusted here. This would be a no go usually
    # but the only user are trusted.
    #hours = eval(args.hours)
    hours = [["thu_1_open", "12:00"], ["thu_1_close", "14:00"], ["fri_1_open", "12:00"], ["fri_1_close", "14:00"], ["thu_2_open", "19:00"], ["thu_2_close", "22:00"], ["fri_2_open", "19:00"], ["fri_2_close", "22:00"]]
    result = restaurant_opening(hours)
    result_s = repr(result).lower()
    print(result_s)
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

    >>> transform(["tue_1_close", "09:00"])
    (datetime.datetime(2000, 1, 16, 9, 0), 'close')

    >>> transform(["tue_2_close", "09:00"])
    (datetime.datetime(2000, 1, 16, 9, 0), 'close')
    """

    event = elem[0]
    full_hour = elem[1]

    event_components = event.split("_")
    weekday = event_components[0]
    day = WEEKDAY_TO_NUM[weekday]
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
    (datetime.datetime(2000, 1, 8, 9, 0), 'open')
    """

    # take all the previous events
    # sort them
    # take the last element from the list.
    # NOTE: list is guaranteed to have lenght of at least 1.

    previous = [ e for e in H if e[0] <= d ]
    previous.sort()
    result = previous[-1]

    return result

def event_between(H, d1, d2):
    """
    return the events in H that are between the range [d1,d2[

    EXMAPLE
    =======

    >>> H = [(datetime(2000, 1, 8, 9, 0), 'open'), (datetime(2000, 1, 15, 9, 0), 'open'), (datetime(2000, 1, 22, 9, 0), 'open')]
    >>> d1 = datetime(2000,1,14,9,0)
    >>> d2 = datetime(2000,1,16,9,0)
    >>> event_between(H,d1,d2)
    [(datetime.datetime(2000, 1, 15, 9, 0), 'open')]
    """

    result = [e for e in H if e[0] >= d1 and e[0] < d2]
    return result

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

    result = (prior[1] == 'open') and (len(close_events_in) == 0)
    return result

def hourmin(hour_s):
    """
    EXAMPLE
    =======

    >>> hourmin("09:48")
    (9, 48)
    """

    hour_comp = hour_s.split(":")
    hour = int(hour_comp[0])
    minutes = int(hour_comp[1])
    result = (hour,minutes)
    return result

def daily_range(hour_range):
    """
    takes a range containing hours (e.g ("09:00","10:00")) and transform it
    into a list of daily datetime ranges.

    EXAMPLE
    =======

    >>> daily_range(("09:00","10:00"))
    [(datetime.datetime(2000, 1, 15, 9, 0), datetime.datetime(2000, 1, 15, 10, 0)), (datetime.datetime(2000, 1, 16, 9, 0), datetime.datetime(2000, 1, 16, 10, 0)), (datetime.datetime(2000, 1, 17, 9, 0), datetime.datetime(2000, 1, 17, 10, 0)), (datetime.datetime(2000, 1, 18, 9, 0), datetime.datetime(2000, 1, 18, 10, 0)), (datetime.datetime(2000, 1, 19, 9, 0), datetime.datetime(2000, 1, 19, 10, 0)), (datetime.datetime(2000, 1, 20, 9, 0), datetime.datetime(2000, 1, 20, 10, 0)), (datetime.datetime(2000, 1, 21, 9, 0), datetime.datetime(2000, 1, 21, 10, 0))]
    """

    result = []
    for day in WEEKDAYS:
        hour1,min1 = hourmin(hour_range[0])
        hour2,min2 = hourmin(hour_range[1])
        d1 = datetime(REF_YEAR, REF_MONTH, WEEKDAY_TO_NUM[day], hour1, min1)
        d2 = datetime(REF_YEAR, REF_MONTH, WEEKDAY_TO_NUM[day], hour2, min2)
        result.append((d1,d2))

    return result

def businesshours(H, ranges):
    """ given a series of event H and a list of pairs of ranges, return a list
    of bool that indicates if the commerce is opened in the given range for
    at least one day of the week.

    EXAMPLE
    =======

    # simple example, opened in all ranges.
    >>> H = [ ["mon_1_open", "09:00"], ["mon_1_close", "22:00"], ["tue_1_open", "09:00"], ["tue_1_close", "22:00"] ]
    >>> ranges = [("09:00","10:00"),("11:30","12:30"),("17:00","18:00")]
    >>> businesshours(H,ranges)
    [True, True, True]

    # simple example, opened in the first and second range
    >>> H = [ ["mon_1_open", "09:00"], ["mon_1_close", "22:00"], ["tue_1_open", "09:00"], ["tue_1_close", "22:00"] ]
    >>> ranges = [("08:00","10:00"),("11:30","12:30"),("17:00","22:01")]
    >>> businesshours(H,ranges)
    [False, True, False]

    # real worl example, cafe pamplona (ranges correspond to breakfast, dinner, supper).
    >>> H = [["mon_1_open", "11:00"], ["mon_1_close", "00:00"], ["tue_1_open", "11:00"], ["tue_1_close", "00:00"], ["wed_1_open", "11:00"], ["wed_1_close", "00:00"], ["thu_1_open", "11:00"], ["thu_1_close", "00:00"], ["fri_1_open", "11:00"], ["fri_1_close", "00:00"], ["sat_1_open", "11:00"], ["sat_1_close", "00:00"], ["sun_1_open", "11:00"], ["sun_1_close", "00:00"]]
    >>> ranges = [("09:00","10:00"),("11:30","12:30"),("17:00","18:00")]
    >>> businesshours(H,ranges)
    [False, True, True]

    # real world example, miller ale house (ranges correspond to breakfast, dinner, supper).
    >>> H = [["mon_1_open", "11:00"], ["mon_1_close", "01:00"], ["tue_1_open", "11:00"], ["tue_1_close", "01:00"], ["wed_1_open", "11:00"], ["wed_1_close", "01:00"], ["thu_1_open", "11:00"], ["thu_1_close", "01:00"], ["fri_1_open", "11:00"], ["fri_1_close", "01:00"], ["sat_1_open", "11:00"], ["sat_1_close", "01:00"], ["sun_1_open", "12:00"], ["sun_1_close", "00:00"]]
    >>> ranges = [("09:00","10:00"),("11:30","12:30"),("17:00","18:00")]
    >>> businesshours(H,ranges)
    [False, True, True]

    #


    """
    # Convert H into something I can work with
    transformed = [transform(e) for e in H]
    full_period = periodize(transformed)

    result = []
    for r in ranges:
        daily_ranges = daily_range(r)
        openings = [opened_range(full_period,d1,d2) for d1,d2 in daily_ranges]
        result.append(any(openings))

    return result

def all_open(H):
    """
    return true if the H contains only opening events.
    """

    openings = [e[1] == 'open' for e in H]
    result = all(openings)
    return result

def restaurant_opening(H):
    """
    return a string of the form bool,bool,bool that represents weither the
    commerce with openings hours H offers breakfast, dinner and supper.

    EXAMPLE
    =======
    # should not flip out when empty list is given.
    >>> restaurant_opening([])
    [False, False, False]

    >>> H = [["mon_1_open", "11:00"], ["mon_1_close", "00:00"], ["tue_1_open", "11:00"], ["tue_1_close", "00:00"], ["wed_1_open", "11:00"], ["wed_1_close", "00:00"], ["thu_1_open", "11:00"], ["thu_1_close", "00:00"], ["fri_1_open", "11:00"], ["fri_1_close", "00:00"], ["sat_1_open", "11:00"], ["sat_1_close", "00:00"], ["sun_1_open", "11:00"], ["sun_1_close", "00:00"]]
    >>> restaurant_opening(H)
    [False, True, True]

    >>> H = [["tue_1_open", "12:00"], ["tue_1_close", "23:00"], ["wed_1_open", "12:00"], ["wed_1_close", "23:00"], ["thu_1_open", "12:00"], ["thu_1_close", "23:00"], ["fri_1_open", "12:00"], ["fri_1_close", "23:00"], ["sat_1_open", "20:00"], ["sat_1_close", "23:00"]]
    >>> restaurant_opening(H)
    [False, True, True]

    """

    if len(H) == 0:
        return [False,False,False]

    # opening hours that only state that the shop open leads to unreliable
    # results. This is because the shop never close ! so will be available
    # all the time.
    if all_open(H):
        return [False,False,False]

    breakfast_ranges = [("08:30","09:00"),("09:00","10:00")]
    dinner_ranges = [("11:30","12:30"),("13:15","14:15")]
    supper_ranges = [("17:00","18:00"), ("18:00","19:00"), ("19:00","20:00"),
                     ("20:00","21:00")]

    breakfast_opened = any(businesshours(H, breakfast_ranges))
    dinner_opened = any(businesshours(H, dinner_ranges))
    supper_opened = any(businesshours(H, supper_ranges))

    result = [breakfast_opened,dinner_opened,supper_opened]
    return result

if __name__ == '__main__':
    main()

