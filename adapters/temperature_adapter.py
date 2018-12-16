from adapters.base_adapter import Adapter
import urllib.parse
import Domoticz

class TemperatureAdapter(Adapter):

    def __init__(self):
        Adapter.__init__(self)

    def handleMqttMessage(self, device, data, action, domoticz_port):
        if action == 'tempset-setpoint':
            parsed_temp = float(data)
            if parsed_temp < 5:
                # assume that its an increase or decrease
                data = float(device['Data']) + parsed_temp
            params = {
                'param': 'udevice',
                'idx': device['idx'],
                'nvalue': '0',
                'svalue': data
            }
            Adapter.callDomoticzApi(self, domoticz_port, urllib.parse.urlencode(params))
        else:
            Domoticz.Debug('Action: %s not supported yet for thermostat' % action)

    def getBridgeType(self, device):
        return 5

    def getTraits(self):
        return [4]
