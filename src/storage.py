import time
from pathlib import Path
import os
import secrets
import shutil

from fastapi import UploadFile


class ProcessingDirExists(Exception):
    pass

class StorageRootContainsFile(Exception):
    pass

class ProcessingDirLengthError(Exception):
    pass

class FileStorage:
    __instance = None

    STORAGE_PATH = Path("./static/files")
    CLEAN_AFTER_SECONDS = 60 * 60 * 24 * 10

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(FileStorage, cls).__new__(cls)
        return cls.__instance

    def init_storage(self):
        if not self.STORAGE_PATH.exists():
            os.makedirs(self.STORAGE_PATH)
            return True
        return False

    def create_user_folder(self, uid: int):
        pth = self.STORAGE_PATH / str(uid)
        os.makedirs(pth)

    # В разработке)))
    # def validate_storage(self):
    #     for file in os.listdir(self.STORAGE_PATH):
    #         pth = self.STORAGE_PATH / file
    #         if not pth.is_dir():
    #             raise StorageRootContainsFile()
    #         elif len(fname) != self.TOKEN_LENGTH:
    #             raise ProcessingDirLengthError()

    def clear_storage(self):
        deleted_tokens = []
        for file in os.listdir(self.STORAGE_PATH):
            pth = self.STORAGE_PATH / file
            if time.time() - pth.stat().st_ctime > self.CLEAN_AFTER_SECONDS:
                shutil.rmtree(pth)
                deleted_tokens.append(file)
        return deleted_tokens

    async def save_uploaded_file(self, user_id, file: UploadFile):
        contents = await file.read()
        with open(self.STORAGE_PATH / str(user_id) / file.filename, 'wb') as f:
            f.write(contents)
        await file.close()

