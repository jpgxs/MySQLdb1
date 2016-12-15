MySQLdb1
========

This is the legacy (1.x) version of MySQLdb. While it is still being
maintained, there will not be a lot of new feature development. 

[![Build Status](https://secure.travis-ci.org/farcepest/MySQLdb1.png)](http://travis-ci.org/farcepest/MySQLdb1)


Gevent Support
--------------
Gevent support is available in a similar way to psycopg2. It MUST be built against libmariadb for this to work.

```python
import MySQLdb
from gevent import socket as gsocket


class WaitTimeout(gsocket.timeout):
    pass


def callback(conn):
    event = 0

    while True:
        state = conn.poll(event)

        if state == gmysql.POLL_OK:
            break
        
        if state & MySQLdb.POLL_TIMEOUT:
            timeout = conn.wait_timeout()
        else:
            timeout = -1

        try:
            if state & MySQLdb.POLL_READ and state & gmysql.POLL_WRITE:
                gsocket.wait_readwrite(conn.fileno(), timeout=timeout, 
                                       timeout_exc=WaitTimeout)

                event = MySQLdb.POLL_READ | MySQLdb.POLL_WRITE

            elif state & MySQLdb.POLL_READ:
                gsocket.wait_read(conn.fileno(), timeout=timeout, 
                                  timeout_exc=WaitTimeout)

                event = MySQLdb.POLL_READ

            elif state & MySQLdb.POLL_WRITE:
                gsocket.wait_write(conn.fileno(), timeout=timeout,
                                   timeout_exc=WaitTimeout)

                event = MySQLdb.POLL_WRITE

            else:
                raise RuntimeError("Poll returned: %s" % state)


# Raises MySQLdb.ProgrammingError if async support was not compiled in
MySQLdb.set_wait_callback(callback)
```

TODO
----

* A bugfix 1.2.4 release
* A 1.3.0 release that will support Python 2.7-3.3
* The 2.0 version is being renamed [moist][] and is heavily refactored.

Projects
--------

* [MySQLdb-svn][]

	This is the old Subversion repository located on SourceForge.
	It has all the early historical development of MySQLdb through 1.2.3,
	and also is the working repository for ZMySQLDA. The trunk on this
	repository was forked to create the [MySQLdb2][] repository.

* [MySQLdb1][]

	This is the new (active) git repository.
	Only updates to the 1.x series will happen here.

* [MySQLdb2][]

	This is the now obsolete Mercurial repository for MySQLdb-2.0
	located on SourceForge. This repository has been migrated to the
    [moist][] repository.


[MySQLdb1]: https://github.com/farcepest/MySQLdb1
[moist]: https://github.com/farcepest/moist
[MySQLdb-svn]: https://sourceforge.net/p/mysql-python/svn/
[MySQLdb2]: https://sourceforge.net/p/mysql-python/mysqldb-2/
