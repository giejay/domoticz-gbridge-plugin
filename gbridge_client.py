import json
import urllib.parse
import urllib.request
from json import JSONDecodeError
from urllib.error import URLError, HTTPError

import Domoticz

from adapters import getAdapter


class gBridgeClient:
    Address = ""

    brightness_devices = ['Blinds', 'Blinds Inverted', 'Blinds Percentage', 'Dimmer', 'Blinds Percentage Inverted']

    def __init__(self, address):
        Domoticz.Debug("gBridgeClient::__init__")
        self.Address = address

    def getToken(self, api_key):
        gBridgeUrl = "%s/api/v2/auth/token" % self.Address
        req = urllib.request.Request(gBridgeUrl, method='POST')
        req.add_header('apikey', api_key)
        return self.callAPI(req, 'Fetch token')['access_token']

    def syncDevices(self, domoticz_devices_by_name, bridge_devices, delete_removed_devices, token):
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
                prefix = device['idx']
                self.createDevice(name, type, traits, prefix, token)

        # remove devices in gbridge which are no longer in domoticz
        if delete_removed_devices:
            for device in bridge_devices:
                if device['name'] not in domoticz_devices_by_name:
                    self.deleteDevice(device['device_id'], token)

    def fetchDevicesFromBridge(self, token):
        url = "%s/api/device" % self.Address
        req = urllib.request.Request(url)
        req.add_header("Authorization", 'Bearer %s' % token)
        try:
            return json.loads(self.callAPI(req, 'Fetching all devices from gBridge'))
        except JSONDecodeError as e:
            Domoticz.Error('Could not decode JSON due to: %s, json: %s' % (e.msg, e.doc))
            raise e

    def deleteDevice(self, id, token):
        gBridgeUrl = "%s/api/device/%s" % (self.Address, id)
        req = urllib.request.Request(gBridgeUrl, method='DELETE')
        req.add_header("Authorization", 'Bearer %s' % token)
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

    def createDevice(self, name, type, traits, id, token):
        values = {'name': name, 'type': type, 'traits': traits, 'topicPrefix': id}
        data = json.dumps(values).encode('ascii')
        req = urllib.request.Request("%s/api/device" % self.Address, data)
        req.add_header('Content-Type', 'application/json')
        req.add_header("Authorization", 'Bearer %s' % token)
        return self.callAPI(req, 'Try to create device %s for type %s with traits %s' % (name, type, str(traits)))
