There is a [tutorial][openpose-sudo-install] about how to install Openpose if 
you have sudo rights.

This document describes how to install Openpose locally, 
in some `/home/user/XXX` folder, w/o sudo rights.

# Preparation
Before proceeding, a few assumptions:
1. You removed `conda` binaries from your `$PATH` and any conda libs from 
   `$LD_LIBRARY_PATH`. On a number of occasions, I experienced conda files 
   interfering when building things from source. In our particular case, 
   `cmake` and Python headers/libraries may be interfering when installing   
   various dependencies. I used a fresh Python3.8 environment installed 
   using the `pyenv` package.
2. For Slurm users: Openpose installation instructions assume you have a GPU 
   on your machine. This means that if you install it on a remote machine 
   supporting, you need to first launch an interactive job, to login to a 
   node with a GPU.
3. Some of the Openpose dependencies are outdated. For example, installing 
   Caffe with cuDNN support was difficult, because newer versions of cuDNN   
   do not support obsolete class and function declarations. 
   To install cuDNN, follow the installation instructions below.
4. If you have sudo rights, things are much simpler – the necessary 
   dependencies can be installed using the Ubuntu packaging system (sudo apt 
   install XXX). This document assumes that you do not have sudo rights and 
   have to build packages from source. 

## Paths, environment variables and symlinks
In what follows, `$LOCAL_DIR` is an environment variable which denotes a 
folder under `$HOME` (e.g., `$HOME/.local`) which contains folders like 
`bin/`, `lib/`, `include/`which are added to `$PATH`, `$LD_LIBRARY_PATH` or 
`$INCLUDE_DIRS` environment variables, in order for custom packages to be 
discoverable by other packages installed later on. Add the following to your 
`.bashrc` or `.zshrc` dotfiles (depending on whether you use `bash` or `zsh`):
```
export PATH=”$LOCAL_DIR/bin:$PATH”
export LD_LIBRARY_PATH=”$LOCAL_DIR/lib64:$LOCAL_DIR/lib:$LD_LIBRARY_PATH”
```

Each custom package we are going to install will be installed somewhere 
under `$LOCAL_DIR` (the location I use is `$LOCAL_DIR/stow_packages`). After 
installing a package, we create symlinks in `$LOCAL_DIR/bin`, 
`$LOCAL_DIR/lib64` or `$LOCAL_DIR/lib`.We are going to rely on
[GNU Stow][gnu-stow] to create these symlinks. On a high-level, a package 
installation looks like this:
```
wget https:/path/to/some-package.tgz # or pull from GitHub
tar zxvf some-package.tgz 
cd some-package 
./configure –prefix=$LOCAL_DIR/stow_packages/some-package
make 
make install
cd $LOCAL_DIR/stow_packages
stow some-package # this step creates symlinks
```
The last command will create symlinks from 
`$LOCAL_DIR/stow_packages/some-package/bin/` in `$LOCAL_DIR/bin/` and from 
`$LOCAL_DIR/stow_packages/some-package/lib/` in `$LOCAL_DIR/lib/`.

Read GNU Stow documentation for details; you can use any other tool or 
create symlinks manually, if you want, but I found GNU Stow to be very 
helpful in automating this process.

In what follows I will describe only the package installation steps. After 
the package is installed, **do not forget to create the symlinks**!

# Installing dependencies
We will be installing all the dependencies to a local folder and update the 
`$PATH` and `$LD_LIBRARY_PATH` environment variables after each of the tools 
gets installed. Note that after `make install` you can also optionally run 
`make clean`; this will delete the compiled object files which you do not 
need anymore.

## cuDNN
One of Openpose dependencies, Caffe, relies on a very old cuDNN version, and newer 
versions of cuDNN do not support obsolete class and function declarations in 
Caffe. We are going to simpy copy cuDNN library files to a 
local folder.

All possible versions to download are listed [here][cudnn-downloads], but 
the one that worked for me is listed as: `Download cuDNN v5.1 (Jan 20, 2017), 
for CUDA 8.0`. 
Downloading the cuDNN installation files from the Nvidia website is possible 
**after logging into** the Nvidia developer account. The link to the cuDNN 
tarball:
[cudnn-8.0-linux-x64-v5.1-tgz][cudnn-8.0-tgz]. 

Download cuDNN into a local folder. Create a folder where you want cuDNN 
library files to live (e.g., `$LOCAL_DIR/stow_packages/cudnn-8.
0-linux-x64-v5.1`). Unpack the tarball and copy the cuDNN header and library 
files by running the following commands: 

