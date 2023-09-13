#!/usr/bin/python3
import sys
import re
import json

from sonic_py_common import multi_asic
from swsscommon import swsscommon

def onInit():
    global pattern
    global port_alias_mapping
    num_asics = multi_asic.get_namespaces_from_linux()
    port_alias_mapping  = {}
    swsscommon.SonicDBConfig.load_sonic_global_db_config()
    for asic in num_asics:
        cfg_db = multi_asic.connect_config_db_for_ns(asic)
        port_table = cfg_db.get_table('PORT')
        for port, values in port_table.items():
            port_alias_mapping[port] = values['alias']

    pattern = 'Ethernet[\d]+'

def onReceive(msg):
    global pattern
    global port_alias_mapping

    matches = re.findall(pattern, msg)
    found_match = False
    for match in matches:
        if match in port_alias_mapping.keys():
            new_log= re.sub(match, port_alias_mapping[match],msg)
            msg = new_log
            found_match = True
    if found_match:
        print(json.dumps({'msg': new_log}))
    else:
        print(json.dumps({}))

def onExit():
    pass


## source https://github.com/rsyslog/rsyslog/blob/master/plugins/external/messagemod/anon_cc_nbrs/anon_cc_nbrs.py

"""
-------------------------------------------------------
This is plumbing that DOES NOT need to be CHANGED
-------------------------------------------------------
Implementor's note: Python seems to very agressively
buffer stdouot. The end result was that rsyslog does not
receive the script's messages in a timely manner (sometimes
even never, probably due to races). To prevent this, we
flush stdout after we have done processing. This is especially
important once we get to the point where the plugin does
two-way conversations with rsyslog. Do NOT change this!
See also: https://github.com/rsyslog/rsyslog/issues/22
"""
onInit()
keepRunning = 1
while keepRunning == 1:
    msg = sys.stdin.readline()
    if msg:
        msg = msg[:-1] # remove LF
        onReceive(msg)
        sys.stdout.flush() # very important, Python buffers far too much!
    else: # an empty line means stdin has been closed
        keepRunning = 0
onExit()
sys.stdout.flush() # very important, Python buffers far too much!
