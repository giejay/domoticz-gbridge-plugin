"""
<plugin key="gBridge" name="gBridge" version="0.0.14">
    <description>
      Plugin to add support for <a href="https://github.com/kservices/gBridge">gBridge</a> project<br/><br/>
      Specify MQTT server, the base topic, so gBridge/{your user id} and the gBridge url + credentials<br/>
      If using local MQTT server, add also "MQTT Client Gateway with LAN Interface", config on Topic "out" to have the live update.<br/>
    </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1:1883"/>
        <param field="Username" label="MQTT username" width="300px" required="false" default=""/>
        <param field="Password" label="MQTT password" width="300px" required="false" default="" password="true"/>
        <param field="Mode1" label="MQTT base topic" width="300px" required="true" default="gBridge/u1"/>
        <param field="Port" label="Domoticz port" width="300px" required="true" default="8080"/>
        <param field="Mode2" label="gBridge url" width="300px" required="true" default="http://localhost:8082"/>
        <param field="Mode3" label="gBridge username" width="300px" required="true" default="username"/>
        <param field="Mode4" label="gBridge password" width="300px" required="true" default="password" password="true"/>
        <param field="Mode5" label="Delete removed Domoticz devices from gBridge" width="75px">
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

from adapters import getAdapter
from gbridge_client import gBridgeClient
from domoticz_client import DomoticzClient
from mqtt import MqttClient


class BasePlugin:
    mqttClient = None
    domoticzDevicesByName = None
    domoticzDevicesById = None

    def onStart(self):
        self.debugging = Parameters["Mode6"]

        if self.debugging == "Verbose":
            Domoticz.Debugging(2 + 4 + 8 + 16 + 64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2)

        Domoticz.Debug("onStart called")

        self.base_topic = Parameters["Mode1"].strip()
        self.domoticz_port = int(Parameters["Port"].strip())
        self.delete_removed_devices = Parameters["Mode5"].strip()
        if Parameters["Mode6"].find("localhost") >= 0:
            self.domoticz_mqtt_used = True
        else :
            self.domoticz_mqtt_used = False
        
        self.mqttClient = MqttClient(Parameters["Address"].strip().split(":")[0],
                                     Parameters["Address"].strip().split(":")[1],
                                     self.onMQTTConnected,
                                     self.onMQTTDisconnected,
                                     self.onMQTTPublish,
                                     self.onMQTTSubscribed)
        self.gBridgeClient = gBridgeClient(Parameters["Mode2"].strip(),
                                           Parameters["Mode3"].strip(),
                                           Parameters["Mode4"].strip())
        self.domoticz_client = DomoticzClient(self.domoticz_port)

        self.syncDevices()

        Domoticz.Debug("Done")

    def syncDevices(self):
        Domoticz.Debug('Starting sync')
        bridge_devices = self.gBridgeClient.fetchDevicesFromBridge()
        domoticz_devices = self.domoticz_client.fetchDevicesFromDomoticz()
        self.domoticzDevicesByName = self.domoticz_client.getDevicesByName(domoticz_devices)
        self.domoticzDevicesById = {x['idx']: x for x in list(self.domoticzDevicesByName.values())}
        Domoticz.Debug('Domoticz devices available for gBridge: ' + str(self.domoticzDevicesByName.keys()))
        self.gBridgeClient.syncDevices(self.domoticzDevicesByName, bridge_devices,
                                       self.delete_removed_devices == 'True')

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
        self.mqttClient.Subscribe([self.base_topic + '/#','domoticz/out'])

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")

    def onMQTTPublish(self, topic, message):
        Domoticz.Debug("MQTT message: " + topic + " " + str(message))
        if str(topic) == 'domoticz/out':
            if message.get('name') is not None:
                name = message['name']
            elif message.get('Name') is not None:
                name = message['Name']
            else:
                return
            if name in self.domoticzDevicesByName:
                device = self.domoticzDevicesByName[name]
                adapter = getAdapter(device)
                if adapter is not None:
                    adapter.publishState(self.mqttClient, device, self.base_topic , message)
                else:
                    Domoticz.Error('No adapter registered for action: %s for device: %s' % (action, str(device)))
        else:        
            if message == 'SYNC':
                self.syncDevices()
            elif topic.endswith('/set'):
                Domoticz.Debug('Published new state for device, topic: %s, state: %s' % (topic, message))
            else:
                match = re.search(self.base_topic + '/(.*)/(.*)', topic)

                if match:
                    device_id = match.group(1)
                    # Backwards compatibility, previously the device name was used as topic name
                    if device_id in self.domoticzDevicesByName:
                        device = self.domoticzDevicesByName[device_id]
                    elif device_id in self.domoticzDevicesById:
                        device = self.domoticzDevicesById[device_id]
                    else:
                        Domoticz.Log('Received message for device which is not in Domoticz: %s, skipping' % device_id)
                        return
                    action = match.group(2)
                    adapter = getAdapter(device)
                    if adapter is not None:
                        adapter.handleMqttMessage(device, str(message), action, self.domoticz_port)
                        if self.domoticz_mqtt_used == False:
                            self.mqttClient.Publish(topic + '/set', message) #answer directly
                    else:
                        Domoticz.Error('No adapter registered for action: %s for device: %s' % (action, str(device)))


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
