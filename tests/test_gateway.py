import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from jarvis.gateway.router import GatewayRouter
from jarvis.gateway.server import create_app


class TestGateway(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "inbox.db"
        self.app = create_app(repo_root=self.repo_root, db_path=self.db_path)
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()
        self.tmp.cleanup()

    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"ok": True})

    def test_websocket_roundtrip_and_inbox_done(self):
        with self.client.websocket_connect("/ws") as ws:
            ws.send_json({"workspace": "default", "text": "check repo", "mode": "plan"})
            data = ws.receive_json()

        self.assertEqual(data["status"], "done")
        self.assertEqual(data["mode"], "plan")
        self.assertIsInstance(data["inbox_id"], int)

        conn = sqlite3.connect(self.db_path)
        row = conn.execute("SELECT status, mode, workspace FROM inbox_messages WHERE id = ?", (data["inbox_id"],)).fetchone()
        conn.close()
        self.assertEqual(row[0], "done")
        self.assertEqual(row[1], "plan")
        self.assertEqual(row[2], "default")

    def test_plan_mode_does_not_call_memory_write(self):
        def fake_run(cmd, **kwargs):
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
            if "memory_write.py" in cmd_str:
                raise AssertionError("plan mode must not call memory_write")
            if "memory_read.py" in cmd_str:
                class Res:
                    stdout = '{"success": true}'
                return Res()
            raise AssertionError(f"unexpected subprocess call: {cmd_str}")

        router = GatewayRouter(self.repo_root)
        with patch("jarvis.gateway.router.subprocess.run", side_effect=fake_run):
            text = router.handle("default", "Create plan only", "plan")
        self.assertIn("Execution Plan", text)


if __name__ == "__main__":
    unittest.main()
