"""
<plugin key="gBridge" name="gBridge" version="0.0.14">
    <description>
      Plugin to add support for <a href="https://github.com/kservices/gBridge">gBridge</a> project<br/><br/>
      Specify MQTT server, the base topic, so gBridge/{your user id} and the gBridge url + credentials<br/>
    </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1:1883"/>
        <param field="Mode1" label="MQTT base topic" width="300px" required="true" default="gBridge/u1"/>
        <param field="Port" label="Domoticz port" width="300px" required="true" default="8080"/>
        <param field="Mode2" label="gBridge url" width="300px" required="true" default="http://localhost:8082"/>
        <param field="Username" label="gBridge username" width="300px" required="true" default="username"/>
        <param field="Password" label="gBridge password" width="300px" required="true" default="password"/>
        <param field="Mode3" label="Delete removed Domoticz devices from gBridge" width="75px">
            <options>
                <option label="True" value="True"/>
                <option label="False" value="False" default="true" />
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="Verbose" value="Verbose"/>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import re

from adapters import adapter_by_type
from gbridge_client import gBridgeClient
from domoticz_client import DomoticzClient
from mqtt import MqttClient


class BasePlugin:
    mqttClient = None

    def onStart(self):
        self.debugging = Parameters["Mode6"]

        if self.debugging == "Verbose":
            Domoticz.Debugging(2 + 4 + 8 + 16 + 64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2)

        Domoticz.Debug("onStart called")

        self.base_topic = Parameters["Mode1"].strip()
        self.domoticz_port = int(Parameters["Port"].strip())
        self.delete_removed_devices = Parameters["Mode3"].strip()

        self.mqttClient = MqttClient(Parameters["Address"].strip().split(":")[0],
                                     Parameters["Address"].strip().split(":")[1],
                                     self.onMQTTConnected,
                                     self.onMQTTDisconnected,
                                     self.onMQTTPublish,
                                     self.onMQTTSubscribed)
        self.gBridgeClient = gBridgeClient(Parameters["Mode2"].strip(),
                                           Parameters["Username"].strip(),
                                           Parameters["Password"].strip())
        domoticz_client = DomoticzClient(self.domoticz_port)

        bridgeDevices = self.gBridgeClient.fetchDevicesFromBridge()
        domoticzDevices = domoticz_client.fetchDevicesFromDomoticz()
        self.domoticzDevicesByName = domoticz_client.getDevicesByName(domoticzDevices)
        Domoticz.Debug('Domoticz devices available for gBridge: ' + str(self.domoticzDevicesByName))
        self.gBridgeClient.syncDevices(self.domoticzDevicesByName, bridgeDevices, self.delete_removed_devices == 'True')

        Domoticz.Debug("Done")

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug("onCommand: " + Command + ", level (" + str(Level) + ") Color:" + Color)

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
        Domoticz.Debug('Incoming message!' + str(Data))
        self.mqttClient.onMessage(Connection, Data)

    def onHeartbeat(self):
        Domoticz.Debug("Heartbeating...")

        # Reconnect if connection has dropped
        if self.mqttClient.mqttConn is None or (
                not self.mqttClient.mqttConn.Connecting() and not self.mqttClient.mqttConn.Connected() or not self.mqttClient.isConnected):
            Domoticz.Debug("Reconnecting")
            self.mqttClient.Open()
        else:
            self.mqttClient.Ping()

    def onMQTTConnected(self):
        self.mqttClient.Subscribe([self.base_topic + '/#'])

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")

    def onMQTTPublish(self, topic, message):
        Domoticz.Debug("MQTT message: " + topic + " " + str(message))

        match = re.search(self.base_topic + '/(.*)/(.*)', topic)

        if match:
            device_name = match.group(1)
            if device_name not in self.domoticzDevicesByName:
                Domoticz.Log('Received message for device which is not in Domoticz: %s, skipping' % device_name)
                return
            device = self.domoticzDevicesByName[device_name]
            action = match.group(2)
            adapter = adapter_by_type[action]
            if adapter:
                if 'Type' in device and device['Type'] in adapter:
                    # Specific adapter for this switch type
                    adapter[device['Type']].handleMqttMessage(device['idx'], str(message),
                                                                    self.domoticz_port)
                else:
                    adapter['Default'].handleMqttMessage(device['idx'], str(message), self.domoticz_port)
            else:
                Domoticz.Error('No adapter registered for action: %s for device: %s' % (action, device_name))


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onMessage(Connection, Data):
    global _plugin
    Domoticz.Debug('Message from base')
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
