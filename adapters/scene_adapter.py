from adapters.on_off_switch_adapter import OnOffSwitchAdapter

class SceneAdapter(OnOffSwitchAdapter):

    def getType(self):
        return 'switchscene'
