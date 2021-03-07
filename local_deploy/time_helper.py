import datetime


def dstr_obj(dtstr):
    """Convert date in string format to datetime object.

    eg. 'Wed Mar 08 03:11:05 +0000 2019' to 2019-03-08 03:11:05

    :param dtsr: datetime string
    :return: datetime
    :rtype: datetime object
    """

    dt = datetime.datetime.strptime(dtstr, '%a %b %d %H:%M:%S %z %Y')
    dtstr2 = dt.strftime('%Y-%m-%d %H:%M:%S')
    return datetime.datetime.strptime(dtstr2, '%Y-%m-%d %H:%M:%S')


def current_time():
    """Return current time as datetime object."""

    timenow = datetime.datetime.utcnow()
    return datetime.datetime.strptime(timenow.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')


def lag_time(timenow, x):
    """Return time x minutes before timenow.

    :param timenow: datetime object
    :param x: minutes (integer)
    :return: lagged time.
    :rtype: datetime object
    """

    return timenow-datetime.timedelta(minutes=x)


def isin_window(dt1, dt2, x):
    """Is the input time within a given window ?

    :param dt1: Start of window (datetime object)
    :param dt2: End of window   (datetime object)
    :param x: time to be checked  (datetime object)
    :return: True if x is dt1<= x <dt2
    :rtype: Boolean
    """

    return True if (x >= dt1 and x < dt2) else False
