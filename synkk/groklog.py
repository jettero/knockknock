
import time
import logging
import re
import uptime
from collections import namedtuple
from . sig import DISCOVERABLE

log = logging.getLogger('synkk:groklog')

LOG_PREFIX = 'SYNKK'

# dmesg time is super annoying
# my dmesg times (reported by seconds since boot and /proc/uptime or via --ctime)
# are off by 50 or 60 seconds (depending on the boottime compuation used).
# I tried quite a few things, including misc/*.c ...
# ... it took me a while to notice, but all my dmesg times are off, not my boottime
# computations.
# I'm teaching the dmesg log tailer to find the end of the file and just
# disabling all this stuff for now. Leaving it in, cuz I may circle back to it.
# (I'd rather not introduce a boottime fudgefactor...)
BOOTTIME  = time.mktime( uptime.boottime().timetuple() )
plan_item = namedtuple("plan_item", ['src', 'regex', 'reject', 'cast'])

class GrokLog(object):
    re_plan = (
        # TODO: these plan rules should really come from config
        plan_item(src=None, reject=True, cast=None,
            regex=re.compile(r'^\[(?P<_time>[^\]]+)\]\s+(?P<_log_ent>.+)')),
        plan_item(src='_log_ent', reject=True, cast=None,
            regex=re.compile(r'^(?P<prefix>.+?)\s+IN=(?P<nic>\S+)\s+(?P<_fields>.*)')),
        plan_item(src='_fields', reject=True, cast=int,  regex=re.compile(r'SEQ=(?P<seq>\d+)')),
        plan_item(src='_fields', reject=True, cast=int,  regex=re.compile(r'ACK=(?P<ack>\d+)')),
        plan_item(src='_fields', reject=True, cast=int,  regex=re.compile(r'WINDOW=(?P<win>\d+)')),
        plan_item(src='_fields', reject=True, cast=None, regex=re.compile(r'SRC=(?P<src>[\d\.\:\[\]]+)')),
        plan_item(src='_fields', reject=True, cast=None, regex=re.compile(r'DST=(?P<dst>[\d\.\:\[\]]+)')),
        plan_item(src='_fields', reject=True, cast=int,  regex=re.compile(r'SPT=(?P<spt>\d+)')),
        plan_item(src='_fields', reject=True, cast=int,  regex=re.compile(r'DPT=(?P<dpt>\d+)')),
        plan_item(src='_fields', reject=True, cast=int,  regex=re.compile(r'\bID=(?P<id>\d+)')),
    )

    def __init__(self, line, log_prefix=LOG_PREFIX, age_reject=0):
        self.understood = False
        log.debug(f'attempting to grok "{line}"')
        self.dat = dict()
        for pi in self.re_plan:
            li_txt = pi.src
            if pi.src is None:
                data = line
                li_txt = '<entire line>'
            elif pi.src in self.dat:
                data = self.dat[pi.src]
            elif pi.reject:
                log.debug(f"'{li_txt}' not found in data, rejecting log entry")
                self.understood = False # we don't understand this record
                return
            m = pi.regex.search(data)
            if m:
                d = m.groupdict()
                if pi.cast:
                    try:
                        dc = { k: pi.cast(v) for k,v in d.items() }
                        d = dc
                    except ValueError as e:
                        log.debug(f"found fields in '{li_txt}': {k} -- conversion error: {e}")
                        self.understood = False
                        return
                k = ', '.join(d.keys())
                log.debug(f"found fields in '{li_txt}': {k}")
                self.dat.update(d)
                if '_time' in d:
                    if not self._grok_time(age_reject=age_reject):
                        self.understood = True # we understand, we choose to quit
                        return
                if 'prefix' in d:
                    if d['prefix'] != log_prefix:
                        log.debug(f'found non-matching log prefix: {d["prefix"]} != {log_prefix}')
                        self.understood = True # we understand, we choose to quit
                        return
            elif pi.reject:
                log.debug(f"'{pi.regex.pattern}' failed to match, rejecting log entry")
                self.understood = False # we don't understand this record
                return
        for k in [ k for k in self.dat if k.startswith('_') and k != '_time' ]:
            del self.dat[k]
        self.understood = True

    def __getattribute__(self, k):
        try: return super(GrokLog, self).__getattribute__(k)
        except AttributeError: pass
        return self.dat.get(k)

    def __str__(self):
        return f'GL:{self.passed}({self.as_dict})'
    __repr__ = __str__

    def __bool__(self):
        return self.passed

    def _grok_time(self, age_reject):
        t = self.dat.get('_time')
        if not t:
            return False
        try:
            self.dat['_time'] = t = BOOTTIME + float(t)
            a = time.time() - t
            log.debug(f"'_time' field found, age computed as: {a}s")
            self.dat['age'] = a
        except ValueError as e:
            log.debug(f"failed to parse _time field: {e}")
            return False
        if age_reject and age_reject < self.age:
            log.debug(f"record too old according to {age_reject}s < {self.age}s")
            return False
        return True

    @property
    def as_dict(self):
        return { k: self.dat[k] for k in self.dat }

    @property
    def passed(self):
        if not self.understood:
            return False
        for k in DISCOVERABLE:
            if k not in self.dat:
                return False
        return True
