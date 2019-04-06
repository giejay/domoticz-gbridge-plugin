from adapters.base_adapter import Adapter
import urllib.parse
import Domoticz

class TemperatureAdapter(Adapter):

    def __init__(self):
        Adapter.__init__(self)

    def handleMqttMessage(self, device, data, action, domoticz_port):
        if action == 'tempset-setpoint':
            data = self.get_temperature(data, device)
            params = {
                'param': 'udevice',
                'idx': device['idx'],
                'nvalue': '0',
                'svalue': data
            }
            Adapter.callDomoticzApi(self, domoticz_port, urllib.parse.urlencode(params))
        else:
            Domoticz.Debug('Action: %s not supported yet for thermostat' % action)

    def get_temperature(self, data, device):
        parsed_temp = float(data)
        if parsed_temp < 5:
            # assume that its an increase or decrease
            data = float(device['Data']) + parsed_temp
        return data

    def getBridgeType(self, device):
        return 5

    def getTraits(self):
        return [4]

    def publishState(self, mqtt_client, device, topic, message):
        if 'svalue1' in message:
            temp = self.get_temperature(message['svalue1'], device)
            topic = topic + '/' + str(message['idx'])
            mqtt_client.Publish(topic + '/tempset-ambient/set', temp)
            mqtt_client.Publish(topic + '/tempset-setpoint/set', temp)
