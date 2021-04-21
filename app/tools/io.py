import os
import uuid
import errno
import pathlib
import zipfile


def secure_filename(path, filename=None, ext=None):
    filename = filename or str(uuid.uuid4())
    ext = ext or '.png'
    if not ext.startswith('.'):
        ext = '.' + ext
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return os.path.join(path, filename + ext)


def path_create(path, is_file=False):
    if is_file:
        parent = pathlib.PurePath(path).parent
        pathlib.Path(parent).mkdir(parents=True, exist_ok=True)
        pathlib.Path(path).touch(exist_ok=True)
    else:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def secure_file_exist(filepath):
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        os.open(filepath, flags)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise


def file_walker(path, directory, do_not_delete):
    file_list = []
    if os.path.isdir(path):
        for path, dirs, files in os.walk(path):
            for file in files:
                ext = file.lower().rpartition('.')[-1]
                if ext in 'xml' and file.startswith('SB8'):
                    filename = os.path.join(path, file)
                    file_list.append(filename)
                else:
                    if not do_not_delete:
                        src = os.path.join(path, file)
                        dst = os.path.join(directory['crap'], file)
                        os.replace(src, dst)
    return file_list


def append_to_zip(zip_path, file_path, append_path):
    zf = zipfile.ZipFile(zip_path, mode='a', compression=zipfile.ZIP_LZMA, compresslevel=9)
    arcname = append_path + os.path.basename(file_path)
    zf.write(file_path, arcname)
    zf.close()


def clean_startup(dir_dict):
    for item in dir_dict:
        path_create(dir_dict[item], is_file=False)
