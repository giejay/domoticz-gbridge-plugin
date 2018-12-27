import Domoticz
import json
import urllib.parse
import urllib.request
from base64 import b64encode
from urllib.error import URLError, HTTPError
from json import JSONDecodeError
from adapters import getAdapter


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
                adapter = getAdapter(device)
                if adapter is None:
                    Domoticz.Error('No gBridge adapter found for device: ' + str(device))
                    continue

                traits = adapter.getTraits()
                type = adapter.getBridgeType(device)
                self.createDevice(name, type, traits, device['idx'])

        # remove devices in gbridge which are no longer in domoticz
        if delete_removed_devices:
            for device in bridge_devices:
                if device['name'] not in domoticz_devices_by_name:
                    self.deleteDevice(device['device_id'])

    def fetchDevicesFromBridge(self):
        url = "%s/api/device" % self.Address
        req = urllib.request.Request(url)
        req.add_header("Authorization", 'Basic %s' % self.getAuthHeader())
        try:
            return json.loads(self.callAPI(req, 'Fetching all devices from gBridge'))
        except JSONDecodeError as e:
            Domoticz.Error('Could not decode JSON due to: %s, json: %s' % (e.msg, e.doc))
            raise e

    def deleteDevice(self, id):
        gBridgeUrl = "%s/api/device/%s" % (self.Address, id)
        req = urllib.request.Request(gBridgeUrl, method='DELETE')
        req.add_header("Authorization", 'Basic %s' % self.getAuthHeader())
        return self.callAPI(req, 'Delete device %s' % id) == 'Created'

    def callAPI(self, request, action):
        try:
            Domoticz.Debug('Calling API for action: %s, url: %s' % (action, str(request.get_full_url())))
            response = urllib.request.urlopen(request).read().decode('utf-8')
        except HTTPError as e:
            Domoticz.Error('The server couldn\'t fulfill the request: %s.' % action)
            Domoticz.Error('Error code: %d, reason: %s' % (e.code, e.reason))
            raise
        except URLError as e:
            Domoticz.Error('We failed to reach a server.')
            Domoticz.Error('Reason: %s' % e.reason)
            raise
        else:
            Domoticz.Debug('Successfully executed action: %s, response: %s' % (action, response))
            return response

    def createDevice(self, name, type, traits, id):
        values = {'name': name, 'type': type, 'traits': traits, 'topicPrefix': id}
        data = json.dumps(values).encode('ascii')
        req = urllib.request.Request("%s/api/device" % self.Address, data)
        req.add_header('Content-Type', 'application/json')
        req.add_header("Authorization", 'Basic %s' % self.getAuthHeader())
        return self.callAPI(req, 'Try to create device %s for type %s with traits %s' % (name, type, str(traits)))

    def getAuthHeader(self):
        return b64encode(bytes("%s:%s" % (self.Username, self.Password), 'utf-8')).decode("ascii")