```commandline
cp cudnn-8.0-linux-x64-*/include/cudnn*.h $LOCAL_DIR/stow_packages/cudnn-8.0-linux-x64-v5.1/include 
cp -P cudnn-8.0-linux-x64-*/lib/libcudnn* $LOCAL_DIR/stow_packages/cudnn-8.0-linux-x64-v5.1/lib64 
chmod a+r $LOCAL_DIR/stow_packages/cudnn-8.0-linux-x64-v5.1/include/cudnn*.h $LOCAL_DIR/stow_packages/cudnn-8.0-linux-x64-v5.1/lib64/libcudnn* 
```

Finally, create symbolic links:
```commandline
cd $LOCAL_DIR/stow_packages
stow cudnn-8.0-linux-x64-v5.1 
```

## GFlags
```commandline
git clone https://github.com/gflags/gflags.git
cd gflags && mkdir build && cd build
cmake .. \
    -DCMAKE_INSTALL_PREFIX=$LOCAL_DIR/stow_packages/gflags \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_CXX_FLAGS='-fPIC' 
make 
make install 
(create symlinks) 
```

## Googletest 
```commandline
git clone https://github.com/google/googletest.git -b release-1.12.1
cd googletest 
mkdir build && cd build
cmake .. \
    -DCMAKE_INSTALL_PREFIX=$LOCAL_DIR/stow_packages/googletest-1.12.1 \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_CXX_FLAGS='-fPIC' 
make 
make install 
(create symlinks) 

```

## Libunwind 
```commandline
wget https://github.com/libunwind/libunwind/releases/download/v1.6.2/libunwind-1.6.2.tar.gz
tar zxvf libunwind-1.6.2.tar.gz
cd libunwind-1.6.2
./configure \
    --prefix=$LOCAL_DIR/stow_packages/libunwind-1.6.2 \
    --enable-shared 
make 
make install 
(create symlinks) 
```

## Glog
As of 12.10.2024, master branch ofGlog works with a newer version of Cmake 
(3.22), my system currently has Cmake version 3.16.3. One can either upgrade 
their OS and install the newest Cmake, or just checkout an older commit. I 
tested the installation with the second option and checked out commit 
`05fbc6`.

```commandline
git clone https://github.com/google/glog.git
cd glog 
git checkout 05fbc6
mkdir build && cd build
cmake .. \
   -DCMAKE_INSTALL_PREFIX=$LOCAL_DIR/stow_packages/glog \
   -DUnwind_INCLUDE_DIR=$LOCAL_DIR/include \
   -DUnwind_LIBRARY=$LOCAL_DIR/lib/libunwind-x86_64.so.8 \
   -DGTest_DIR=$LOCAL_DIR/stow_packages/googletest-1.12.1/lib/cmake/GTest \
   -DBUILD_TESTING=OFF \
   -DBUILD_SHARED_LIBS=ON \
   -DCMAKE_CXX_FLAGS='-fPIC' \
   -Dgflags_DIR=$LOCAL_DIR/stow_packages/gflags/lib/cmake/gflags 

make 
make install 
(create symlinks) 
```

## Protobuf
```commandline
wget https://github.com/protocolbuffers/protobuf/releases/download/v21.8/protobuf-cpp-3.21.8.tar.gz
tar zxvf protobuf-cpp-3.21.8.tar.gz
cd protobuf-3.21.8
CFLAGS='-std=c++11 -fPIC' \
    CXXFLAGS='-std=c++11 -fPIC' \
    FFLAGS='-fPIC' \
    FCFLAGS='-fPIC' \
    ./configure \
    --prefix=$LOCAL_DIR/stow_packages/protobuf-3.21.8 \
    --enable-shared=yes

make 
make install 
(create symlinks) 
```

## HDF5
```commandline
git clone https://github.com/mokus0/hdf5.git
cd hdf5
./configure \
   --prefix=$LOCAL_DIR/stow_packages/hdf5 \
   --enable-shared=yes 
make 
make install
(create symlinks) 
```

## lmdb 
```commandline
git clone https://github.com/LMDB/lmdb
cd lmdb/libraries/liblmdb 
```
Modify Makefile by setting the prefix variable to the target location, 
for example, `prefix = $LOCAL_DIR/stow_packages/lmdb`. Then run from the 
command-line:
```commandline
make
make install 
(create symlinks)
```

## OpenBLAS
```commandline
wget https://github.com/xianyi/OpenBLAS/releases/download/v0.3.21/OpenBLAS-0.3.21.tar.gz
tar zxvf OpenBLAS-0.3.21.tar.gz
cd OpenBLAS-0.3.21
make PREFIX=$LOCAL_DIR/stow_packages/oblas-0.3.21 FC=gfortran
make PREFIX=$LOCAL_DIR/stow_packages/oblas-0.3.21 FC=gfortran install 
(create symlinks)
```

