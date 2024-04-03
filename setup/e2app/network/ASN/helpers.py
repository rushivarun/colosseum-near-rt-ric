from pyasn1.codec.der import decoder
from pyasn1.codec.der import encoder
from pyasn1.type.namedtype import NamedType, NamedTypes
from pyasn1.type.univ import Integer, Sequence, SequenceOf, UTF8String, Boolean

class Message(Sequence):
    componentType = NamedTypes(
        NamedType('sender', UTF8String()),
        NamedType('message', UTF8String()),
        NamedType('criticality', Integer()),
        NamedType('signals', SequenceOf(componentType=Integer())),
        NamedType('active', Boolean())
    )

def encode_asn1_message(sender, criticality, signals, active):
    message = Message()
    message.setComponentByName('sender', sender)
    message.setComponentByName('criticality', criticality)
    message.setComponentByName('signals', signals)
    message.setComponentByName('active', active)
    return encoder.encode(message)

def decode_asn1_message(data):
    decoded_message, _ = decoder.decode(data, asn1Spec=Message())
    return {
        'sender': str(decoded_message.getComponentByName('sender')),
        'criticality': int(decoded_message.getComponentByName('criticality')),
        'signals': [int(x) for x in decoded_message.getComponentByName('signals')],
        'active': bool(decoded_message.getComponentByName('active'))
    }