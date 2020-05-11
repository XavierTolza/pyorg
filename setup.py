from setuptools import setup
import os
import re
from multiprocessing import cpu_count
from os import listdir
from os.path import join
from distutils.extension import Extension

DEBUG = os.environ.get("DEBUG")
DEBUG = DEBUG is not None and DEBUG == "1"
if DEBUG:
    print("Debug enabled")

base_folder = "pyorg"
name = base_folder

kwargs = {}
try:
    import numpy

    numpy_include_path = numpy.get_include()
except ImportError:
    import sys

    numpy_include_path = join(sys.executable, "site-packages/numpy/core/include/numpy")


def generate_extensions(filenames):
    extra_compile_args = ['-fopenmp']
    if DEBUG:
        extra_compile_args.append("-O0")
    extensions = [Extension(join(base_folder, i.split(".")[0]).replace("/", "."), [join(base_folder, i)],
                            language="c++",
                            extra_compile_args=extra_compile_args,
                            include_dirs=[numpy_include_path],
                            extra_link_args=['-fopenmp'])
                  for i in filenames]
    return extensions


files = listdir(base_folder)
try:
    from Cython.Build import cythonize

    r = re.compile(".+\.pyx")
    try:
        cython_files = [i for i in listdir(base_folder) if r.fullmatch(i) is not None]
    except AttributeError:
        cython_files = [i for i in listdir(base_folder) if r.match(i) is not None]
    if len(cython_files):
        extensions = generate_extensions(cython_files)
        kwargs.update(dict(
            ext_modules=cythonize(extensions, annotate=True, gdb_debug=DEBUG, nthreads=cpu_count())
        ))
except ImportError:
    # Cython not present, compiling C files
    r = re.compile(".+\.c(pp)?")
    c_files = [i for i in files if r.fullmatch(i)]
    extensions = generate_extensions(c_files)
    kwargs.update(dict(
        ext_modules=extensions,
    ))

# Load requirements
with open("requirements.txt", "r") as fp:
    requirements = fp.read().splitlines()

required = []
EGG_MARK = '#egg='
for line in requirements:
    if line.startswith('-e git:') or line.startswith('-e git+') or \
            line.startswith('git:') or line.startswith('git+'):
        if EGG_MARK in line:
            package_name = line[line.find(EGG_MARK) + len(EGG_MARK):]
            required.append(f"{package_name} @ {line.split(EGG_MARK)[0]}")
            # dependency_links.append(line)
        else:
            raise ValueError('Dependency to a git repository should have the format:\n'
                             'git+ssh://git@github.com/xxxxx/xxxxxx#egg=package_name')
    else:
        required.append(line)

setup(
    name=name,
    version='1.0',
    description='Simple tool library to use python in Emacs ORGmode',
    author='Xavier Tolza',
    author_email='tolza.xavier@gmail.com',
    packages=[base_folder],
    install_requires=required,
    **kwargs
)

# Pour compiler: python setup.py build_ext --inplace
