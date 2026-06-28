from __future__ import annotations

import http.client
import json
import tempfile
import threading
import unittest
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path

from cpx_agent.src.bad_news_backend import BadNewsSessionService
from cpx_agent.src.cpx_server import CpxRequestHandler

ROOT = Path(__file__).resolve().parents[2]


class CpxServerResponseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        app_dir = Path(self.temporary_directory.name)
        service = BadNewsSessionService(
            ROOT / "cpx_agent" / "data" / "bad_news",
            app_dir / "reports",
        )
        self.index_body = "<!doctype html><html lang='ko'><body>문진</body></html>".encode()
        (app_dir / "index.html").write_bytes(self.index_body)
        handler = type(
            "TestCpxRequestHandler",
            (CpxRequestHandler,),
            {"app_dir": app_dir, "service": service},
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

    def test_api_cases_uses_imported_bad_news_backend(self) -> None:
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=2)
        connection.request("GET", "/api/cases")
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))

        case_ids = [case["case_id"] for case in payload["cases"]]
        self.assertEqual(response.status, HTTPStatus.OK)
        self.assertIn("B05-breast-cancer", case_ids)
        self.assertTrue(all(case_id.startswith("B") for case_id in case_ids))
        self.assertNotIn("synthetic_abdominal_pain_example", case_ids)
        self.assertNotIn("synthetic_chest_pain_example", case_ids)
        connection.close()

    def test_api_session_starts_bad_news_case(self) -> None:
        body = json.dumps({"case_id": "B05-breast-cancer"}).encode("utf-8")
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=2)
        connection.request(
            "POST",
            "/api/sessions",
            body=body,
            headers={"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))

        self.assertEqual(response.status, HTTPStatus.CREATED)
        self.assertEqual(payload["case"]["case_id"], "B05-breast-cancer")
        self.assertIsInstance(payload["session_id"], str)
        self.assertEqual(payload["session"]["messages"], [])
        connection.close()


if __name__ == "__main__":
    unittest.main()
