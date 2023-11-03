from network      import STA_IF, WLAN
from binascii     import hexlify
from time         import sleep, localtime
from machine      import Pin
from umqtt.simple import MQTTClient

####### UDFYLD DISSE #######
SSID        = 'IOT-netvaerk'
PASSWORD    = 'testgruppe5'
CLIENT_ID   = 'klient_1'
MQTT_BROKER = '192.168.1.18'
############################

green_button  = Pin(3, Pin.IN, Pin.PULL_UP)
yellow_button = Pin(4, Pin.IN, Pin.PULL_UP)
red_button    = Pin(5, Pin.IN, Pin.PULL_UP)
green_led     = Pin(6, Pin.OUT)
yellow_led    = Pin(7, Pin.OUT)
red_led       = Pin(8, Pin.OUT)

def mqtt_connect():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=3600)
    client.connect()
    print('Forbundet til MQTT broker med IP:', MQTT_BROKER)
    return client

def publish(topic, payload):
    client.publish(topic, payload)
    print(f'Publicerede {payload} til {topic}')
    sleep(3)

def get_datetime():
    time_list = localtime()
    date = str(time_list[0:3]).strip('()').replace(', ', '-')
    time = str(time_list[3:6]).strip('()').replace(', ', ':')
    return f'{date} {time}'

def get_ip():
    ifconfig = nic.ifconfig()
    ip = str(ifconfig[0])
    return ip

def publish_ap(topic):
    ap_list = []
    ap_scan = nic.scan()
    for ap in ap_scan:
        ap_list.append(ap)
    for ix in ap_list:
        ssid = str(ix[0]).strip("b'")
        if ssid == SSID:
            mac = str(hexlify(ix[1])).strip("b'")
            mac = mac[:2] + ':' + mac[2:4] + ':' + mac[4:6] + ':' + mac[6:8] + ':' + mac[8:10] + ':' + mac[10:12]
            dbm = str(ix[3])
            publish(topic, f'{get_datetime()} | {CLIENT_ID} | {ssid} | {mac} | {dbm}')

def toggle_led(toggle):
    red_led(toggle)
    yellow_led(toggle)
    green_led(toggle)

def blink_led(led, delay):
    led(1)
    sleep(delay)
    led(0)

def intro(delay):
    for ix in range(5):
        blink_led(red_led, delay)
        blink_led(yellow_led, delay)
        blink_led(green_led, delay)
    for ix in range(2):
        toggle_led(1)
        sleep(delay)
        toggle_led(0)
        sleep(delay)
    toggle_led(1)
    print('Enhed er klar!')

def wave(led1, led2, led3, delay):
    toggle_led(0)
    sleep(delay)
    blink_led(led1, delay)
    blink_led(led2, delay)
    blink_led(led3, delay * 2)
    blink_led(led2, delay)
    blink_led(led1, delay)
    sleep(delay)
    toggle_led(1)

nic = WLAN(STA_IF)
nic.active(True)
nic.connect(SSID, PASSWORD)
while nic.isconnected() is False:
    sleep(1)
print(f'Forbundet til {SSID}')

try:
    client = mqtt_connect()
except OSError:
    print('Kunne ikke forbinde til MQTT broker. Forsøger igen om:')
    for n in range(30, 0, -1):
        sleep(1)
        print(n)
    client = mqtt_connect()

publish(f'iot/status', f'{CLIENT_ID} forbundet med IP: {get_ip()} @ {get_datetime()}')
publish_ap(f'iot/status/{CLIENT_ID}')
status_time = localtime()
pressed = 0
intro(0.2)
while True:
    current_time = localtime()
    if status_time[3] != current_time[3]:
        publish('iot/status', f'{CLIENT_ID} forbundet med IP: {get_ip()} @ {get_datetime()}')
        status_time = current_time
    if green_button() is pressed:
        wave(green_led, yellow_led, red_led, 0.2)
        publish(f'iot/{CLIENT_ID}', f'{get_datetime()} | {CLIENT_ID} | {get_ip()} | {MQTT_BROKER} | HAPPY')
    if yellow_button() is pressed:
        for ix in range(4):
            toggle_led(0)
            sleep(0.2)
            toggle_led(1)
            sleep(0.2)
        publish(f'iot/{CLIENT_ID}', f'{get_datetime()} | {CLIENT_ID} | {get_ip()} | {MQTT_BROKER} | NEUTRAL')
    if red_button() is pressed:
        wave(red_led, yellow_led, green_led, 0.2)
        publish(f'iot/{CLIENT_ID}', f'{get_datetime()} | {CLIENT_ID} | {get_ip()} | {MQTT_BROKER} | ANGRY')
