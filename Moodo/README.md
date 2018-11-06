Custom HA component to control Moodo Aroma Diffusers (https://moodo.co/)

- Exposes all Aroma Diffusers associated with the account as lights (brigthness controls main fan volume)
- When turned OFF, the device stays ON but the speed for all fans is set to 0 (not turning the device off seems to help
with keeping the devices connected for longer periods of time... They still disconnect sometimes requiring a manual power-cycle)
- API token can be obtained via https://rest.moodo.co/

Configuration example:

```yaml
light:
  - platform: moodo
    api_token: XXXXXXX       # Obtain token via https://rest.moodo.co/
```
