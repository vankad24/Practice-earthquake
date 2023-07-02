from loguru import logger

logger.add("./log/error_log.log", level="ERROR")
logger.add("./log/info_log.log", level="INFO")
# logger.add("./log/test_soconds.txt", retention="10 s", level = "INFO")


