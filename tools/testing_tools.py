

import math



def ok_(expr, msg=None):
    """Shorthand for assert. Saves 3 whole characters!
    """
    if not expr:
        raise AssertionError(msg)


def eq_(a, b, rel_tol=None,  msg=None):
    """Shorthand for 'assert a == b, "%r != %r" % (a, b)
    if rel_tol set then allows for almost equal.  rel_tol is the percentage difference allowed.
    Suggested value for rel_tol 1e-9
    """

    if rel_tol:
        if not math.isclose(a, b, rel_tol=rel_tol):
            raise AssertionError(msg or "%r != %r" % (a, b))
    else:
        if not a == b:
            raise AssertionError(msg or "%r != %r" % (a, b))


def assertDatesMatch(dt1, dt2, msg=None, seconds=60):

    # must both be dates to succeed
    if not dt1 or not dt2:
        raise AssertionError(msg)


    #
    # tz = timezone.get_current_timezone()

    # using arrow forces them into tz aware datetimes
    # dt1.replace(tzinfo=tz)
    # dt2.replace(tzinfo=tz)


    # note: abs doesn't work if dt1 < dt2
    if dt1 > dt2:
        diff = (dt1 - dt2).seconds
    else:
        diff = (dt2 - dt1).seconds


    if not (diff < seconds):

        if not msg:
            msg = "Differences in datetimes %s and %s is %d seconds and only allowed %d" % (str(dt1), str(dt2), diff, seconds)

        raise AssertionError(msg)
