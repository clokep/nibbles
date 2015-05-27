Declarative Data Parsing
========================

Django-esque object models for structured data.

Goal of having something like this:

```python

from byte_packer import fields, struct

class SomePacket(struct.Struct):
    class Meta:
        endianess = 'BIG'

    length = fields.UnsignedInt()
    msg = fields.CString()
    color = fields.UnsignedByte(mapping={0: 'NONE', 1: 'BLUE', 2: 'RED'})
    str = fields.PString()

    def post_consume(self):
        # Do something with the fields here...maybe decompression?

data = (
    '\x0A' # length
    'Test\x00' # msg = 'Test'
    '\x01' # color = BLUE
    '\x02AB' # str = 'AB'
)

p = SomePacket(data)
p.msg # prints 'Test'
p.color # prints 'BLUE'
p.str # prints 'AB'
p.length # prints 10
p.meta.consumed_bytes # prints 10

data = (
    '\x0A' # length
    'Test\x00' # msg
    '\x03' # This is invalid!
    '\x02' #  This would also be invalid!
)

p = SomePacket(data) # raises an exception!
```
