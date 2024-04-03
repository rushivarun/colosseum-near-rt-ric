from pyasn1.codec.der import encoder, decoder
from pyasn1.type.namedtype import NamedType, NamedTypes
from pyasn1.type.univ import Integer, Sequence, UTF8String

class Message(Sequence):
    componentType = NamedTypes(
        NamedType('id', Integer()),
        NamedType('text', UTF8String())
    )

def encode_message(id, text):
    message = Message()
    message.setComponentByName('id', id)
    message.setComponentByName('text', text)
    return encoder.encode(message)

def decode_message(data):
    return decoder.decode(data, asn1Spec=Message())[0]
