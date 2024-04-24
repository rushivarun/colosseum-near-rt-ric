from pyasn1.codec.der import decoder
from pyasn1.codec.der import encoder
from pyasn1.type.namedtype import NamedType, NamedTypes
from pyasn1.type.univ import Integer, Sequence, SequenceOf, Boolean, BitString, OctetString
import datetime
import json

class Message(Sequence):
    componentType = NamedTypes(
        NamedType('sender', OctetString()),
        NamedType('messages', OctetString()),
        NamedType('criticality', Integer()),
        NamedType('signals', OctetString()),
        NamedType('active', Boolean())
    )

def encode_asn1_message(sender, criticality, messages, signals, active):
    logs_message = {
        "type": "E2term",
        "log_time": datetime.datetime.now(),
        "message": messages,
        "origin": "NS3 Simulation",
        "dest": "A1 message bus"
    }
    message = Message()
    message.setComponentByName('sender', sender)
    message.setComponentByName('messages', messages)
    message.setComponentByName('criticality', criticality)
    message.setComponentByName('signals', signals)
    message.setComponentByName('active', active)
    return encoder.encode(message), logs_message

def decode_asn1_message(data):
    decoded_message, _ = decoder.decode(data, asn1Spec=Message())
    return {
        'sender': str(decoded_message.getComponentByName('sender')),
        'messages': str(decoded_message.getComponentByName('messages')),
        'criticality': int(decoded_message.getComponentByName('criticality')),
        'signals': str(decoded_message.getComponentByName('signals')),
        'active': bool(decoded_message.getComponentByName('active'))
    }