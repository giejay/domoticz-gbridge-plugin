from adapters.on_off_switch_adapter import OnOffSwitchAdapter

class SceneAdapter(OnOffSwitchAdapter):

    def getBridgeType(self, device):
        return 4

    def getTraits(self):
        return [3]

    def getParamType(self):
        return 'switchscene'
