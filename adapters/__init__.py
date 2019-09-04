from adapters.dimmable_adapter import DimmableAdapter
from adapters.on_off_switch_adapter import OnOffSwitchAdapter
from adapters.scene_adapter import SceneAdapter
from adapters.temperature_adapter import TemperatureAdapter
from adapters.temperature_sensor_adapter import TemperatureSensorAdapter

adapter_by_type = {
    'Dimmer': DimmableAdapter(),
    'Blinds Inverted': DimmableAdapter(),
    'Blinds': DimmableAdapter(),
    'Blinds Percentage': DimmableAdapter(),
    'Blinds Percentage Inverted': DimmableAdapter(),
    'On/Off': OnOffSwitchAdapter(),
    'Push On Button': OnOffSwitchAdapter(),
    'Push Off Button': OnOffSwitchAdapter(),
    'Selector': OnOffSwitchAdapter(),
    'Scene': SceneAdapter(),
    'Group': SceneAdapter(),
    'Thermostat': TemperatureAdapter(),
    'Door Lock': OnOffSwitchAdapter(),
    'Temp': TemperatureSensorAdapter(),
    'Temp + Humidity':TemperatureSensorAdapter(),
    'Temp + Humidity + Baro':TemperatureSensorAdapter()
}

def getAdapter(device):
    if 'SwitchType' in device and device['SwitchType'] in adapter_by_type:
        # Specific adapter for this switch type
        return adapter_by_type[device['SwitchType']]
    elif 'Type' in device and device['Type'] in adapter_by_type:
        return adapter_by_type[device['Type']]
    return None
