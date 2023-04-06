## 安装

使用git克隆此项目

## 使用

### 运行

其中`py`和`unitylive2D`文件夹是项目源码

`Live2D_V2.0`和`py_V2.3`是已打包文件

**运行：执行 `VtuberLive2D.exe`，再执行 `py_V2.3\dist\main\main.exe`**

**关闭：关闭`VtuberLive2D`窗口即可**

`python`和`unity`进程通信实现：建立TCP连接，将`python`数据传输到`unity`

### 演示

![](images/1.gif)

![](images/2.gif)



***(如果你想搭建python和unity开发环境，需要借助以下工具)***

### Python环境搭建: 

- Python 3.6
- cmake 3.23.0 项目构建工具
- boost 1.79.0 C++开源库
- Dlib 9.0.0 人脸识别的开源库
- OpenCV 跨平台计算机视觉和机器学习软件库
- NumPy 要求python版本在3.5以上.Python库，主要用于对多维数组执行计算
- OpenGL 3.1.6 渲染2D、3D矢量图形硬件的一种软件接口
- vs2019

#### 安装配置Python3.6

安装地址 http://www.python.org/download/

Download Windows x86-64 executable installer

添加环境变量，用户变量`path`

例如：

`C:\Users\86177\AppData\Local\Programs\Python\Python36`
`C:\Users\86177\AppData\Local\Programs\Python\Python36\Scripts`

#### 安装cmake

安装地址 https://cmake.org/download/ 

#### 安装boost

安装地址 http://www.boost.org/users/history/

解压后，在Boost目录，执行bootstrap.bat

执行完后，运行目录下的b2.exe

成功后，booat编译完成

添加环境变量，用户变量`path`

例如:

`BOOST_ROOT = D:\boost_1_79_0`
`BOOST_LIBRARYDIR = D:\boost_1_79_0\stage\lib`

再进行python library的编译
```
b2 -a --with-python address-model=32 toolset=msvc runtime-link=static
```
#### 安装Opencv
```
pip install opencv-python
```
#### 安装dlib

Dlib的开发中使用到boost库，编译时使用cmake，在安装之前要先安装这两样，如果没有安装的话，会报错误
```
pip install dlib
```


## 主要项目负责人

[@AiLiAA](https://github.com/AiLiaa)
