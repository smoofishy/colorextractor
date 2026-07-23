from PySide6.QtCore import QObject, QRunnable, Signal


class CallableThread(QObject, QRunnable):
    """Runs an arbitrary no-arg callable on a QThreadPool worker thread.

    Used to keep slow, blocking work (decoding large photos, quantizing
    colors) off the GUI thread. Results/errors come back as queued signals,
    so slots run on whichever thread this object lives on (the GUI thread,
    as long as it's constructed there).
    """

    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, fn):
        QObject.__init__(self)
        QRunnable.__init__(self)
        self._fn = fn
        # We're a QObject the caller holds a Python reference to (its
        # signals are what deliver the result), so let Python's GC own our
        # lifetime instead of having QThreadPool delete us from a worker
        # thread once run() returns.
        self.setAutoDelete(False)

    def run(self):
        try:
            result = self._fn()
        except Exception as exc:  # noqa: BLE001 - surface any failure to the UI
            self.failed.emit(str(exc))
        else:
            self.succeeded.emit(result)
