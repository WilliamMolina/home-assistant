Originally ported from https://github.com/sean6541/tuya-homeassistant and https://github.com/clach04/python-tuya

Changes from above-mentioned Tuya custom component\pytuya library:
- pytuya: Persistent TCP socket connection (side effect: disables local control via Smart Life app)
- pytuya: Listener thread (1 thread per device) so device updates are immediately reflected in HA
- pytuya: Retries when connecting\re-connecting and updating state
- HA: Support for Oil Diffusers and Humidifiers based on Tuya platform (via TuyaLocal switch custom component)
- HA: Support for Tuya RGB bulbs and dimmers (via TuyaLocal light custom component)

These changes are very significant modifications for HA custom component and pytuya library and, as such, aren't really mergeable back
to those repos (and vice versa) in any meaningful way.<br/><br/>
The changes also disable support for tuya devices with multiple switches (e.g. power strips, 2-socket devices, etc) primarily because
I didn't bother maintaining that functionality since I don't have any such devices.
