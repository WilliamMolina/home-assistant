Modified versions of built-in Wemo switch and light components as well as the pywemo library
- Enable support for Wemo Crock-Pot Slow Cooker
  - Exposes attributes for mode (Warm\Low\High), remaining time and cooked time
  - Adds a service to set mode and cook time
- Retry on failure when trying to connect to Wemo devices during HA startup
- Retry when updating dimmer state
- When Slow Cooker becomes disconnected, ignore it for the first couple of updates in the hope that it reconnects
  
Configuration example:

```yaml
# Belkin WeMo
wemo:
  disable_discovery: true
  static:
    # Breakfast Room light switch
    - 192.168.2.228
    # Crock-Pot Slow Cooker
    - 192.168.2.236
```

Example script to set Slow Cooker mode and cook time based on UI updates (I use input_select for mode and two input_numbers for hours and minutes)

```yaml
# Set Wemo CrockPot Slow Cooker cook time
  set_crockpot_cook_time:
    alias: Cook Timer
    sequence:
      - service: wemo.crockpot_update_settings
        data_template:
          mode: >
            {% if is_state('input_select.crockpot_mode', 'Warm') %}
              50
            {% elif is_state('input_select.crockpot_mode', 'Low') %}
              51
            {% elif is_state('input_select.crockpot_mode', 'High') %}
              52
            {% else %}
              0
            {% endif %}
          time: "{{ states('input_number.crockpot_cook_time_hour')|int * 60 + states('input_number.crockpot_cook_time_minute')|int }}"
```