## Abseil
```commandline
git clone https://github.com/abseil/abseil-cpp.git
cd abseil-cpp
mkdir build && cd build
cmake .. \
   -DCMAKE_INSTALL_PREFIX=$LOCAL_DIR/stow_packages/abseil \
   -DABSL_LOCAL_GOOGLETEST_DIR=$LOCAL_DIR/stow_packages/googletest-1.12.1 \
   -DABSL_BUILD_TESTING=OFF \
   -DCMAKE_CXX_STANDARD=14 \
   -DABSL_USE_GOOGLETEST_HEAD=ON \
   -DCMAKE_CXX_FLAGS='-fPIC'
make 
make install 
(create symlinks)
```

## OpenCV
For some reason, OpenCV could not find my OpenBlas installation, so I needed 
to export an env var explicitly before building OpenCV:
```commandline
export OpenBLAS_HOME=$LOCAL_DIR/stow_packages/oblas-0.3.21 
```
Then I could proceed to the installation of OpenCV: 
```commandline
mkdir OpenCV && cd OpenCV
wget -O opencv.zip https://github.com/opencv/opencv/archive/4.x.zip 
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.x.zip 
unzip opencv.zip 
unzip opencv_contrib.zip 
mkdir -p build && cd build 
cmake ../opencv-4.x \ 
   -G 'Unix Makefiles' \ 
   -DCMAKE_INSTALL_PREFIX=$LOCAL_DIR/stow_packages/opencv4 \ 
   -DOPENCV_EXTRA_MODULES_PATH=../opencv_contrib-4.x/modules \ 
   -DPYTHON_DEFAULT_EXECUTABLE=$(which python3)\ 
   -DWITH_GTK=ON \ 
   -DWITH_QT=OFF \ 
   -DBUILD_opencv_python2=NO \ 
   -DPYTHON_INCLUDE_DIR=$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
   -DPYTHON_LIBRARY=$(python -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))") 
make -j8 
make install
(create symlinks) 
```

## Boost 
```commandline
wget https://boostorg.jfrog.io/artifactory/main/release/1.80.0/source/boost_1_80_0.tar.gz
tar zxvf boost_1_80_0.tar.gz
cd boost_1_80_0
./bootstrap.sh  --prefix=$LOCAL_DIR/stow_packages/boost-1.80.0 --with-libraries=python,filesystem,thread,system
./b2 headers --prefix=$LOCAL_DIR/stow_packages/boost-1.80.0
./b2 install --prefix=$LOCAL_DIR/stow_packages/boost-1.80.0 
(create symlinks) 
```

## Caffe 
Installation of Caffe involved changing some of the files. I decided to 
fork the original repo and make the changes there. Clone that repo:
```commandline
git clone https://github.com/ypuzikov/caffe/tree/install-for-openpose
```
Modify the `LOCAL_DIR` variable in `Makefile` and `Makefile.config` (to point 
to the location you chose at the beginning of this installation guide). Then 
run `make`. There is no need to follow with `make install` or creating the 
symlinks. 

One Caffe file needs to be created manually (see details [here]
[caffe-proto-issue]). Go the directory you installed Caffe to and create the 
necessary file by running:
```commandline
protoc src/caffe/proto/caffe.proto --cpp_out=.
mkdir include/caffe/proto
mv src/caffe/proto/caffe.pb.h include/caffe/proto/ 
```

## Yaml and libyaml 

### Libyaml 
```commandline
wget http://pyyaml.org/download/libyaml/yaml-0.2.5.tar.gz
tar zxvf yaml-0.2.5.tar.gz
cd yaml-0.2.5
CFLAGS='-fPIC' CXXFLAGS='-fPIC' ./configure \
   --prefix=$LOCAL_DIR/stow_packages/libyaml-0.2.5 \
   --enable-shared=yes 
make 
make install
(create symlinks) 
```

### PyYaml
Install PyYaml for the Python environment (I used the same as the one 
specified in Caffe Makefile.config): 
```commandline
git clone https://github.com/yaml/pyyaml.git
cd pyyaml 
```

Activate your Python environment, install Cython `pip install Cython`, then run:
```commandline
python setup.py --with-libyaml install
```

If it complains about the absence of `yaml.h`, or you get linker errors 
(`cannot find -lyaml`), make sure the header and library files can be found. 
E.g. by adjusting the environment variables:
```commandline
CFLAGS='-I$LOCAL_DIR/include' \
    LDFLAGS='-L$LOCAL_DIR/lib64 -L$LOCAL_DIR/lib' \
    python setup.py --with-libyaml install
```

# Building Openpose (finally)

