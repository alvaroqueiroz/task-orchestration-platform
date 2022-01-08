import logging
from sys import stdout


def get_std_logger():
    """
    Applies log settings and returns a logging object.
    :flag_stdout: boolean
    :flag_logfile: boolean
    """
    handler_list = list()
    logger = logging.getLogger(__name__)
    [logger.removeHandler(h) for h in logger.handlers]
    handler_list.append(logging.StreamHandler(stdout))
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s - %(message)s",
        handlers=handler_list,
    )
    return logger