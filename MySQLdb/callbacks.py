#!/usr/bin/env python

from MySQLdb import (
    set_wait_callback,
    POLL_OK,
    POLL_READ,
    POLL_WRITE,
    POLL_EXCEPT,
    POLL_TIMEOUT
)

try:
    from gevent import select
    from gevent.select import (
        POLLIN,
        POLLOUT,
        POLLPRI
    )
except ImportError:
    import select
    from select import (
        POLLIN,
        POLLOUT,
        POLLPRI
    )


def wait_for_mysql(conn, status):
    """Waits for the MySQL file descriptor to be ready for the next operation"""

    # Creates a new poll object; doesn't actually poll anything...
    pfd = select.poll()

    # Bitmask of events to listen for
    events = (
        (POLLIN if status & POLL_READ else 0) |
        (POLLOUT if status & POLL_WRITE else 0) |
        (POLLPRI if status & POLL_EXCEPT else 0)
    )

    # conn implements fileno() so can be passed as-is
    pfd.register(conn, events)

    if status & POLL_TIMEOUT:
        # Must convert to milliseconds or you'll get some weird behaviour
        timeout = 1000 * conn.wait_timeout()
    else:
        # No timeout
        timeout = -1

    # Poll the fd for the specified events. On timeout, will be []
    revents = pfd.poll(timeout)

    try:
        # Should look like: [(fd, events)]
        revents = revents[0][1]
    except IndexError:
        # Operation timed out and [] was returned
        status = POLL_TIMEOUT
    else:
        # Create a mask of what actually happened
        status = (
            (POLL_READ if revents & POLLIN else 0) |
            (POLL_WRITE if revents & POLLOUT else 0) |
            (POLL_EXCEPT if revents & POLLPRI else 0)
        )

    return status


def gevent_callback(conn):
    # The first time the connection is polled, it returns the status of the
    # first operation so it doesn't need an event
    status = conn.poll(0)

    # Loop until the operation has completed
    while status != POLL_OK:
        status = wait_for_mysql(conn, status)
        status = conn.poll(status)


def patch_for_gevent():
    set_wait_callback(gevent_callback)
