import datetime

def Greeting():
    greeting_message = {
        "type": "E2term",
        "log_time": datetime.datetime.now(),
        "message": "initializing simulation environment",
        "origin": "NS3 Simulation",
        "dest": "A1 message bus"
    }
    return greeting_message

def IPSetup(ip_address, port):
    message = {
        "type": "E2term",
        "log_time": datetime.datetime.now(),
        "message": "ASN socket setup on {}:{}".format(ip_address, port),
        "origin": "NS3 Simulation",
        "dest": "A1 message bus"
    }
    return message