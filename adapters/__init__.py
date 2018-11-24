from adapters.dimmable_adapter import DimmableAdapter
from adapters.on_off_switch_adapter import OnOffSwitchAdapter
from adapters.scene_adapter import SceneAdapter

adapter_by_type = {
    'brightness': {
        'Default': DimmableAdapter()
    },
    'onoff': {
        'Default': OnOffSwitchAdapter(),
        'Scene': SceneAdapter(),
        'Group': SceneAdapter()
    }
}
