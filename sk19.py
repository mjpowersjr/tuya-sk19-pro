#!/usr/bin/env python3
"""Local control for the SK19 Pro. Usage:
  sk19.py status
  sk19.py set <dp> <value>     value parsed as JSON if possible (true, 40, "36")
Config: see sk19conf.py / sk19.example.toml.
"""
import json, sys
import tinytuya
from sk19conf import load

c = load()
d = tinytuya.Device(c["device_id"], c["host"], c["local_key"], version=c["version"])
d.set_socketTimeout(5)

cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
if cmd == "status":
    print(json.dumps(d.status(), indent=2))
elif cmd == "set":
    try:
        val = json.loads(sys.argv[3])
    except ValueError:
        val = sys.argv[3]
    print(json.dumps(d.set_value(int(sys.argv[2]), val), indent=2))
else:
    sys.exit(__doc__)