## Fix CmakeLists.txt
I will assume your Caffe installation resides in `$LOCAL_CAFFE`. Make sure to 
check that this location is set correctly in the CMakeLists.txt in the 
Openpose root directory: 
```commandline
if (Caffe_INCLUDE_DIRS AND Caffe_LIBS AND NOT BUILD_CAFFE)
    set(Caffe_INCLUDE_DIRS "$(LOCAL_CAFFE)/include")
```

## Download pre-trained model files
The URLs to the pre-trained model files have been down for a long time. 
Consider downloading them manually, following the maintainer's comment [here]
[model-files-broken-urls-comment]. 

## Generate Makefile
Once you download the model files and move them into respective folders, you 
are good to proceed with generating a Makefile using CMake. Navigate to the root 
directory of Openpose, create a build directory:
```commandline
mkdir build && cd build
```
Then run CMake:
```commandline
CXXFLAGS='-I/usr/local/cuda/include' \
   LDFLAGS='-pthread  -lpthread' \
   cmake .. -G 'Unix Makefiles' \
   -DBUILD_PYTHON=ON \
   -DCMAKE_INSTALL_PREFIX=$LOCAL_DIR/stow_packages/openpose \
   -DOpenCV_INCLUDE_DIRS=$LOCAL_DIR/include/opencv4 \
   -DCaffe_INCLUDE_DIRS=$LOCAL_CAFFE/include \
   -DCaffe_LIBS=$LOCAL_CAFFE/build/lib/libcaffe.so \
   -DProtobuf_INCLUDE_DIR=$LOCAL_DIR/include \
   -DGFLAGS_INCLUDE_DIR=$LOCAL_DIR/include/gflags/ \
   -DGFLAGS_LIBRARY=$LOCAL_DIR/lib/libgflags.so  \
   -DGLOG_INCLUDE_DIR=$LOCAL_DIR/include/glog \
   -DGLOG_LIBRARY=$LOCAL_DIR/lib/libglog.so \
   -DCUDA_TOOLKIT_INCLUDE=$LOCAL_DIR/include \
   -DCUDNN_ROOT=$LOCAL_DIR/lib64 \
   -DProtobuf_LIBRARIES=$LOCAL_DIR/lib \
   -DBUILD_CAFFE=OFF
```

If you get linking errors, you can try to link the required library by 
modifying the `LDFLAGS` environment variable. Alternatively, you can try to 
create a symlink manually. For example, suppose you get an error stating that `_yaml.
cpython-38-x86_64-linux-gnu.so` library cannot be found: 
```commandline
/usr/bin/ld: cannot find -l_yaml.cpython-38-x86_64-linux-gnu
collect2: error: ld returned 1 exit status
src/openpose/CMakeFiles/openpose.dir/build.make:6070: recipe for target ‘src/openpose/libopenpose.so.1.7.0’ failed
make[2]: *** [src/openpose/libopenpose.so.1.7.0] Error 1
CMakeFiles/Makefile2:658: recipe for target ‘src/openpose/CMakeFiles/openpose.dir/all’ failed
make[1]: *** [src/openpose/CMakeFiles/openpose.dir/all] Error 2
Makefile:135: recipe for target ‘all’ failed
make: *** [all] Error 2 
```

You can solve this by creating a symlink as follows:
```commandline
ln -s \
    $LOCAL_DIR/lib/python3.8/site-packages/yaml/_yaml.cpython-38-x86_64-linux-gnu.so \
    $LOCAL_DIR/lib/lib_yaml.cpython-38-x86_64-linux-gnu.so 
```

If the `cmake ..` command above finishes w/o errors, you can run `make`. Ta-da!
Openpose built :)

## Final steps
If you want to install Openpose-related headers and libraries under the 
location specified by `$DCMAKE_INSTALL_PREFIX`, run the following command:
```commandline
make install 
(create symlinks) 
```

If you want to run Openpose as a standalone application, the last step above 
might not be necessary. The binary executable of Openpose can be found 
here: `$OPENPOSE_PROJECT_DIR./build/examples/openpose/openpose.bin`.

[cuda-8.0]: https://developer.nvidia.com/cuda-80-download-archive
[cudnn-8.0-tgz]: https://developer.nvidia.com/compute/machine-learning/cudnn/secure/v5.1/prod_20161129/8.0/cudnn-8.0-linux-x64-v5.1-tgz
[cudnn-downloads]: https://developer.nvidia.com/cudnn-downloads
[gnu-stow]: https://www.gnu.org/software/stow/
[model-files-broken-urls-comment]: https://github.com/CMU-Perceptual-Computing-Lab/openpose/issues/1602#issuecomment-641653411
[openpose-sudo-install]: https://amir-yazdani.github.io/post/openpose/
[caffe-proto-issue]: https://github.com/muupan/dqn-in-the-caffe/issues/3#issuecomment-70795202