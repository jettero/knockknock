#!/usr/bin/env python
# encoding: utf-8

import time
import click
import click_config_file
import logging
from synkk.groklog import GrokLog
from synkk.dmesg   import DmesgReader
from synkk.sig     import compare_sig
from synkk.config  import Provider

# this "daemon" doesn't actually fork/fork/chdir
# it's meant to run from systemd

class NonceRing(list):
    maxsize = 100
    def append(self, item):
        super(NonceRing,self).append(item)
        while len(self) > self.maxsize:
            self.pop(0)

@click.command()
@click.option('-l', '--log-level',
    type=click.Choice(['debug','info','error']), default='info')
@click.option('-s', '--secret', type=click.Path(dir_okay=False), prompt=True)
@click.option('-x', '--xt-recent-file', default='/proc/net/xt_recent/synkk')
@click_config_file.configuration_option(
    config_file_name='/etc/synkk.conf',
    provider=Provider())
def dmesg_daemon_cmd(secret,xt_recent_file,log_level):
    logging.basicConfig(level=log_level.upper(),
        datefmt='%Y-%m-%d %H:%M:%S',
        format='{%(name)s} %(levelname)s: %(message)s')
    log = logging.getLogger('synkk:daemon')
    log.info(f"started logging at level={logging.getLevelName(logging.root.level)}")

    dmr = DmesgReader()
    nonces = NonceRing()
    while True:
        time.sleep(0.5)
        try:
            for line in dmr:
                gl = GrokLog(line)
                if gl.passed:
                    if gl.nonce in nonces:
                        log.info(f'{gl.src} nonce repetition')
                        continue
                    if compare_sig(secret=secret, **gl.as_dict):
                        nonces.append(gl.nonce)
                        issue = f'+{gl.src}'
                        log.info(f'issuing {issue} to {xt_recent_file} (nonce: {gl.nonce})')
                        with open(xt_recent_file, 'w') as fh:
                            fh.write(issue)
                    else:
                        log.info(f'{gl.src} signature failure')
        except Exception as e:
            log.error("exception during dmesg mainlop (follows)")
            log.exception(e)

def cli():
    dmesg_daemon_cmd(auto_envvar_prefix='SYNKK')
