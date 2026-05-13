import logging
from logging import StreamHandler
from contextlib import contextmanager

from tuflow.pt.pytuflow import pytuflow_logging


class CustomLoggingHandler(StreamHandler):
    """Custom log handler so that logging can be checked. Use global instance below."""

    def __init__(self):
        super().__init__()
        self.msg_filters = []
        self.msg_count = 0
        self.caught_messages = []
        self.use_filter = False

    @contextmanager
    def catch(self):
        with self.catch_with_filter(None) as handler:
            handler.use_filter = False
            yield handler

    @contextmanager
    def catch_with_filter(self, msgs):
        """Use a context manager so that the previous handlers can be restored no matter how the test exits."""
        self.use_filter = True
        if msgs is None:
            self.msg_filters = None
        else:
            self.msg_filters = msgs.copy()
        logger = pytuflow_logging.get_logger()
        tmf_logger = logging.getLogger('tmf')
        viewer_logger = logging.getLogger('tuflow_viewer')
        exist_hdlrs = logger.handlers.copy()
        for hdlr in exist_hdlrs:
            logger.removeHandler(hdlr)
        tmf_handlers = tmf_logger.handlers.copy()
        for hdlr in tmf_handlers:
            tmf_logger.removeHandler(hdlr)
        viewer_handlers = viewer_logger.handlers.copy()
        for hdlr in viewer_handlers:
            viewer_logger.removeHandler(hdlr)
        logger.addHandler(self)
        tmf_logger.addHandler(self)
        viewer_logger.addHandler(self)
        yield self
        logger.removeHandler(self)
        tmf_logger.removeHandler(self)
        viewer_logger.removeHandler(self)
        for hdlr in exist_hdlrs:
            logger.addHandler(hdlr)
        for hdlr in tmf_handlers:
            tmf_logger.addHandler(hdlr)
        for hdlr in tmf_handlers:
            viewer_logger.addHandler(hdlr)
        if self.msg_filters is not None:
            self.msg_filters.clear()
        self.msg_count = 0
        self.caught_messages.clear()

    def handle(self, record):
        if not self.use_filter or (self.msg_filters and record.msg in self.msg_filters):
            self.msg_count += 1
            self.caught_messages.append(record.msg)
        else:
            super().handle(record)


custom_log_handler = CustomLoggingHandler()
