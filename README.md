Declarative Data Parsing
========================

Warning: This is pre-alpha software. Much of it doesn't work, elements might
change at any time.

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
    version = fields.windows.OSVERSIONINFOEX()
    bytes = fields.Byte(length=length)

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
p.version.build_id # prints 2600

data = (
    '\x0A' # length
    'Test\x00' # msg
    '\x03' # This is invalid!
    '\x02' #  This would also be invalid!
)

p = SomePacket(data) # raises an exception!
```

Supported Features
------------------

* Variable length strings
* Multi-stage processing (i.e. a zlib compressed field that once decompressed is broken into further fields)
* Twisted protocol support

Similar Stuff
-------------

[scapy](http://secdev.org/projects/scapy/)
* Still requires manually writing parser methods.
* Difficult to inherit parsing.

[construct](http://construct.readthedocs.org/en/latest/) / [construct3](http://tomerfiliba.com/blog/Survey-of-Construct3/)
* Still requires manually writing parser methods.
* Difficult to inherit parsing.

[protlib](http://courtwright.org/protlib/):
* Doesn't support bit fields, choice fields, Pascal-strings
* Has a globally growing list of `CType` objects
* Interaction with Twisted? (Via warning module.)
* Odd choices of what to consider exception vs. warning.
* Endianess is global?
* (Super easy to add, but...) doesn't have nice types like `DWORD`, etc.


TODO
====

* Setup Sphinx...
* Created a Twisted protocol which can parse incoming packets
* File parser / context
* Deal with Endianess more completely
