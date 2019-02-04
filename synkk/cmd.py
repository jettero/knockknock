# encoding: utf-8

import subprocess
import random, os, sys
import click
import click_config_file
from synkk.sig import compute_sig
from synkk.config import Provider

HPING = '{prefix} hping3 -c 1 --syn --win {win} --setack {ack} ' \
'--setseq {seq} {target} -p {port} --id {nonce}'

def gencmd(secret, target='localhost', port=22, prefix=''):
    args = compute_sig(
        prefix=prefix,
        target=target,
        port=port,
        dpt=port,
        nonce=random.randint(0,0xffff),
        secret=secret,
    )
    formatted = HPING.format(**args)
    r = [ x.strip() for x in formatted.split() ]
    return r[0], r

@click.command()
@click.option('-g', '--go-host', is_flag=True, default=False)
@click.option('-d', '--dry-run', is_flag=True, default=False)
@click.option('--version',       is_flag=True, default=False)
@click.option('-h', '--host', type=str, prompt=True)
@click.option('-s', '--secret', type=click.Path(dir_okay=False), prompt=True)
@click.option('-p', '--port', type=click.IntRange(0,0xffff), default=22)
@click_config_file.configuration_option(
    config_file_name=os.path.expanduser('~/.synkk.conf'),
    provider=Provider())
@click.argument('post', nargs=-1)
def synkk(host,port,secret,dry_run,go_host,post, version):
    if version:
        from synkk.version import version as vstr
        print(f'{vstr}')
        sys.exit(0)
    # setup
    dpt = port
    prefix = ''
    if dry_run:
        prefix = 'echo'
    elif os.getuid() > 0:
        prefix = 'sudo'

    if go_host:
        post = ['ssh', host] + list(post)

    cmd, args = gencmd(secret,host,dpt, prefix)
    if not post:
        # we're just doing the ping
        os.execvp( cmd, args )
        sys.exit(1)

    # ping first
    proc = subprocess.Popen(args)
    proc.communicate()

    if not dry_run:
        print('\n')

    # then deal with the post command
    args = post
    if dry_run:
        args = ['echo'] + list(args)
    cmd = args[0]
    os.execvp( cmd, args )
    sys.exit(1)

def cli():
    synkk(auto_envvar_prefix='SYNKK')
