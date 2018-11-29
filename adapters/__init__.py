from adapters.dimmable_adapter import DimmableAdapter
from adapters.on_off_switch_adapter import OnOffSwitchAdapter
from adapters.scene_adapter import SceneAdapter

adapter_by_type = {
    'Dimmer': DimmableAdapter(),
    'Blinds Inverted': DimmableAdapter(),
    'Blinds': DimmableAdapter(),
    'Blinds Percentage': DimmableAdapter(),
    'Blinds Percentage Inverted': DimmableAdapter(),
    'On/Off': OnOffSwitchAdapter(),
    'Push On Button': OnOffSwitchAdapter(),
    'Push Off Button': OnOffSwitchAdapter(),
    'Scene': SceneAdapter(),
    'Group': SceneAdapter()
}

def getAdapter(device):
    if 'SwitchType' in device and device['SwitchType'] in adapter_by_type:
        # Specific adapter for this switch type
        return adapter_by_type[device['SwitchType']]
    elif 'Type' in device and device['Type'] in adapter_by_type:
        return adapter_by_type[device['Type']]
    return None
