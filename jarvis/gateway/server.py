"""FastAPI gateway server for Jarvis."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

from .inbox import InboxStore
from .router import GatewayRouter


def create_app(repo_root: Path | None = None, db_path: Path | None = None) -> FastAPI:
    base = Path(repo_root or Path(__file__).resolve().parents[2])
    inbox_db = Path(db_path or (base / "data" / "inbox.db"))

    app = FastAPI()
    app.state.inbox = InboxStore(inbox_db)
    app.state.router = GatewayRouter(base)
    app.state.ui_path = Path(__file__).resolve().parent / "ui" / "index.html"

    @app.get("/health")
    def health():
        return JSONResponse({"ok": True})

    @app.get("/")
    def index():
        return HTMLResponse(app.state.ui_path.read_text(encoding="utf-8"))

    @app.get("/app.js")
    def app_js():
        js_path = Path(__file__).resolve().parent / "ui" / "app.js"
        return HTMLResponse(js_path.read_text(encoding="utf-8"), media_type="application/javascript")

    @app.websocket("/ws")
    async def ws_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                payload = await websocket.receive_json()
                workspace = payload.get("workspace", "default")
                text = payload.get("text", "").strip()
                mode = payload.get("mode", "plan")

                if mode not in {"plan", "exec"}:
                    await websocket.send_json(
                        {
                            "inbox_id": None,
                            "status": "failed",
                            "mode": mode,
                            "text": "",
                            "error": "mode must be 'plan' or 'exec'",
                        }
                    )
                    continue

                inbox_id = app.state.inbox.insert_pending(workspace, "web", mode, text)
                app.state.inbox.set_status(inbox_id, "running")

                try:
                    response_text = app.state.router.handle(workspace, text, mode)
                    app.state.inbox.set_status(inbox_id, "done", response_text=response_text, error_text=None)
                    await websocket.send_json(
                        {
                            "inbox_id": inbox_id,
                            "status": "done",
                            "mode": mode,
                            "text": response_text,
                            "error": None,
                        }
                    )
                except Exception as exc:
                    app.state.inbox.set_status(inbox_id, "failed", response_text=None, error_text=str(exc))
                    await websocket.send_json(
                        {
                            "inbox_id": inbox_id,
                            "status": "failed",
                            "mode": mode,
                            "text": "",
                            "error": str(exc),
                        }
                    )
        except WebSocketDisconnect:
            return

    return app


app = create_app()
