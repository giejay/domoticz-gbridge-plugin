# Kappelt gBridge - Domoticz Python Plugin
Python plugin for Domoticz to add integration with [gBridge](https://github.com/kservices/gBridge) project

## Prerequisites

Setup and run gBridge server, for now only local setups are supported due to username/password protection of remote MQTT server (https://doc.gbridge.kappelt.net/html/index.html).

## Installation

1. Clone repository into your domoticz plugins folder
```
cd domoticz/plugins
git clone --- gbridge
```
2. Restart domoticz
3. Make sure you add "localhost" and "127.0.0.1" to your Local Networks under Settings comma separated: localhost;127.0.0.1
4. Go to "Hardware" page and add new item with type "gBridge"
5. Set your MQTT server address, gBridge config etc. to plugin settings

Once plugin receive any message from mqtt server it will call the domoticz API and switch on a light/switch or change brightness of a device

## Configure devices
For this plugin to know which devices it may add to the gBridge, it checks the description of the device.
`Description: gBridge` is making sure the device is added with its Domoticz name.
`Description: gBridge:Another friendlyName` is creating a device in gBridge with "Another friendlyName".
After you have configured your devices, go the Hardware page again, select your gBridge harware and click "Update". 
Check the logging if the devices are added successfully. 

## Plugin update

1. Stop domoticz
2. Go to plugin folder and pull new version
```
cd domoticz/plugins/gbridge
git pull
```
3. Start domoticz

## Supported devices

The onoff, brightness, scenes and temperature traits are supported, this means the following Domoticz devices can be controlled:
- Lights
- Dimmers
- Blinds (including Percentage and Percentage Inverted)
- Scenes
- (Dummy) switches
- Temperature setpoint