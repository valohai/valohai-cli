import hashlib
from typing import BinaryIO


def get_fp_sha256(fp: BinaryIO) -> str:
    """
    Get the SHA-256 checksum of the data in the file `fp`.

    :return: hex string
    """
    fp.seek(0)
    hasher = hashlib.sha256()
    while True:
        chunk = fp.read(524288)
        if not chunk:
            break
        hasher.update(chunk)
    return hasher.hexdigest()
