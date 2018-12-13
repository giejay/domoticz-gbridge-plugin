# Kappelt gBridge - Domoticz Python Plugin
Python plugin for Domoticz to add integration with [gBridge](https://github.com/kservices/gBridge) project

## Prerequisites

You have two options:
- Using the hosted version on https://gbridge.kappelt.net. This way you only have to create an account, add the account settings to this plugin and you're done.
- Running the gBridge yourself in case you have a server which is capable of running docker images (through compose) and don't want to use the hosted version. More information about hosting it yourself can be found here: https://doc.gbridge.kappelt.net/html/selfHosted/hostItYourself.html

## Installation

1. Clone repository into your domoticz plugins folder
```
cd domoticz/plugins
git clone https://github.com/giejay/domoticz-gbridge-plugin.git
```
2. Restart domoticz
3. Make sure you add "127.0.0.1" to your Local Networks under Settings.
4. Go to "Hardware" page and add new item with type "gBridge"
5. Set your MQTT server address, gBridge config etc. to plugin settings and click Add
 
Example of a hosted setup:
![alt text](https://raw.githubusercontent.com/giejay/domoticz-gbridge-plugin/master/example-hosted.png)

Example of a local setup:
![alt text](https://raw.githubusercontent.com/giejay/domoticz-gbridge-plugin/master/example-local.png)

## Configure devices
For this plugin to know which devices it may add to the gBridge, it checks the description of the device.
`Description: gBridge` is making sure the device is added with its Domoticz name.
`Description: gBridge:Another friendlyName` is creating a device in gBridge with "Another friendlyName".

After you have configured your devices, you have two choices. The first one is going to the Hardware page again, select your gBridge hardware and click "Update". 

The second option, if you have gBridge linked to your Google account already, is asking Google: "Sync my devices". This will trigger a MQTT sync message for which the plugin will start a sync cycle. 
Finally check the logging if the devices are added successfully to gBridge (or visit the device page of gBridge) 

## Testing
Follow the instructions to connect to Google: https://doc.gbridge.kappelt.net/html/firstSteps/gettingStarted.html#connect-google-assistant
After you added gBridge to your Google Home/Assistant, ask Google (again) to "Sync my devices".
Then say: Turn on x light and see your light shining. If something went wrong, check for messages in the Domoticz log regarding gBridge. 
If it doesn't make a lot of sense, create an issue and I will help asap. 

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