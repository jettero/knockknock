#!/usr/bin/env python
# encoding: utf-8

import random, os
import click
import click_config_file
from synkk.sig import compute_sig

HPING = '''{prefix} hping3 -c 1 --syn --baseport {spt} --win {win}
        --setack {ack} --setseq {seq} {target} -p {port} --id {id}'''

def gencmd(secret, target='localhost', port=22, prefix=''):
    args = compute_sig(
        prefix=prefix,
        target=target,
        port=port,
        dpt=port,
        spt=random.randint(0,0xffff),
        secret=secret,
    )
    formatted = HPING.format(**args)
    r = [ x.strip() for x in formatted.split() ]
    return r[0], r

@click.command()
@click.option('-d', '--dry-run', is_flag=True, default=False)
@click.option('-h', '--host', type=str, prompt=True)
@click.option('-s', '--secret', type=click.Path(dir_okay=False), prompt=True)
@click.option('-p', '--port', type=click.IntRange(0,0xffff), default=22)
@click_config_file.configuration_option(
    config_file_name=os.path.expanduser('~/.synkk.conf'),
    provider=click_config_file.configobj_provider(False,'synkk'))
def synkk(host,port,secret,dry_run):
    dpt = port
    prefix = ''
    if dry_run:
        prefix = 'echo'
    elif os.getuid() > 0:
        prefix = 'sudo'
    cmd, args = gencmd(secret,host,dpt, prefix)
    os.execvp( cmd, args )

def cli():
    synkk(auto_envvar_prefix='SYNKK')
