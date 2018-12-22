import urllib.parse

from adapters.on_off_switch_adapter import OnOffSwitchAdapter

class DimmableAdapter(OnOffSwitchAdapter):

    def handleMqttMessage(self, device, data, action, domoticz_port):
        if action == 'brightness':
            params = {
                'param': 'switchlight',
                'idx': device['idx'],
                'switchcmd': 'Set Level',
                'level': data
            }
            OnOffSwitchAdapter.callDomoticzApi(self, domoticz_port, urllib.parse.urlencode(params))
        elif action == 'onoff':
            OnOffSwitchAdapter.handleMqttMessage(self, device, data, action, domoticz_port)

    def getTraits(self):
        return [1,2]

