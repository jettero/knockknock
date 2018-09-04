# coding: utf-8

from synkk.groklog import GrokLog

def test_logs(log_entries):
    for ent in log_entries:
        gl = GrokLog(ent['line'], log_prefix='SYNKK', age_reject=False)
        md = ent.get('mdat')
        assert bool(gl.understood) == bool(md)
        assert bool(gl.passed)     == bool(md and 'SYNKK' in ent['line'])

        if gl.passed:
            for k,v in md.items():
                assert getattr(gl, k) == v
