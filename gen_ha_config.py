"""Generate the tuya-local device config for the SK19 Pro from projections.json."""
import json

proj = json.load(open("projections.json"))
light = json.load(open("lighting_scenes.json"))
assert len({p["name"] for p in proj}) == len(proj), "projection names must be unique"

head = '''name: Projector light
products:
  # cloud product id (Tuya IoT Platform / Smart Life app)
  - id: a5enoboa4fnkicus
    manufacturer: Tuya
    model: Smart 3D Video Projector Light (SK19 Pro)
  # product id the device itself reports on the LAN (seen in Tuya Local's discovery warning)
  - id: fx1h9mjhadi9mytv
    manufacturer: Tuya
    model: Smart 3D Video Projector Light (SK19 Pro)
entities:
  - entity: switch
    name: Master
    dps:
      - id: 20
        type: boolean
        name: switch
  - entity: light
    name: Colour
    icon: "mdi:palette"
    dps:
      - id: 52
        type: boolean
        name: switch
      - id: 24
        name: rgbhsv
        type: hex
        format:
          - name: h
            bytes: 2
            range:
              min: 0
              max: 360
          - name: s
            bytes: 2
            range:
              min: 0
              max: 1000
          - name: v
            bytes: 2
            range:
              min: 10
              max: 1000
  - entity: switch
    name: Projection
    icon: "mdi:movie-open"
    dps:
      - id: 105
        type: boolean
        name: switch
  - entity: number
    name: Projection brightness
    icon: "mdi:brightness-6"
    dps:
      - id: 106
        type: integer
        name: value
        range:
          min: 0
          max: 100
  - entity: switch
    name: Play
    icon: "mdi:play-pause"
    dps:
      - id: 107
        type: boolean
        name: switch
  - entity: switch
    name: Sound
    icon: "mdi:volume-high"
    dps:
      - id: 108
        type: boolean
        name: switch
  - entity: number
    name: Volume
    icon: "mdi:volume-medium"
    dps:
      - id: 109
        type: integer
        name: value
        range:
          min: 0
          max: 100
  - entity: switch
    name: Bluetooth
    icon: "mdi:bluetooth"
    dps:
      - id: 111
        type: boolean
        name: switch
  - entity: binary_sensor
    name: Bluetooth connected
    class: connectivity
    dps:
      - id: 120
        type: string
        name: sensor
        mapping:
          - dps_val: connect
            value: true
          - dps_val: disconnect
            value: false
  - entity: select
    name: Playback order
    icon: "mdi:shuffle-variant"
    dps:
      - id: 112
        type: string
        name: option
        mapping:
          - dps_val: sequence
            value: Sequence
          - dps_val: random
            value: Random
          - dps_val: single_cycle
            value: Single cycle
  - entity: button
    name: Next
    icon: "mdi:skip-next"
    dps:
      - id: 125
        type: string
        name: button
        optional: true
        mapping:
          - dps_val: next
            value: true
  - entity: button
    name: Previous
    icon: "mdi:skip-previous"
    dps:
      - id: 125
        type: string
        name: button
        optional: true
        mapping:
          - dps_val: previous
            value: true
  - entity: select
    name: Colour scene
    icon: "mdi:palette-swatch"
    dps:
      - id: 121
        type: integer
        name: option
        mapping:
LIGHT_SCENES
  - entity: select
    name: Projection scene
    icon: "mdi:movie-open-play"
    dps:
      - id: 122
        type: string
        name: option
        mapping:
'''
body = "".join(f'          - dps_val: "{p["code"]}"\n            value: "{p["name"]}"\n' for p in proj)
lbody = "".join(f'          - dps_val: {l["code"]}\n            value: "{l["name"]}"\n' for l in light)
head = head.replace("LIGHT_SCENES\n", lbody)
open("ha/sk19_pro_projector.yaml", "w").write(head + body)
print("wrote ha/sk19_pro_projector.yaml with", len(proj), "scenes")
