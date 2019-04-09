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
        elif action == 'colorsettingrgb':
            params = {
                'param': 'setcolbrightnessvalue',
                'idx': device['idx'],
                'hex': data
            }
            OnOffSwitchAdapter.callDomoticzApi(self, domoticz_port, urllib.parse.urlencode(params))

    def getTraits(self):
        return [1, 2, 12]

    def publishStateFromDomoticzTopic(self, mqtt_client, device, base_topic, message):
        OnOffSwitchAdapter.publishStateFromDomoticzTopic(self, mqtt_client, device, base_topic, message)
        base_topic = base_topic + '/' + str(message['idx'])
        if message.get('svalue1') is not None:
            mqtt_client.Publish(base_topic + '/brightness/set', str(message['svalue1']))
        if message.get('Color') is not None:
            rgb_color = message['Color']
            color = '%02x%02x%02x' % (rgb_color['r'], rgb_color['g'], rgb_color['b'])
            mqtt_client.Publish(base_topic + '/colorsettingrgb/set', color)

    def publishState(self, mqtt_client, device, base_topic, value):
        OnOffSwitchAdapter.publishState(self, mqtt_client, device, base_topic, value)
        # todo check how to set the brightness next to on/off
