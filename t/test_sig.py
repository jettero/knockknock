
from synkk.sig import (
    Sig, HMACData, SigData, NonceData,
    SIG_PLAN, HMAC_PLAN, NONCE_PLAN,
    compute_sig, compare_sig
)

various_values = {
    'nonce': 1, 'dpt': 2, 'secret': 'testing',
    'spurious': "value shouldn't matter at all",
    'ack': 3, 'win': 7, 'seq': 0xfff
}

def test_compute_sig():
    kw = compute_sig(nonce=3, dpt=4, secret='ohdang', something_else='ja')
    assert kw['nonce'] == 3
    assert kw['dpt'] == 4
    assert kw['secret'] == 'ohdang'
    assert kw['something_else'] == 'ja'
    assert 'ack' in kw
    assert 'win' in kw
    assert 'seq' in kw

def test_compare_sig():
    kw1 = compute_sig(nonce=3, dpt=4, secret='ohdang')
    kw2 = compute_sig(**kw1)
    assert compare_sig(**kw1) is True
    assert compare_sig(**kw2) is True
    kwf = kw1.copy()
    kwf['secret'] = 'fail'
    assert compare_sig(**kwf) is False
    kwf = kw1.copy()
    kwf['nonce'] = 6
    assert compare_sig(**kwf) is False
    kws = kw1.copy()
    assert compare_sig(**kws) is True

def test_sig():
    sig = Sig('blither', 'blather')
    # echo -n 'blitherblather' | sha512sum
    # 67282d6fa0e647635c2c7dd2a0d04295
    # c4626a2d354849f7fe40f51e30b0b2fa
    # 7cd40480d0f7576c31e872db261a0f1e
    # 7cc8abaaa82ccb55d5da5bca06ce98be

    # 67 28.2d 6f.a0.e6 4763.5c2c
    assert sig.consume_bytes(1) == 0x67
    assert sig.consume_bytes(2) == 0x282d
    assert sig.consume_bytes(3) == 0x6fa0e6
    assert sig.consume_bytes(4) == 0x47635c2c

def test_hmac():
    hd = HMACData.slurp(various_values)
    assert hd.nonce    == various_values['nonce']
    assert hd.dpt    == various_values['dpt']
    assert hd.secret == various_values['secret']

    for v,k in zip(hd, HMAC_PLAN):
        assert v == various_values[k]

def test_sig_data():
    sd = SigData.slurp(various_values)
    assert sd.ack == various_values['ack']
    assert sd.win == various_values['win']
    assert sd.seq == various_values['seq']

    for v,k in zip(sd, SIG_PLAN):
        assert v == various_values[k]

def test_nonce_data():
    nd = NonceData.slurp(various_values)
    assert nd.nonce == various_values['nonce']

    for v,k in zip(nd, NONCE_PLAN):
        assert v == various_values[k]
