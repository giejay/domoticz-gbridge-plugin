from adapters.base_adapter import Adapter
import urllib.parse

class TemperatureAdapter(Adapter):

    def __init__(self):
        Adapter.__init__(self)

    def handleMqttMessage(self, device_id, data, domoticz_port):
        params = {
            'param': 'udevice',
            'idx': device_id,
            'nvalue': '0',
            'svalue': data
        }
        Adapter.callDomoticzApi(self, domoticz_port, urllib.parse.urlencode(params))

    def getBridgeType(self, device):
        return 5

    def getTraits(self):
        return [5]
