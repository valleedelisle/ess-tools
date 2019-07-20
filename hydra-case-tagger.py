#!/usr/bin/env python3
# encoding: utf-8
#
# Description: Set the tags for cases 
#
# Copyright (C) 2018 David Vallee Delisle (dvd@redhat.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import os
import requests
import datetime
import persistent.dict
import argparse
import unicodedata
import re
from collections import defaultdict

def args_case_id(s, pat=re.compile(r"^0[1-9][0-9]{6}$")):
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s

parser = argparse.ArgumentParser()
# Logging options
parser.add_argument("--debug", action="store_true", help="Display debug information")
parser.add_argument("--log", default=None, help="Log file")

# Filtering options
parser.add_argument("--case-id", type=args_case_id, help="Case ID to tag")
parser.add_argument("--tags", nargs="+", help="Tag(s) to add")
args = parser.parse_args()
tags = [t.replace('\r', '') for t in args.tags]

from lib.log import Log
log = Log(debug = args.debug, log_file = args.log)
from lib.hydra import Hydra

log.debug(vars(args))

def main():
    log.debug("Case ID: {0} Data: {1}".format(args.case_id, tags))

    hydra = Hydra()
    hydra.set_tags(args.case_id, tags)

if __name__ == "__main__":
    main()
