from adapters.base_adapter import Adapter
import urllib.parse
import Domoticz

#Use of the Thermostat type but giving fake value on unvailable information
class TemperatureSensorAdapter(Adapter):

    def __init__(self):
        Adapter.__init__(self)

    def handleMqttMessage(self, device, data, action, domoticz_port):
        mqtt_client.Publish(topic + '/tempset-mode/set', 'off')
        mqtt_client.Publish(topic + '/tempset-setpoint/set', '0')

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
        topic = topic + '/' + str(message['idx'])
        if message['dtype'] == 'Temp':
            mqtt_client.Publish(topic + '/tempset-ambient/set', str(message['nvalue']))
        elif message['dtype'] == 'Humidity':
            mqtt_client.Publish(topic + '/tempset-humidity/set',str(message['nvalue']))
        elif message['dtype'] == 'Temp + Humidity' or message['dtype'] == 'Temp + Humidity + Baro':
            mqtt_client.Publish(topic + '/tempset-ambient/set', str(message['svalue1']))
            mqtt_client.Publish(topic + '/tempset-humidity/set',str(message['svalue2']))
        else:
            return
        
        # Set thermostat setup or GA won't work
        mqtt_client.Publish(topic + '/tempset-mode/set', 'off')
        mqtt_client.Publish(topic + '/tempset-setpoint/set', '0')
