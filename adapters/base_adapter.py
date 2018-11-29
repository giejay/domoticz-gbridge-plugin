import urllib.parse
import urllib.request
import Domoticz

class Adapter:

    def __init__(self):
        pass

    def handleMqttMessage(self, device_id, data, action, domoticz_port):
        raise NotImplementedError("Please Implement this method")

    def getTraits(self):
        raise NotImplementedError("Please Implement this method")

    def getBridgeType(self, device):
        raise NotImplementedError("Please Implement this method")

    def callDomoticzApi(self, domoticz_port, command):
        url = "http://localhost:%s/json.htm?type=command&%s" % (domoticz_port, command)
        Domoticz.Debug('Executing command for device: %s' % command)
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req).read()
        return response.decode('utf-8')
