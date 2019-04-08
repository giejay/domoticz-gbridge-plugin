from adapters.base_adapter import Adapter
import urllib.parse

class OnOffSwitchAdapter(Adapter):

    def __init__(self):
        Adapter.__init__(self)

    def handleMqttMessage(self, device, data, action, domoticz_port):
        if data == '0':
            command = 'Off'
        else:
            command = 'On'

        params = {
            'param': self.getParamType(),
            'idx': self.determineDeviceId(device),
            'switchcmd': command
        }
        Adapter.callDomoticzApi(self, domoticz_port, urllib.parse.urlencode(params))

    def getBridgeType(self, device):
        if ('TypeImg' in device and (device['TypeImg'] == 'lightbulb' or device['TypeImg'] == 'dimmer')) \
                and 'Image' in device and device['Image'] == 'Light':
            # Light
            return 1
        # Switch
        return 3

    def getParamType(self):
        return 'switchlight'

    def getTraits(self):
        return [1]
    
    def publishStateFromDomoticzTopic(self, mqtt_client, device, base_topic, message):
        self.publishState(mqtt_client, device, base_topic, message['nvalue'])

    def publishState(self, mqtt_client, device, base_topic, value):
        base_topic = base_topic + '/' + str(self.determineDeviceId(device)) + '/onoff/set'
        mqtt_client.Publish(base_topic, value)

    def determineDeviceId(self, device):
        return device['idx']