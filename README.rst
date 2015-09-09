Declarative Data Parsing
========================

.. warning::
    This is pre-alpha software. Much of it doesn't work, elements might change
    at any time.

Django-esque object models for structured binary data.

The overall goal is to be able to describe a "model" for binary data which can
then easily be parsed and composed without writing much boilerplate code.
Something like this:

.. code-block:: python

    from nibbles import fields


    class TypeLengthValueField(fields.Field):
        type = fields.ByteField(mapping={0: 'ascii', 1: 'utf-8'})
        length = fields.IntegerField()
        value = fields.StringField(length='length')


    # Each object can be instantiated and then accept an input stream.
    tlv = TypeLengthValueField().consume(io)

    # Or you can directly set the fields!
    tlv = TypeLengthValueField(type=0, length=10, value='\0' * 10)
    tlv.emit()  # output bytes.


Supported Features
------------------

* Variable length strings
* Multi-stage processing (i.e. a zlib compressed field that once decompressed is
  broken into further fields)
* Twisted protocol support

Similar Stuff
-------------

This package won't be best suited for everyone's use case. Parts of it were
inspired by the following, they might suit your needs better! (Below is some
notes about why *I* found that package unsuitable, they're opinion and won't be
true for every use case...or might just be plain wrong.)

scapy_:

* Very network / packet focused.

.. _scapy: http://secdev.org/projects/scapy/

construct_ / construct3_:

* Requires manual writing of parser methods.
* Difficult to inherit parsing.
* Depends upon ``dict`` instances for data instead of classes.

.. _construct: http://construct.readthedocs.org/en/latest/
.. _construct3: http://tomerfiliba.com/blog/Survey-of-Construct3/

protlib_:

* Has class-based objects!
* Doesn't support bit fields, choice fields, Pascal-strings
* Has a globally growing list of ``CType`` objects
* Interaction with Twisted? (Via warning module.)
* Odd choices of what to consider exception vs. warning.
* Endianess is global?
* (Super easy to add, but...) doesn't have nice types like ``DWORD``, etc.

.. _protlib: http://courtwright.org/protlib/

TODO
====

* Setup Sphinx...
* Created a Twisted protocol which can parse incoming packets
* File parser / context
* Deal with Endianess more completely
