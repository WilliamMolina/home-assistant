Originally ported from https://github.com/sean6541/tuya-homeassistant and https://github.com/clach04/python-tuya

Changes from above-mentioned Tuya custom component\pytuya library:
- pytuya: Persistent TCP socket connection (side effect: disables local control via Smart Life app)
- pytuya: Listener thread (1 thread per device) so device updates are immediately reflected in HA
- pytuya: Retries when connecting\re-connecting and updating state
- HA: Support for Oil Diffusers and Humidifiers based on Tuya platform (via TuyaLocal switch custom component)
  - Oil Diffusers: expose mist mode as attribute, add service to set mist mode
  - Humidifiers: expose fog level, led light setting and water low indicator as attributes
- HA: Support for Tuya RGB bulbs and dimmers (via TuyaLocal light custom component)

These changes are very significant modifications for HA custom component and pytuya library and, as such, aren't really mergeable back
to those repos (and vice versa) in any meaningful way.<br/><br/>
The changes also disable support for tuya devices with multiple switches (e.g. power strips, 2-socket devices, etc) primarily because
I didn't bother maintaining that functionality since I don't have any such devices.

Configuration example:

```yaml
switch:
  # Tuya locally controlled devices using a custom component
  - platform: tuyalocal
    host: 192.168.2.196 #OilDiffuser_Kitchen
    local_key: 2c63a66368cc6df9
    device_id: 02200353b4e62d06dd2e
    device_type: diffuser
    name: Kitchen Essential Oil Diffuser
  - platform: tuyalocal
    host: 192.168.2.186 #FanSwitch_MasterBathroom
    local_key: 523bba09803080eb
    device_id: 42514300b4e62d1e2fc0
    name: Master Bathroom Fan
    
light:
  # Tuya locally controlled devices using a custom component
  - platform: tuyalocal
    host: 192.168.2.117 #LightSwitch_NathanRoom
    local_key: 61b31e67dda1b51f
    device_id: 07200079bcddc2eff8b1
    device_type: dimmer
    name: Nathan Room Lights
  - platform: tuyalocal
    host: 192.168.2.145 #TUYA_Bulb_Office1
    local_key: ba755a9b44bfb315
    device_id: 88272017ecfabc1e3e95
    device_type: bulb
    name: Office Lamp 1
```

Automation example to set mist mode:

```yaml
- alias: Turn on Kitchen oil diffuser at 6pm
  trigger:
    platform: time
    at: '18:00:00'
  action:
    - service: switch.turn_on
      entity_id: switch.kitchen_essential_oil_diffuser
    # set it to intermittent mist mode
    - service: tuyalocal.set_diffuser_mist_mode
      data:
        entity_id: switch.kitchen_essential_oil_diffuser
        mode: 'intermittent'    # Can also be 'continuous' or 'off'
```
