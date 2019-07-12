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

import json

class BasePlugin:
    domoticzDevicesByName = None
    domoticzDevicesById = None
    linkedDevices = None
    mqttClients = {}

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
        self.local_setup = Parameters["Address"] is not 'mqtt.gbridge.io:8883'

        for address in Parameters["Address"].split(","):
            self.mqttClients[address] = MqttClient(address.split(":")[0].strip(),
                                                   address.split(":")[1].strip(),
                                                   lambda: self.onMQTTConnected(address),
                                                   self.onMQTTDisconnected,
                                                   self.onMQTTPublish,
                                                   self.onMQTTSubscribed)
            self.mqttClients[address].Open()
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
        self.linkedDevices = self.domoticz_client.getLinkedDevices(domoticz_devices)
        Domoticz.Debug('Linked devices: ' + str(self.linkedDevices))
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
        for mqttClient in self.mqttClients.values():
            mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
        pass

    def onMessage(self, Connection, Data):
        Domoticz.Debug('Incoming message!' + str(Data))
        for mqttClient in self.mqttClients.values():
            mqttClient.onMessage(Connection, Data)

    def onHeartbeat(self):
        Domoticz.Debug("Heartbeating...")

        for mqttClient in self.mqttClients.values():
            # Reconnect if connection has dropped
            if mqttClient.mqttConn is None or (
                    not mqttClient.mqttConn.Connecting() and not mqttClient.mqttConn.Connected() or not mqttClient.isConnected):
                Domoticz.Debug("Reconnecting")
                mqttClient.Open()
            else:
                mqttClient.Ping()


    def onMQTTConnected(self, address):
        Domoticz.Log("MQTT Connected")
        self.mqttClients[address].Subscribe([self.base_topic + '/#'])
        if 'mqtt.gbridge.io' not in address:
            self.mqttClients[address].Subscribe(['domoticz/out'])


    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")

    def onMQTTPublish(self, topic, message):
        Domoticz.Debug("MQTT message: " + topic + " " + str(message))
        if str(topic) == 'domoticz/out':
            if message.get('idx') is not None:
                domoticz_id = str(message['idx'])
                if message.get('Type') is not None and (message['Type'] == 'Scene' or message['Type'] == 'Group'):
                    domoticz_id = 'group_' + domoticz_id
            else:
                return
            device = None
            if domoticz_id in self.domoticzDevicesById:
                device = self.domoticzDevicesById[domoticz_id]
            elif domoticz_id in self.linkedDevices and self.linkedDevices[domoticz_id] in self.domoticzDevicesById:
                # Get the device to which this device message is linked to, for example, device id 13 -> update device 12
                device = self.domoticzDevicesById[self.linkedDevices[domoticz_id]]
            if device is not None:
                adapter = getAdapter(device)
                if adapter is not None:
                    for mqttClient in self.mqttClients.values():
                        adapter.publishStateFromDomoticzTopic(mqttClient, device, self.base_topic, message)
                else:
                    Domoticz.Error('No adapter registered to publish state for device: %s' % str(device))

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
                        if not self.local_setup:
                            for mqttClient in self.mqttClients.values():
                                adapter.publishState(mqttClient, device, self.base_topic, message)  # answer directly
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
