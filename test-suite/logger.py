from datetime import datetime
import logging
import os
try:
    from http.client import HTTPConnection # py3
except ImportError:
    from httplib import HTTPConnection # py2

logger = logging.getLogger("hawkeye")


def configure_hawkeye_logging(hawkeye_logs_dir, language):
  """
  This function configures hawkeye logger and loggers of some libraries
  to write relevant logs to specific log file located in
  hawkeye_logs_dir.
  Hawkeye logs written by logging framework in contrast to those logs
  which are written manually to report files are aimed to collect debug
  information which can help to understand unexpected failure of testcase.

  Args:
    hawkeye_logs_dir: a string - path to hawkeye logs directory
    language: a string - name of currently testing language
  """
  # Configure simple formatter
  formatter = logging.Formatter("%(levelname)s %(name)s %(message)s")

  # Configure file handler
  file_name = (
    "{lang}-detailed {dt:%Y-%m-%d %H-%M-%S}.log"
    .format(lang=language, dt=datetime.now())
  )
  file_path = os.path.join(hawkeye_logs_dir, file_name)
  handler = logging.FileHandler(file_path)
  handler.setFormatter(formatter)
  handler.setLevel(logging.DEBUG)

  # Configure hawkeye logger
  logger.addHandler(handler)
  logger.setLevel(logging.DEBUG)

  # Other loggers
  requests_logger = logging.getLogger("requests")
  requests_logger.addHandler(handler)
  requests_logger.setLevel(logging.WARN)

