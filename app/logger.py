from loguru import logger
import logging
import os


logger.error("Msg")
logger.critical("Msg")
# logger.add()

path = os.getcwd() + "\\log.txt"
print(path)
id = logger.add(path, filter="__main__", level="INFO", rotation="9 seconds", retention="10 seconds")
print(id)
logger.error("msg")
# logger.remove(1)			# stop writing logs to the specified file

logger.info("aa")

for i in range(1000):
	logger.info(i)









