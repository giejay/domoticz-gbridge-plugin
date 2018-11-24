from adapters.base_adapter import Adapter
import urllib.parse

class DimmableAdapter(Adapter):

    def handleMqttMessage(self, device_id, data, domoticz_port):
        params = {
            'param': 'switchlight',
            'idx': device_id,
            'switchcmd': 'Set Level',
            'level': data
        }
        Adapter.callDomoticzApi(self, domoticz_port, urllib.parse.urlencode(params))