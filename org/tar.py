import tarfile


class Tar(tarfile.TarFile):
    def read(self, name, encoding="utf-8"):
        res = self.extractfile(self.getmember(name)).read()
        if encoding is not None:
            res = res.decode(encoding)
        return res


def tar_read_file_member(filename, *args, **kwargs):
    with Tar.open(filename) as tar:
        res = tar.read(*args, **kwargs)
    return res
