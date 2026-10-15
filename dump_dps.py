"""Probe protocol versions and dump data points."""
import json, tinytuya
from sk19conf import load

c = load()
for v in (3.5, 3.4, 3.3, 3.2, 3.1):
    d = tinytuya.Device(c["device_id"], c["host"], c["local_key"], version=v)
    d.set_socketTimeout(5); d.set_socketRetryLimit(1)
    r = d.status()
    print(v, "->", json.dumps(r)[:600])
    if r and "dps" in r:
        print("WORKING VERSION", v); break
