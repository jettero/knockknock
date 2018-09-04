

from synkk.dmesg import DmesgReader

def test_dmesg():
    dmr = DmesgReader(cmd=['tail', '-f', 't/pretend.log'], wait_timeout=1, read_timeout=1, find_live=False)
    lines = list(dmr)
    # wc -l t/pretend.log
    # 5 t/pretend.log
    assert len(lines) == 5
