from mcn.mq import Message, IncomingMessage
import pytest
import json


def test_message():
    msg = Message()
    assert msg.meta.get("id", None)
    assert msg.data == dict()
    assert msg.meta
    assert msg.get_meta("ctime", None)
    msg.update(test=123)
    msg.update_meta(test=234)
    assert msg.get("test", None) == 123
    assert msg.get_meta("test", None) == 234
    json_str = json.dumps(
        dict(
            data=msg.data,
            meta=msg.meta,
        ),
        indent=4,
    )

    assert str(msg) == json_str

    # test incoming message
    assert issubclass(IncomingMessage, Message)
    im = IncomingMessage(None, None, None, str(msg).encode())
    assert im.meta["id"] == msg.meta["id"]
    assert im.get("test", None) == msg.get("test", True)
    assert im.get_meta("test", None) == msg.get_meta("test", True)
    assert im["test"] == 123

    assert dict(im) == dict(msg)
