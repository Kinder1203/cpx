"""Local HTTP server for the CPX app and session API."""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .cpx_service import CpxSessionService, codex_matcher_factory


ROOT = Path(__file__).resolve().parents[2]
SESSION_ROUTE = re.compile(r"^/api/sessions/([^/]+)/(questions|complete)$")


class CpxRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    service: CpxSessionService
    app_dir: Path

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/health":
            self._json(HTTPStatus.OK, {"status": "ok"})
        elif path == "/api/cases":
            self._json(HTTPStatus.OK, self.service.list_cases())
        elif path == "/api/profile":
            self._json(HTTPStatus.OK, self.service.profile())
        elif path.startswith("/api/"):
            self._json(HTTPStatus.NOT_FOUND, {"error": "API route not found"})
        else:
            self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            payload = self._request_json()
            if path == "/api/sessions":
                case_id = payload.get("case_id")
                if not isinstance(case_id, str) or not case_id:
                    raise ValueError("case_id is required")
                response = self.service.start_session(case_id)
                self._json(HTTPStatus.CREATED, response)
                return

            match = SESSION_ROUTE.fullmatch(path)
            if not match:
                self._json(HTTPStatus.NOT_FOUND, {"error": "API route not found"})
                return
            session_id, action = match.groups()
            if action == "questions":
                question = payload.get("question")
                if not isinstance(question, str) or not question.strip():
                    raise ValueError("question is required")
                response = self.service.ask(session_id, question)
            else:
                response = self.service.complete(session_id, payload.get("assessment"))
            self._json(HTTPStatus.OK, response)
        except KeyError as exc:
            self._json(HTTPStatus.NOT_FOUND, {"error": str(exc)})
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception as exc:
            self.log_error("request failed: %s", exc)
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "internal server error"})

    def _request_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 64 * 1024:
            raise ValueError("request body is too large")
        raw = self.rfile.read(length)
        payload = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    def _json(self, status: HTTPStatus, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(status, body, "application/json; charset=utf-8")

    def _serve_static(self, request_path: str) -> None:
        relative = unquote(request_path).lstrip("/") or "index.html"
        target = (self.app_dir / relative).resolve()
        app_root = self.app_dir.resolve()
        if app_root not in target.parents and target != app_root:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
        }:
            content_type = f"{content_type}; charset=utf-8"
        self._send_bytes(HTTPStatus.OK, body, content_type)

    def _send_bytes(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        # Keep the HTTP/1.1 socket alive so the Android emulator does not coalesce
        # the final response bytes with a TCP close on the 10.0.2.2 host bridge.
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()


def build_server(
    host: str,
    port: int,
    *,
    use_codex: bool,
    release_mode: str = "demo",
) -> ThreadingHTTPServer:
    service = CpxSessionService(
        ROOT / "cpx_agent" / "data" / "patient_cards",
        ROOT / "cpx_agent" / "data" / "sessions" / "learner_profile.json",
        matcher_factory=codex_matcher_factory if use_codex else None,
        release_mode=release_mode,
    )
    handler = type(
        "ConfiguredCpxRequestHandler",
        (CpxRequestHandler,),
        {"service": service, "app_dir": ROOT / "app"},
    )
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--llm", choices=("off", "codex"), default="off")
    parser.add_argument("--release-mode", choices=("demo", "production"), default="demo")
    args = parser.parse_args()
    server = build_server(
        args.host,
        args.port,
        use_codex=args.llm == "codex",
        release_mode=args.release_mode,
    )
    print(f"CPX app: http://{args.host}:{args.port} (LLM: {args.llm})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
