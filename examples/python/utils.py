import logging, os

def get_logger(name, log_to_file=True, logger_file=None):
    logging.basicConfig(level = logging.INFO)
    logger = logging.Logger(name)

    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)

    if log_to_file:
        logger.addHandler(ch)
        logger.propagate = False
        if not logger_file:
            logger_file = name + ".log"

        # Hacky way to clear file
        open(logger_file, 'w').close()

        ch_file = logging.FileHandler(logger_file)
        ch_file.setLevel(level = logging.INFO)
        ch_file.setFormatter(formatter)
        logger.addHandler(ch_file)

    logger.setLevel(level=logging.INFO) # Root level
    return logger
