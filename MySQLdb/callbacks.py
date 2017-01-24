#!/usr/bin/env python

from gevent.event import Event
from gevent.hub import get_hub

from MySQLdb import set_wait_callback
from MySQLdb import (POLL_OK,
                     POLL_READ,
                     POLL_WRITE,
                     POLL_EXCEPT,
                     POLL_TIMEOUT)

_GEV_READ = 1
_GEV_WRIT = 2


class PollResult(object):

    __slots__ = (
        'event',
        'events',
    )

    def __init__(self):
        self.events = set()
        self.event = Event()

    def add_event(self, events, fd):
        if events < 0:
            flags = POLL_EXCEPT
        else:
            flags = (
                (POLL_READ if events & _GEV_READ else 0) |
                (POLL_WRITE if events & _GEV_WRIT else 0)
            )
        self.events.add(flags)
        self.event.set()


def wait_for_mysql(conn, status):
    """Waits for the MySQL file descriptor to be ready for the next operation"""

    # Get the gevent event loop
    ev_loop = get_hub().loop

    # Bitmask of events to listen for
    events = (
        (_GEV_READ if status & POLL_READ else 0) |
        (_GEV_WRIT if status & POLL_WRITE else 0)
    )

    # Get the connection's file descriptor
    fd = conn.fileno()

    # Register it with the event loop to be watched
    ev_watcher = ev_loop.io(fd, events)
    ev_watcher.priority = ev_loop.MAXPRI

    if status & POLL_TIMEOUT:
        timeout = conn.wait_timeout()
    else:
        # No timeout
        timeout = -1

    ev_result = PollResult()
    try:
        # Start the watcher
        ev_watcher.start(ev_result.add_event, fd, pass_events=True)
        ev_result.event.wait(timeout=timeout)

        # Get the list of events. Should contain one item or nothing on timeout
        revents = list(ev_result.events)
    finally:
        ev_watcher.stop()

    try:
        status = revents[0]
    except IndexError:
        # Operation timed out and [] was returned
        status = POLL_TIMEOUT

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
