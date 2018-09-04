# coding: utf-8

import yaml
import pytest

@pytest.fixture
def log_entries():
    fnames = ('t/log-entries.yaml', 'log-entries.yaml')
    for fname in fnames:
        try:
            with open(fname, 'r') as fh:
                return yaml.safe_load(fh)
        except FileNotFoundError:
            continue
    raise FileNotFoundError("couldn't find the log entries :-(")
