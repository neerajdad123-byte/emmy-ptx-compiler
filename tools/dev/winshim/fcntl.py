"""Windows stand-in for fcntl so the emmy CLI can generate IRs (dev tooling only).
shortcut: locking is a no-op, so never run two emmy processes on the same tune DB at once."""
LOCK_SH, LOCK_EX, LOCK_NB, LOCK_UN = 1, 2, 4, 8
def flock(fd, op): pass
def lockf(fd, cmd, len=0, start=0, whence=0): pass
