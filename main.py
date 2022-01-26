from m5stack import *
from m5ui import *
from uiflow import *
import wifiCfg
from easyIO import *
import urequests
import json

import time

data = {}

ssid = 'ssid' # SSID
wifipassword = 'password' # Password
endpoint = 'https://example.com/data-for-m5paper' # HTTP Endpoint (No trailing slash)
authorizationHeader = 'Bearer FOOBAR' # Auth Header
screenTitle = 'Home' # Title to display on the device

wifiCfg.doConnect(ssid, wifipassword)

def aggregateData():
  global data
  data['batteryPercentage'] = str(map_value((bat.voltage() / 1000), 3.2, 4.3, 0, 100)) + '%'
  data['isWifiConnected'] = wifiCfg.wlan_sta.isconnected()
  data['temperature'] = '{0:.2f}'.format(sht30.temperature)
  data['humidity'] = str(int(sht30.humidity))
  data['voltage'] = str(bat.voltage() / 1000)
  try:
    req = urequests.request(
      method='GET',
      url=(endpoint + '?temperature=' + data['temperature'] + '&humidity=' + data['humidity'] + '&battery=' + str(map_value((bat.voltage() / 1000), 3.2, 4.3, 0, 100)) + '&voltage=' + data['voltage'] ),
      headers={
'Authorization': authorizationHeader
      })
    data['json'] = json.loads((req.text))
  except:
    pass

def showLoading():
  width = 88
  M5Rect(540-width, 0, 100, 40, 2, 0)
  M5Circle(540-width+18, 20, 5, 0, 15)
  M5TextBox(540-width+32, 3, '...', lcd.FONT_DejaVu24, 15, rotate=0)
  lcd.partial_show(540-width, 0, width, 40)

def showActive(isActive, partialRender):
  width = 88
  if bool(isActive):
    M5Rect(540-width, 0, 100, 40, 2, 0)
    M5Circle(540-width+18, 20, 5, 15, 15)
    M5TextBox(540-width+32, 10, str(data['json']['shutdownDelay']) + 's', lcd.FONT_DejaVu24, 15, rotate=0)
  else:
    M5Rect(540-width, 0, width, 40, 15, 15)
  if partialRender:
    lcd.partial_show(540-width, 0, width, 40)

def renderMenu(keyName, constX, constY, height, width, margin, padding, background, border):
  M5Rect(constX, constY, width, height, background, border)
  M5TextBox(constX+padding, constY+padding, data['json'][keyName]['firstLine'], lcd.FONT_DejaVu24, 0) # 14 / 28
  if bool(data['json'][keyName]['textLarge1']):
    M5TextBox(constX+padding, constY+padding+28, data['json'][keyName]['textLarge1'], lcd.FONT_DejaVu56, 0) # 6 / 13
  else:
    M5TextBox(constX+padding, constY+padding+28, data['json'][keyName]['text1'], lcd.FONT_DejaVu24, 0) # 14 / 28
    M5TextBox(constX+padding, constY+padding+(28*2), data['json'][keyName]['text2'], lcd.FONT_DejaVu24, 0) # 14 / 28
  if bool(data['json'][keyName]['textLarge2']):
    M5TextBox(constX+padding, constY+padding+(28*3), data['json'][keyName]['textLarge2'], lcd.FONT_DejaVu56, 0) # 6
  else:
    M5TextBox(constX+padding, constY+padding+(28*3), data['json'][keyName]['text3'], lcd.FONT_DejaVu24, 0) # 14 / 28
    M5TextBox(constX+padding, constY+padding+(28*4), data['json'][keyName]['text4'], lcd.FONT_DejaVu24, 0) # 14 / 28
  M5TextBox(constX+padding, constY+padding+(28*5), data['json'][keyName]['text5'], lcd.FONT_DejaVu24, 0) # 14 / 28
  M5TextBox(constX+padding, constY+height-padding-16, data['json'][keyName]['actionName'], lcd.FONT_DejaVu18, 6) # 17 / 37

def render():
  lcd.fillScreen(15)
  lcd.font(lcd.FONT_DejaVu24)
  lcd.setTextColor(0, 15)
  M5Rect(0, 0, 540, 40, 15, 15)
  M5TextBox(12, 10, screenTitle, lcd.FONT_DejaVu24, 0, rotate=0)
  M5Line(M5Line.PLINE, 0, 40, 540, 40, 0)
  showActive(True, False)

  border = 0
  background = 15

  margin = 12
  padding = 12

  # menu0
  constX = margin
  constY = 40 + margin
  width = 540 - (constX * 2)
  height = 212
  renderMenu('menu0', constX, constY, height, width, margin, padding, background, border)

  # menu1
  constX = margin
  constY = constY + height + margin
  width = int(width / 2) - int(constX / 2)
  renderMenu('menu1', constX, constY, height, width, margin, padding, background, border)

  # menu2
  constX = margin + width + margin
  renderMenu('menu2', constX, constY, height, width, margin, padding, background, border)

  # menu3
  constX = margin
  constY = constY + height + margin
  renderMenu('menu3', constX, constY, height, width, margin, padding, background, border)

  constX = margin + width + margin
  renderMenu('menu4', constX, constY, height, width, margin, padding, background, border)

  constX = margin
  constY = constY + height + margin
  renderMenu('menu5', constX, constY, height, width, margin, padding, background, border)

  # System us 18 font size, the rest should use 24
  constX = margin + width + margin
  M5Rect(constX, constY, width, height, background, border)
  M5TextBox(constX+padding, constY+padding, 'Time: ' + str(data['json']['timeDisplay']) + ' ~' + str(int(data['json']['wakeupInterval'] / 60)) + 'm', lcd.FONT_DejaVu18, 0)
  M5TextBox(constX+padding, constY+padding+22, 'WiFi: ' + ssid if data['isWifiConnected'] else '? ' + ssid, lcd.FONT_DejaVu18, 0)
  M5TextBox(constX+padding, constY+padding+(22*2), 'Battery: ' + data['batteryPercentage'], lcd.FONT_DejaVu18, 0)
  M5TextBox(constX+padding, constY+padding+(22*3), 'Voltage: ' + data['voltage'], lcd.FONT_DejaVu18, 0)
  M5TextBox(constX+padding, constY+padding+(22*4), 'Temperature: ' + data['temperature'], lcd.FONT_DejaVu18, 0)
  M5TextBox(constX+padding, constY+padding+(22*5), 'Humidity: ' + data['humidity']  + '%', lcd.FONT_DejaVu18, 0)

  M5TextBox(constX+padding, constY+height-padding-16, 'SYSTEM', lcd.FONT_DejaVu18, 6)

showLoading()

aggregateData()
render()
lcd.show()

wait(int(data['json']['shutdownDelay'])) # delay sleep
showActive(False, True)

power.restart_after_seconds(int(data['json']['wakeupInterval'])) # uncomment this when deploy