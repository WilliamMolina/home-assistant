Custom HA component to control Soma Smart Shades (https://www.somasmarthome.com/)

- Shades are only controllable via BLE so this requires a controller setup as per https://github.com/SkyJohn/Homebridge-SOMA-Smart-Shades
- If using HASSOS\HASS.IO on RPi3, the controller would have to be a HASS.IO add-on. I am running it on a separate RPi Zero W

Configuration example:

```yaml
cover:
  # Soma Shades
  - platform: somashades
    controller: 192.168.2.234
    scan_interval: 300
    covers:
      dining_room_shades:
        friendly_name: Dining Room Window Shades
        mac: "F6:2B:75:99:DC:BF"
      living_room_shades:
        friendly_name: Living Room Window Shades
        mac: "D3:09:81:73:66:3D"
```
