import pytest
from app.storage import FileStorage, ProcessingDirExists, StorageRootContainsFiles, ProcessingDirLengthIncorrect
import secrets, os


class TestStorage():

	def test_singltone(self):		# test if the class a singltone
		storage1 = FileStorage()
		storage2 = FileStorage()
		assert storage1 is storage2


	def test_init_storage(self):
		storage1 = FileStorage()
		storage1.init_storage()
		assert not storage1.init_storage()


	def test_make_processing_dir(self):
		storage = FileStorage()
		token = secrets.token_hex(storage.TOKEN_LENGTH)
		info = storage.make_processing_dir(token)
		assert info[0] == token
		assert info[1].is_dir()

		info = storage.make_processing_dir()
		assert info[1].is_dir()


	@pytest.mark.xfail(raises=ProcessingDirExists)
	def test_make_processing_dir_fails(self):
			storage = FileStorage()
			token = secrets.token_hex(storage.TOKEN_LENGTH)
			storage.make_processing_dir(token)
			storage.make_processing_dir(token)


	@pytest.fixture(autouse=True)
	def run_around_tests(self):
		path = FileStorage.STORAGE_PATH / "a.txt"
		with open(path, 'w') as f:
			f.write("a")

			yield
		os.remove(path)


	@pytest.mark.xfail(raises=ProcessingDirLengthIncorrect)
	def test_validate_storage(self):
		storage = FileStorage()
		storage.validate_storage()















