## Install

Clone this project using git

## Usage

### Run

The `py` and `unitylive2D` folders are the project source code

`Live2D_ V2.0` and `py_ V2.3` Two folders are packaged file folders

**Run: Execute `VtuberLive2D.exe`, then execute `py_ V2.3\dist\main\main.exe`**

**Close: Just close the `VtuberLive2D` window**

Implementation of communication between Python and Unity processes: establish a TCP connection to transfer py data to Unity

### Demo

![](images/1.gif)

![](images/2.gif)



***(If you want to build a Python and Unity development environment, you need to use the following tools)***

### Environmental construction: 

- **Python 3.6**
- **cmake 3.23.0** : Project building tools
- **boost 1.79.0** : C++open source library
- **Dlib 9.0.0** : Open source library for facial recognition
- **OpenCV** : Cross platform computer vision and machine learning software library
- **NumPy** : Python version 3.5 or higher is required. The Python library is mainly used to perform calculations on multidimensional arrays
- **OpenGL 3.1.6** : A software interface for rendering 2D and 3D vector graphics hardware
- **vs2019**

#### Install and configure Python 3.6

Installation website: http://www.python.org/download/

Download Windows x86-64 executable installer

Add environment variables and user variable `path`

For example:
`C:\Users\86177\AppData\Local\Programs\Python\Python36`
`C:\Users\86177\AppData\Local\Programs\Python\Python36\Scripts`

#### Install cmake

Installation website: https://cmake.org/download/ 

#### Install boost

Installation website: http://www.boost.org/users/history/

After decompression, execute `bootstrap. bat` in the Boost directory

After execution, run `b2.exe` in the directory

After these, the boot compilation is completed

Add environment variables and user variable `path`
For example:
`BOOST_ROOT = D:\boost_1_79_0`
`BOOST_LIBRARYDIR = D:\boost_1_79_0\stage\lib`

Compile the Python library 

```
b2 -a --with-python address-model=32 toolset=msvc runtime-link=static
```

#### Install Opencv

```
pip install opencv-python
```

#### Install dlib

In the development of Dlib, the boost library is used, and cmake is used for compilation. Before installing these two libraries, they must be installed first. If they are not installed, errors may occur
```
pip install dlib
```


## Maintainers

[@AiLiAA](https://github.com/AiLiaa)

