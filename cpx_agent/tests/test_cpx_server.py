from __future__ import annotations

import http.client
import tempfile
import threading
import unittest
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path

from cpx_agent.src.cpx_server import CpxRequestHandler


class CpxServerResponseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        app_dir = Path(self.temporary_directory.name)
        self.index_body = "<!doctype html><html lang='ko'><body>문진</body></html>".encode()
        (app_dir / "index.html").write_bytes(self.index_body)
        handler = type(
            "TestCpxRequestHandler",
            (CpxRequestHandler,),
            {"app_dir": app_dir},
        )
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary_directory.cleanup()

    def test_static_response_has_exact_length_and_persistent_http11_connection(self) -> None:
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=2)
        connection.request("GET", "/")
        response = connection.getresponse()
        body = response.read()

        self.assertEqual(response.status, HTTPStatus.OK)
        self.assertEqual(response.version, 11)
        self.assertEqual(response.getheader("Content-Length"), str(len(self.index_body)))
        self.assertEqual(response.getheader("Connection"), "keep-alive")
        self.assertEqual(response.getheader("Content-Type"), "text/html; charset=utf-8")
        self.assertEqual(body, self.index_body)
        connection.close()


if __name__ == "__main__":
    unittest.main()
