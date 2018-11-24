from adapters.base_adapter import Adapter
import urllib.parse

class OnOffSwitchAdapter(Adapter):

    def __init__(self):
        Adapter.__init__(self)

    def handleMqttMessage(self, device_id, data, domoticz_port):
        if data == '1':
            command = 'On'
        else:
            command = 'Off'

        params = {
            'param': self.getType(),
            'idx': device_id,
            'switchcmd': command
        }
        Adapter.callDomoticzApi(self, domoticz_port, urllib.parse.urlencode(params))

    def getType(self):
        return 'switchlight'
