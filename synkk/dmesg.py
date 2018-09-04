
import logging
import subprocess
import re
import os, fcntl
import time

log = logging.getLogger('synkk:dmesg')

DMESG_CMD = ['/bin/dmesg', '--level', 'debug', '--follow']
MIN_WAIT  = 0.250
DEF_WAIT  = 2

class DT(object):
    def __init__(self, timeout):
        self.start = time.time()
        if isinstance(timeout, DT):
            timeout = timeout.remaining
        self.timeout = timeout
    @property
    def ok(self):
        self._dt = time.time() - self.start
        return self._dt < self.timeout
    @property
    def remaining(self):
        return self.timeout - self._dt
    @property
    def elapsed(self):
        return self._dt

class DmesgReader(object):
    sp = None
    def __init__(self, cmd=None, min_wait=MIN_WAIT, read_timeout=DEF_WAIT, wait_timeout=DEF_WAIT, find_live=True):
        self.find_live = find_live
        self.w_to = wait_timeout
        self.m_to = min_wait
        self.r_to = read_timeout
        if cmd is None:
            cmd = DMESG_CMD
        if not isinstance(cmd, list):
            # TODO: should use shlex or something
            cmd = cmd.split()
        self.cmd = cmd

    def _restart(self):
        if self.sp:
            log.debug("terminating dmesg process")
            self.sp.terminate()
            self.sp.wait(timeout=self.w_to)
        log.debug("starting dmesg process")
        self.sp = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
        fno = self.sp.stdout.fileno()
        oflags = fcntl.fcntl(fno, fcntl.F_GETFL)
        fcntl.fcntl(fno, fcntl.F_SETFL, oflags | os.O_NONBLOCK)
        if self.find_live:
            while self.readline(timeout=0.5):
                log.debug("waiting for the end of the file")

    def _started(self):
        if not self.sp or self.sp.poll() is not None:
            self._restart()

    def _readline(self, timeout=None, loop_wait=None):
        if timeout is None:
            timeout = self.r_to
        if loop_wait is None:
            loop_wait = self.m_to
        dt = DT(timeout)
        log.debug("_readline timeout=%0.1f", dt.timeout)
        while dt.ok:
            self._started()
            line = self.sp.stdout.readline()
            if line:
                return line.decode()
            else:
                time.sleep(loop_wait)

    def readline(self, timeout=None):
        if timeout is None:
            timeout = self.r_to
        loop_counter = 0
        dt = DT(timeout)
        while dt.ok:
            loop_counter += 1
            log.debug("readline timeout=%0.1f dt=%0.1f loop-%d", dt.timeout, dt.elapsed, loop_counter)
            line = self._readline(timeout=dt)
            if not line:
                return
            return line

    def __iter__(self):
        dt = DT(self.r_to)
        while dt.ok:
            line = self.readline(timeout=dt)
            if not line:
                break
            yield line
