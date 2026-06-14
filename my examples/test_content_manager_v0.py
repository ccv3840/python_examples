import unittest
from unittest.mock import MagicMock, patch

import content_manager_v0 as cm


class FakeCursor:
    def __init__(self, fetchone_result=None):
        self.execute = MagicMock()
        self.fetchone = MagicMock(return_value=fetchone_result)


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.close = MagicMock()

    def cursor(self):
        return self._cursor


class TestDbContextManager(unittest.TestCase):
    def test_get_db_cursor_closes_connection_on_normal_exit(self):
        cursor = FakeCursor()
        connection = FakeConnection(cursor)

        with patch.object(cm.sqlite3, "connect", return_value=connection):
            with cm._get_db_cursor("test.db") as returned_cursor:
                self.assertIs(returned_cursor, cursor)
                returned_cursor.execute("SELECT 1")

        connection.close.assert_called_once()

    def test_get_db_cursor_closes_connection_on_exception(self):
        cursor = FakeCursor()
        connection = FakeConnection(cursor)

        with patch.object(cm.sqlite3, "connect", return_value=connection):
            with self.assertRaises(RuntimeError):
                with cm._get_db_cursor("test.db") as returned_cursor:
                    self.assertIs(returned_cursor, cursor)
                    raise RuntimeError("boom")

        connection.close.assert_called_once()


class TestGetSignalFromDB(unittest.TestCase):
    def test_get_signal_from_db_returns_expected_value(self):
        fake_cursor = FakeCursor(fetchone_result=(1, "expected-signal"))

        with patch.object(cm, "_get_db_cursor") as mocked_context_manager:
            mocked_context_manager.return_value.__enter__.return_value = fake_cursor
            mocked_context_manager.return_value.__exit__.return_value = False

            result = cm.GetSignalFromDB("project-a", "train-x", "funswidi-y")

        self.assertEqual(result, "expected-signal")
        fake_cursor.execute.assert_called_once_with(
            "SELECT * FROM signals WHERE project = ? AND train_type = ? AND funswidi = ?",
            ("project-a", "train-x", "funswidi-y"),
        )
        fake_cursor.fetchone.assert_called_once()

    def test_get_signal_from_db_returns_empty_string_when_missing(self):
        fake_cursor = FakeCursor(fetchone_result=None)

        with patch.object(cm, "_get_db_cursor") as mocked_context_manager:
            mocked_context_manager.return_value.__enter__.return_value = fake_cursor
            mocked_context_manager.return_value.__exit__.return_value = False

            result = cm.GetSignalFromDB("project-a", "train-x", "funswidi-y")

        self.assertEqual(result, "")
        fake_cursor.execute.assert_called_once()
        fake_cursor.fetchone.assert_called_once()


if __name__ == "__main__":
    unittest.main()
