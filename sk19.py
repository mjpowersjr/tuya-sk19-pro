#!/usr/bin/env python3
"""Local control for the SK19 Pro. Usage:
  sk19.py status
  sk19.py set <dp> <value>     value parsed as JSON if possible (true, 40, "36")
"""
import json, sys, tinytuya

c = json.load(open(__file__.rsplit("/", 1)[0] + "/device.json"))
d = tinytuya.Device(c["id"], c["ip"], c["local_key"], version=3.5)
d.set_socketTimeout(5)

cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
if cmd == "status":
    print(json.dumps(d.status(), indent=2))
elif cmd == "set":
    raw = sys.argv[3]
    try:
        val = json.loads(raw)
    except ValueError:
        val = raw
    print(json.dumps(d.set_value(int(sys.argv[2]), val), indent=2))
else:
    sys.exit(__doc__)
