import urllib.parse

from adapters.base_adapter import Adapter

class DimmableAdapter(Adapter):

    def handleMqttMessage(self, device_id, data, domoticz_port):
        params = {
            'param': 'switchlight',
            'idx': device_id,
            'switchcmd': 'Set Level',
            'level': data
        }
        Adapter.callDomoticzApi(self, domoticz_port, urllib.parse.urlencode(params))

    def getTraits(self):
        return [1,2]

    def getBridgeType(self, device):
        return 1

