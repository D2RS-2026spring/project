<img width="1571" height="1197" alt="image" src="https://github.com/user-attachments/assets/a8558e8d-27ea-4e16-b568-af4d660b43db" /># project
* 项目名称：WRR-2023 论文复现
## 小组基本信息

* 施振隆   | 学号：2025303110061 [@flovar](https://github.com/flovar)
* 王羿人   | 学号：2025303120134 [@WYR1016](https://github.com/WYR1016)
* 潘钰烁   | 学号：2025303120124 [@tzy311](https://github.com/tzy311)
* 贾雯偲   | 学号：2025303120143 [@Ccwwjia-032](https://github.com/Ccwwjia-032)
* 刘壮壮   | 学号：2025303110049 [@Leo-hub123](https://github.com/Leo-hub123)   
 

  
## 项目内容

该论文发表在 2023 年的 WRR 杂志上，SU et al.Tracing the Soil Water Flux in Variably Saturated Zones Using Temperature.Water Resources Research 10 April 2023. Data DOI10.1029/2022WR033677

* 原始数据:https://doi.org/10.5281/zenodo.7456823

* 分析代码:https://doi.org/10.5281/zenodo.7456823

* 复现内容：温度-深度时间序列反演饱和带土壤水分垂直通量

* 仓库链接：https://github.com/D2RS-2026spring/project
                     https://d2rs-2026spring.github.io/project/

## 论文内容

* 研究背景：
包气带（Variably saturated zone）是连接地表水和地下水的关键纽带。准确量化其中的水通量对于理解水循环和污染物迁移至关重要。虽然热示踪法在饱和带（如河床）已广泛应用，但在非饱和带，由于含水率变化导致土壤热性质（热容、热导率）动态波动，现有的稳态或简单解析解方法往往难以适用。

* 创新：
引入 L-BFGS-B 算法，通过最小化实测温度与模拟温度的剩余平方和（RSS），反演得出水通量 $q$

* 解决的问题：
如何在高频率波动的水力条件下，利用非侵入式的温度序列准确估算变饱和带的垂直水通量。

* 研究目的：
开发一种基于热传导-平流方程数值逆推的新方法，能够同时处理饱和与非饱和条件，并验证其在实验室尺度和现场应用中的准确性。


## 环境配置

* Python 3.8+
* 主要依赖包
       NumPy 1.20+
       SciPy 1.10+
       Pandas 1.2+
       optimparallel 0.1.2
       pyswarms 1.3.0
* 开发环境 ：VS Code

## 原始数据及代码



## 可复现性
1、准备 csv 数据文件。 VSF 需要四个数据系列。第一到第三列是感兴趣深度处的传感器（编号为 1）以及感兴趣深度上方和下方的两个传感器（编号为 0 和 2）监测的温度，第四列是测量的体积含水量 (VWC, )，其深度可以使用 --depth_vwc 选项指定。

2、在终端中运行以下命令：python main.py <path to csv data file> <depth of sensor 1 and 2 relative to sensor 0 in meters> <time duration between two data records in seconds> --cp<heat capacity of moist soil>
例如：python main.py data.csv 0.25 0.5 1800 --freq 48 --dx 0.01 --cw 3.6e6 --cv 90 --cp 2.8e6 --optim tnc --loss_coef 0.9 0.05 0.05--seed 9000 --filter_outputs

3、输出文件是一个压缩的.npz归档文件，其中包含以下优化参数：lambdas: at each discretized nodes, flux: Liquid water flux, vflux: Vapor flux, 


<img width="880" height="535" alt="Image" src="https://github.com/user-attachments/assets/1230289f-66b6-4c35-8438-12aba1c98488" />

<img width="1571" height="1197" alt="image" src="https://github.com/user-attachments/assets/d4e5298f-731d-4801-a49c-c2686b71cb42" />
实验结果差是因为在整个饱和范围内估算热导率的经验公式使用了默认的参数，实际应用时应根据土壤类型查阅或实验获得参数并插入 --theta_coef_custom b1 b2 b3

<img width="1087" height="774" alt="Image" src="https://github.com/user-attachments/assets/59e23686-efe4-49fe-a743-eebd49239320" />
<img width="1696" height="1072" alt="image" src="https://github.com/user-attachments/assets/22c2a161-96f3-4b45-b079-febd0d490d7d" />
（图7、图8来自论文）
