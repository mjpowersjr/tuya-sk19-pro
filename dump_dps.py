import json, sys, tinytuya
c = json.load(open("device.json"))
for v in (3.5, 3.4, 3.3, 3.2, 3.1):
    d = tinytuya.Device(c["id"], c["ip"], c["local_key"], version=v)
    d.set_socketTimeout(5); d.set_socketRetryLimit(1)
    r = d.status()
    print(v, "->", json.dumps(r)[:600])
    if r and "dps" in r:
        print("WORKING VERSION", v); break
