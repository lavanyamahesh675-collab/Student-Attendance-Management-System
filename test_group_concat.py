import sqlite3

conn = sqlite3.connect(':memory:')
c = conn.cursor()
c.execute('CREATE TABLE t (id INT, name TEXT)')
c.execute('INSERT INTO t VALUES (1, "Math"), (1, "Physics")')
c.execute("SELECT id, GROUP_CONCAT(name, ', ') FROM t GROUP BY id")
print("GROUP_CONCAT result:", c.fetchall())
