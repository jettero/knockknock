# coding: utf-8

import hashlib
#from functools import partial
from collections import namedtuple

NONCE_PLAN  = ('spt',)
SECRET_PLAN = ('secret',)
HMAC_PLAN   = NONCE_PLAN + ('dpt',) + SECRET_PLAN
SIG_PLAN    = ('ack', 'win', 'seq', 'id')
SIG_DETAIL  = {'ack': 4, 'win': 2, 'seq': 4, 'id': 2}

PLANNED = set(NONCE_PLAN).union(HMAC_PLAN).union(SIG_PLAN)
DISCOVERABLE = PLANNED - set(SECRET_PLAN)

def compute_sig(**kw):
    dat = HMACData.slurp(kw)
    sig = Sig(*dat)
    out = sig.compute_sig()
    kw.update({ k:v for k,v in zip(SIG_PLAN, out) })
    return kw

def compare_sig(**kw):
    sig = compute_sig(**kw)
    for k in SIG_PLAN:
        try:
            assert sig[k] == kw[k]
        except AssertionError:
            return False
    return True

class Sig(object):
    def __init__(self, *items):
        if len(items) == 1 and isinstance(items[0], HMACData):
            items = items[0]
        digest = hashlib.sha512()
        for i in items:
            digest.update( str(i).encode() )
        self.digest = digest.hexdigest()
        self.c = 0

    def consume_bytes(self, x):
        x *= 2
        r = self.digest[self.c:self.c+x]
        self.c += x
        return int(r, 16)

    def compute_sig(self):
        self.c = 0
        return SigData(*[ self.consume_bytes(SIG_DETAIL[x]) for x in SIG_PLAN ])


class SlurpMixin(object):
    @classmethod
    def slurp(cls, dict_arg):
        try:
            return cls(**{ k: dict_arg[k] for k in cls._fields if k in dict_arg })
        except TypeError as e:
            cfj = ', '.join(cls._fields)
            daj = ', '.join(dict_arg.keys())
            raise TypeError(f'{cls.__name__} requires: {cfj}; received: {daj}') from e


_SigData   = namedtuple('SigData',   SIG_PLAN)
_HMACData  = namedtuple('HMACData',  HMAC_PLAN)
_NonceData = namedtuple('NonceData', NONCE_PLAN)

class HMACData(_HMACData, SlurpMixin): pass
class NonceData(_NonceData, SlurpMixin): pass
class SigData(_SigData, SlurpMixin): pass

del _SigData, _HMACData, _NonceData, SlurpMixin
