import Domoticz
import json
import urllib.parse
import urllib.request
from base64 import b64encode
from adapters import adapter_by_type

class gBridgeClient:
    Address = ""
    Username = ""
    Password = ""

    brightness_devices = ['Blinds', 'Blinds Inverted', 'Blinds Percentage', 'Dimmer', 'Blinds Percentage Inverted']

    def __init__(self, address, username, password):
        Domoticz.Debug("gBridgeClient::__init__")
        self.Address = address
        self.Username = username
        self.Password = password

    def syncDevices(self, domoticz_devices_by_name, bridge_devices, delete_removed_devices):
        bridge_devices_by_name = {x['name']: x for x in bridge_devices}

        # Add devices which are not in gBridge yet
        for name, device in domoticz_devices_by_name.items():
            if name not in bridge_devices_by_name:

                if 'SwitchType' in device and device['SwitchType'] in adapter_by_type:
                    # Specific adapter for this switch type
                    adapter = adapter_by_type[device['SwitchType']]
                elif 'Type' in device and device['Type'] in adapter_by_type:
                    # Scenes/Groups have no SwitchType, in that case, check the type
                    adapter = adapter_by_type[device['Type']]
                else:
                    Domoticz.Error('No gBridge adapter found for device: ' + name)
                    continue

                traits = adapter.getTraits()
                type = adapter.getBridgeType(device)
                self.createDevice(name, type, traits)

        # remove devices in gbridge which are no longer in domoticz
        if delete_removed_devices:
            for device in bridge_devices:
                if device['name'] not in domoticz_devices_by_name:
                    self.deleteDevice(device['device_id'])

    def fetchDevicesFromBridge(self):
        url = "%s/api/device" % self.Address
        req = urllib.request.Request(url)
        req.add_header("Authorization", 'Basic %s' % self.getAuthHeader())
        response = urllib.request.urlopen(req).read().decode('utf-8')
        Domoticz.Debug("Fetching all devices from gBridge %s" % response)
        return json.loads(response)

    def deleteDevice(self, id):
        gBridgeUrl = "%s/api/device/%s" % (self.Address, id)
        req = urllib.request.Request(gBridgeUrl, method='DELETE')
        req.add_header("Authorization", 'Basic %s' % self.getAuthHeader())
        response = str(urllib.request.urlopen(req).read())
        Domoticz.Debug('Delete device %s which is no longer in Domoticz, response: %s' % (id, response))
        return response == b'Created'

    def createDevice(self, name, type, traits):
        values = {'name': name, 'type': type, 'traits': traits, 'topicPrefix': name}
        data = json.dumps(values).encode('ascii')
        req = urllib.request.Request("%s/api/device" % self.Address, data)
        req.add_header('Content-Type', 'application/json')
        req.add_header("Authorization", 'Basic %s' % self.getAuthHeader())
        response = str(urllib.request.urlopen(req).read())
        Domoticz.Debug(
            'Try to create device %s for type %s with traits %s, response: %s' % (name, type, str(traits), response))
        return response == b'Created'

    def getAuthHeader(self):
        return b64encode(bytes("%s:%s" % (self.Username, self.Password), 'utf-8')).decode("ascii")
