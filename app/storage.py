from pathlib import Path
import os, secrets
from shutil import rmtree


class ProcessingDirExists(Exception):
	pass


class StorageRootContainsFiles(Exception):
	pass


class ProcessingDirLengthIncorrect(Exception):
	pass


# that's a singltone
class FileStorage():

	__instance = None

	# you may import it from config.py
	STORAGE_PATH = Path("./storage")
	CLEAN_AFTER_SECONDS = 24 * 3600 * 10 	# 10 days
	TOKEN_LENGTH = 16


	def __new__(cls):
		if cls.__instance is None:
			cls.__instance = super(FileStorage, cls).__new__(cls)
		return cls.__instance


	def init_storage(self):
		if not self.STORAGE_PATH.exists():
			os.makedirs(self.STORAGE_PATH)
			return True
		else:
			return False


	def make_processing_dir(self, token: str = None):
		if not token:
			token = secrets.token_hex(self.TOKEN_LENGTH)	# create tokens to identify files
		path = self.STORAGE_PATH / token
		if not path.exists():
			os.makedirs(path)
		else:
			raise ProcessingDirExists
		return token, path


	def validate_storage(self):
		for fname in os.listdir(self.STORAGE_PATH):
			path = self.STORAGE_PATH / fname

			if not path.is_dir():

				raise StorageRootContainsFiles

			else:

				if len(fname) == self.TOKEN_LENGTH:
					pass
				else:
					raise ProcessingDirLengthIncorrect


	# clear dependin on CLEAN_AFTER_SECONDS time
	def clear_storage(self) -> list:
		deleted_tokens = []

		for fname in os.list(self.STORAGE_PATH):
			path = self.STORAGE_PATH / fname
			if time.time() - path.stat.st_ctime > self.CLEAN_AFTER_SECONDS:
				rmtree(path)
				deleted_tokens.append(fname)

		return deleted_tokens




















