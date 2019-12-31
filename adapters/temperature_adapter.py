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

    def publishState(self, mqtt_client, device, base_topic, value):
        temp = self.get_temperature(value, device)
        device_topic = base_topic + '/' + str(device['idx'])
        mqtt_client.Publish(device_topic + '/tempset-ambient/set', temp)
        mqtt_client.Publish(device_topic + '/tempset-setpoint/set', temp)

    def publishStateFromDomoticzTopic(self, mqtt_client, device, base_topic, message):
        device_topic = base_topic + '/' + str(device['idx'])
        if message['dtype'] == 'Thermostat':
            mqtt_client.Publish(device_topic + '/tempset-setpoint/set', message['svalue1'])
        elif message['dtype'] == 'Temp':
            if message.get('svalue1') is not None: 
                mqtt_client.Publish(device_topic + '/tempset-ambient/set', str(message['svalue1']))
            else:
                mqtt_client.Publish(device_topic + '/tempset-ambient/set', str(message['nvalue']))
        elif message['dtype'] == 'Humidity':
            mqtt_client.Publish(device_topic + '/tempset-humidity/set', str(message['nvalue']))
        elif message['dtype'] == 'Temp + Humidity':
            mqtt_client.Publish(device_topic + '/tempset-ambient/set', str(message['svalue1']))
            mqtt_client.Publish(device_topic + '/tempset-humidity/set', str(message['svalue2']))
