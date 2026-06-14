# Content manager implementation from scratch

import asyncio
from contextlib import contextmanager
from typing import Optional
import sqlite3


class File:
    def __init__(self, filename, method) -> None:
        self.file = open(filename, method)

    def __enter__(self):
        print("Enter")
        return self.file

    def __exit__(self, exc_type: type, exc_val: object, exc_tb: object):
        print("Exit")
        if exc_type is Exception:
            print("File not closed!")
            print(f"Exception type: {exc_type}")
            print(f"Exception value: {exc_val}")
            print(f"Exception traceback: {exc_tb}")

        self.file.close()
        return True


@contextmanager
def file_context(filename, method):
    print("enter")
    file = open(filename, method)
    try:
        yield file
    finally:
        print("exit")
        file.close()




### 

"""
so it basically: conn.cursor() -> Pause -> yield -> finally -> conn.close?


Yes — that's the right idea. Slightly expanded, the exact sequence is:

What runs, step-by-step:

@contextmanager wraps your generator into a context manager implementing __enter__ / __exit__.
Entering with _get_db_cursor(db): executes code up to yield — i.e. 

conn = sqlite3.connect(db_path) — connection opened.
c = conn.cursor() — cursor created.
yield c — generator pauses and hands c to the with ... as cursor: body.
The with block runs (you call execute()/fetchone() etc.) while conn stays open.
When the with block exits (normal return or exception), control resumes the generator right after the yield.
The finally block runs: conn.close() — connection is closed.


"""



@contextmanager
def _get_db_cursor(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        yield conn.cursor()
    finally:
        conn.close()


TESTFUNC_DB = "test.db"


def GetSignalFromDB(project: str, train_type: str, funswidi: str):
    query = (
        "SELECT * FROM signals WHERE project = ? AND train_type = ? AND funswidi = ?"
    )

    with _get_db_cursor(TESTFUNC_DB) as cursor:
        cursor.execute(query, (project, train_type, funswidi))
        row: Optional[tuple] = cursor.fetchone()

        return row[1] if row else ""


def getDictFromSignalDB(query: str, db_path: str, key_col: int, val_col: int):
    signal: dict = {}
    try:
        with _get_db_cursor(db_path) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                signal[row[key_col]] = row[val_col]
    except Exception as e:
        print(f"Error occurred while fetching data from database: {e}")

    return signal

