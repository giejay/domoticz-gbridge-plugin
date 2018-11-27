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
