import hashlib


def get_fp_sha256(fp):
    """
    Get the SHA-256 checksum of the data in the file `fp`.
    :param fp: file descriptor
    :type fp: file
    :return: hexdigest
    """
    fp.seek(0)
    hasher = hashlib.sha256()
    while True:
        chunk = fp.read(524288)
        if not chunk:
            break
        hasher.update(chunk)
    return hasher.hexdigest()
