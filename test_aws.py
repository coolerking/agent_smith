# -*- coding: utf-8 -*-
from time import sleep


def test_aws():
    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/smith.yml', 'smith')

    from parts.broker import PowerReporter
    power = PowerReporter(factory, debug=True)
    print('on')
    power.on()

    try:
        while True:

            sleep(10)
    except KeyboardInterrupt:
        print('off')
    finally:
        power.off()
        sleep(20)

def test_aws3():
    import donkeycar as dk
    V = dk.vehicle.Vehicle()

    from parts.broker import AWSShadowClientFactory
    factory = AWSShadowClientFactory('conf/aws/smith.yml', 'smith')

    from parts.broker import PowerReporter
    power = PowerReporter(factory, debug=True)
    print('on')
    power.on()

    from parts.broker.debug import GetTub
    tub = GetTub()
    V.add(tub, outputs=[
        'user/mode',
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'timestamp'
    ])

    from parts.broker.debug import GetImage
    image = GetImage()
    V.add(image, outputs=['cam/image_array'])

    from parts.broker import TubPublisher
    tub_pub = TubPublisher(factory, debug=True)
    V.add(tub_pub, inputs=[
        'cam/image_array',
        'user/angle', 'user/throttle', 'user/lift_throttle',
        'pilot/angle', 'pilot/throttle', 'pilot/lift_throttle',
        'user/mode', 'timestamp'
    ])

    try:
        V.start(rate_hz=20, max_loop_count=10000)

    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    finally:
        power.off()
        print('off')
        sleep(20)

def test_aws2():
    topic = 'real/agent/loader/test'
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
    myAWSIoTMQTTClient = None

    myAWSIoTMQTTClient = AWSIoTMQTTClient('smith', useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint('ag190y2vfd9hs-ats.iot.ap-northeast-1.amazonaws.com', 8883)
    myAWSIoTMQTTClient.configureCredentials('conf/aws/AmazonRootCA1.pem', 'conf/aws/436b3dba96-private.pem.key', 'conf/436b3dba96-certificate.pem.crt')


    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    myAWSIoTMQTTClient.connect()

    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
    sleep(2)

    loopCount = 0
    while True:
        import json
        message = {}
        message['message'] = {'test':'hehehe'}
        message['sequence'] = loopCount
        messageJson = json.dumps(message)
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        print('Published topic %s: %s\n' % (topic, messageJson))
        loopCount += 1
        sleep(1)

def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

if __name__ == '__main__':
    test_aws3()
