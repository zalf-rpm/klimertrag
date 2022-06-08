#!/usr/bin/python
# -*- coding: UTF-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file is part of the util library used by models created at the Institute of
# Landscape Systems Analysis at the ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import capnp
import os
from pathlib import Path
import time
import sys

PATH_TO_REPO = Path(os.path.realpath(__file__)).parent.parent
if str(PATH_TO_REPO) not in sys.path:
    sys.path.insert(1, str(PATH_TO_REPO))

PATH_TO_PYTHON_CODE = PATH_TO_REPO / "../mas-infrastructure/src/python"
if str(PATH_TO_PYTHON_CODE) not in sys.path:
    sys.path.insert(1, str(PATH_TO_PYTHON_CODE))

import common.common as common

PATH_TO_CAPNP_SCHEMAS = (PATH_TO_REPO / "../mas-infrastructure/capnproto_schemas").resolve()
abs_imports = [str(PATH_TO_CAPNP_SCHEMAS)]
common_capnp = capnp.load(str(PATH_TO_CAPNP_SCHEMAS / "common.capnp"), imports=abs_imports) 
x_capnp = capnp.load("bgr_flow_components/x.capnp", imports=abs_imports) 

#------------------------------------------------------------------------------

config = {
    "name": "_",
    "in_sr": None, # string
}
common.update_config(config, sys.argv, print_config=True, allow_new_keys=False)

conman = common.ConnectionManager()
inp = conman.try_connect(config["in_sr"], cast_as=common_capnp.Channel.Reader, retry_secs=1)

try:
    if inp:
        count = 42
        with open(config["name"]+".out", "w") as out:
            while True:
                msg = inp.read().wait()
                # check for end of data from in port
                if msg.which() == "done":
                    break
                
                #x = msg.value.as_interface(x_capnp.X)
                x = msg.value.as_struct(x_capnp.S).c
                res = "{}: x.m({}) -> {}\n".format(config["name"], count, x.m(count).wait())
                out.write(res)
                #print(config["name"],": x.m(", count, ") ->", x.m(count).wait())
                count += 1

                #time.sleep(1)

except Exception as e:
    print("c.py ex:", e)

print("c.py: exiting run")

