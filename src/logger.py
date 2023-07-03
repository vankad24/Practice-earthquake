from loguru import logger


# def my_filter(record):
#     """ Exclude all levels except for INFO """
#     return record["level"].name == "INFO"


logger.add("./log/error_log.log", level="ERROR", rotation="100 MB", retention="10 minutes")
logger.add("./log/info_log.log", level="INFO", rotation="100 MB", retention="10 minutes")
# logger.add("./log/info_log.log", filter=my_filter, level="INFO")
# logger.add("./log/test_soconds.txt", retention="10 s", level = "INFO")


