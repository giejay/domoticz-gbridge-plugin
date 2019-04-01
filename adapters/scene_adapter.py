from adapters.on_off_switch_adapter import OnOffSwitchAdapter

class SceneAdapter(OnOffSwitchAdapter):

    def getBridgeType(self, device):
        return 4

    def getTraits(self):
        return [3]

    def getParamType(self):
        return 'switchscene'
    
    def publishState(self, mqtt_client, device, topic, message):
        #no state on scene, each device is updated if in the gbridge base
        return
