Modified versions of Denon HEOS custom component and underlying control library.
Originally ported from https://github.com/easink/hass.aioheos.media_player and https://github.com/easink/aioheos

- Fixes to custom component and library to properly support multiple HEOS speakers (proper state and updates targeting)
- Added tracing

Configuration example:

```yaml
media_player:
  # HEOS Speakers
  - platform: heos
    speaker_name: Deck              # This must match the speaker name configured via HEOS app
    host: 192.168.2.182 #Speaker_Backyard
    name: HEOS Speaker (Back Yard)
  - platform: heos
    speaker_name: Master Bedroom    # This must match the speaker name configured via HEOS app
    host: 192.168.2.203 #Speaker_MasterBedroom
    name: HEOS Speaker (Master Bedroom)
```
