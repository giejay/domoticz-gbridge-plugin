import Domoticz
import json
import re
import urllib.parse
import urllib.request
from urllib.error import URLError, HTTPError

class DomoticzClient:
    DomoticzPort = ""

    def __init__(self, domoticz_port):
        self.DomoticzPort = domoticz_port
        Domoticz.Debug("DomoticzClient::__init__")

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

    def fetchDevicesFromDomoticz(self):
        url = "http://127.0.0.1:%d/json.htm?type=devices&filter=all&used=true&order=Name" % self.DomoticzPort
        req = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(req).read().decode('utf-8')
        except HTTPError as e:
            Domoticz.Error('The server couldn\'t fetch devices from Domoticz')
            Domoticz.Error('Error code: %d, reason: %s' % (e.code, e.reason))
            raise
        except URLError as e:
            Domoticz.Error('Could not fetch devices from Domoticz, failed to reach a server: %s.' % url)
            Domoticz.Error('Reason: %s' % e.reason)
            raise
        else:
            Domoticz.Debug('Successfully fetched devices from Domoticz, response: %s' % response)
            return json.loads(response)['result']