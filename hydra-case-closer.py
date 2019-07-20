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
import argparse
import unicodedata
import re
from collections import defaultdict

def args_case_id(s, pat=re.compile(r"^0[1-9][0-9]{6}$")):
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s
def args_status(s, pat=re.compile(r"^Waiting on (Red Hat|Customer)$|^Closed$")):
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s
def args_internal_status(s, pat=re.compile(r"^Waiting on (Owner|Customer|Collaboration|Engineering)$|^Closed$")):
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s



parser = argparse.ArgumentParser()
# Logging options
parser.add_argument("--debug", action="store_true", help="Display debug information")
parser.add_argument("--log", default=None, help="Log file")

# Filtering options
parser.add_argument("--relief", action="store_true", help="Provide relief")
parser.add_argument("--resolve", action="store_true", help="Provide resolution")
parser.add_argument("--case-id", type=args_case_id, help="Case ID to tag")
parser.add_argument("--status", type=args_status, help="Status")
parser.add_argument("--internal-status", type=args_internal_status, help="Internal Status")
parser.add_argument("--resolution", default="Resolved: Answer Provided", help="Resolved: Answer Provided")
parser.add_argument("--resolution-description", default="Case closed automatically (massive close of the new year)", help="Resolution description")

args = parser.parse_args()

from lib.log import Log
log = Log(debug = args.debug, log_file = args.log)
from lib.hydra import Hydra

log.debug(vars(args))

def main():
    log.debug("Case ID: {0} Data: {1}".format(args.case_id, args.status, args.internal_status))

    hydra = Hydra()
    hydra.setStatus(args.case_id, args.status, args.internal_status, args.relief, args.resolve, args.resolution, args.resolution_description)

if __name__ == "__main__":
    main()
