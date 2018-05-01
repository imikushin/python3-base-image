import io
import json
import sys
import unittest

import main


def hello(ctx, payload):
    name = "Noone"
    place = "Nowhere"
    if payload:
        name = payload.get("name", name)
        place = payload.get("place", place)
    return "Hello, %s from %s" % (name, place)


def fail(ctx, payload):
    raise ZeroDivisionError("oh no!")


def logger(ctx, payload):
    print("stdout")
    print("stderr", file=sys.stderr)
    print("stdout2")
    print("stderr2", file=sys.stderr)


class Request():
    """
    Mock of a part of the falcon.Request class
    """
    def __init__(self, content_length=0, stream=None):
        self.content_length = content_length
        self.stream = stream


class TestMainMethods(unittest.TestCase):


    def test_read_logs_valid(self):
        text_io = io.StringIO()
        print("line 1", file=text_io)
        print("line 2", file=text_io)
        logs = main.read_logs(text_io)

        self.assertEqual(["line 1", "line 2"], logs)


    def test_read_logs_empty(self):
        text_io = io.StringIO()
        logs = main.read_logs(text_io)

        self.assertEqual(0, len(logs))


    def test_get_msg_valid(self):
        m = "{\"context\": null, \"payload\": {\"name\": \"Jon\", \"place\": \"Winterfell\"}}"
        req_stream = io.StringIO(m)
        req = Request(content_length=len(m), stream=req_stream)
        
        msg = main.get_msg(req)

        self.assertIn('context', msg)
        self.assertIsNone(msg['context'])
        self.assertIn('payload', msg)
        self.assertEqual({"name": "Jon", "place": "Winterfell"}, msg['payload'])


    def test_get_msg_empty(self):
        msg = main.get_msg(Request())

        self.assertIsNone(msg)


    def test_process_msg_valid(self):
        msg = {'context': None, 'payload': {"name": "Jon", "place": "Winterfell"}}
        body = main.process_msg(msg, hello)
        
        r = json.loads(body)

        self.assertEqual("Hello, Jon from Winterfell", r['payload']);
        self.assertEqual(0, len(r['context']['logs']['stdout']));
        self.assertEqual(0, len(r['context']['logs']['stderr']));
        self.assertIsNone(r['context']['error'])


    def test_process_msg_exception(self):
        msg = {'context': None, 'payload': None}
        body = main.process_msg(msg, fail)
        
        r = json.loads(body)
        err = r['context']['error']
        stderr = main.read_logs(io.StringIO(err['stacktrace']))

        self.assertIsNone(r['payload'])
        self.assertEqual("ZeroDivisionError", err['type'])
        self.assertEqual("oh no!", err['message'])
        self.assertEqual(stderr, r['context']['logs']['stderr'])
        self.assertEqual(0, len(r['context']['logs']['stdout']))


    def test_process_msg_logs(self):
        msg = {'context': None, 'payload': None}
        body = main.process_msg(msg, logger)
        r = json.loads(body)

        self.assertIsNone(r['payload'])
        self.assertIsNone(r['context']['error'])
        self.assertEqual(["stderr", "stderr2"], r['context']['logs']['stderr'])
        self.assertEqual(["stdout", "stdout2"], r['context']['logs']['stdout'])


if __name__ == '__main__':
    unittest.main()