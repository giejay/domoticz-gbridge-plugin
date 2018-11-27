import Domoticz
import json
import re
import urllib.parse
import urllib.request

class DomoticzClient:
    DomoticzPort = ""

    def __init__(self, domoticz_port):
        self.DomoticzPort = domoticz_port
        Domoticz.Debug("DomoticzClient::__init__")

    def fetchDevicesFromDomoticz(self):
        req = urllib.request.Request(
            "http://localhost:%d/json.htm?type=devices&filter=all&used=true&order=Name" % self.DomoticzPort)
        response = urllib.request.urlopen(req).read().decode('utf-8')
        Domoticz.Debug("Fetching all devices from Domoticz %s" % response)
        return json.loads(response)['result']

    def getDevicesByName(self, domoticz_devices):
        domoticz_devices_by_name = {}
        for device in domoticz_devices:
            if "gBridge" in device['Description']:
                match = re.search('gBridge:(.*)([\n|\r]?)', device['Description'])
                if match:
                    name = match.group(1)
                else:
                    name = device['Name']
                domoticz_devices_by_name[name] = device
        return domoticz_devices_by_name