from typing import Tuple

from scipy.signal import butter, lfilter
from numpy import linalg as LA
from scipy import interpolate
import numpy as np

#巴特沃斯带通滤波器：只保留特定频率范围内的信号，滤除高频噪声和低频漂移。
def butter_bandpass_filter(data: np.ndarray,
                           lowcut: float,
                           highcut: float,
                           fs: int,
                           order=5) -> np.ndarray:
    nyq  = 0.5 * fs# 奈奎斯特频率（采样率的一半）
    low  = lowcut / nyq# 归一化低频截止频率
    high = highcut / nyq# 归一化高频截止频率
    b, a = butter(order, [low, high], btype='band')# 生成滤波器系数 b (分子) 和 a (分母)
    y    = lfilter(b, a, data)
    return np.array(y)

#上采样/插值：使用样条曲线（Spline）将稀疏的温度数据变得平滑、稠密。
#k=2 表示使用二次样条插值。
def upsample(depth: np.ndarray, temp: np.ndarray, space: np.ndarray) -> np.ndarray:
    spline = interpolate.UnivariateSpline(depth, temp, k=2)
    return np.array(spline(space))


#根据热导率(lambda)反算含水率(theta)。
#这里建立了一个二次方程并求解，取实数根中绝对值最小的那个
def calc_theta(target_lamd: float, theta_coef: Tuple[float, float, float]) -> float:
    param_a       = theta_coef[1]**2
    param_b       = -(2*theta_coef[1]*target_lamd-2*theta_coef[0]*theta_coef[1]+theta_coef[2]**2)
    param_c       = (target_lamd-theta_coef[0])**2
    theta_dual    = np.roots([param_a, param_b, param_c])# 求解一元二次方程的根
    predict_theta = min(abs(np.real(theta_dual[0])), abs(np.real(theta_dual[1])))# 预测的 theta 取两个根中实部绝对值最小的一个
    return predict_theta


#损失函数：用于衡量预测值与实际值之间的“差距”。
#包含了：1. 温度误差(RMSE)  2. 含水率误差(MAE)  3. 热导率的平滑性约束
def loss(predict_y: np.ndarray,
         y: np.ndarray,
         target_lamd: float,
         theta: float,
         theta_coef: Tuple[float, float, float],
         lamd=None,
         alpha=0.7,
         beta=0.2,
         gamma=0.1):
    temp_rmse     = np.sqrt(LA.norm(predict_y - y)**2/len(y))# 1. 计算温度的均方根误差 (RMSE)
    vwc_mae       = abs(calc_theta(target_lamd, theta_coef) - theta)# 2. 计算含水率的平均绝对误差 (MAE)
    # minimize distance between lamds
    lamd_residual = 0 if lamd is None else np.sqrt(LA.norm(lamd[1:] - lamd[:-1])**2/(len(lamd) - 1))# 3. 计算热导率的变化残差（防止参数变动剧烈，起平滑作用）
    loss          = alpha * temp_rmse + beta * 10 * vwc_mae + gamma * lamd_residual# 加权求和得到最终 Loss
    return loss


#前向物理过程模拟：这是一个数值模拟核心，基于热传导方程。
#使用有限差分法（Finite Difference Method）推导每一时刻的温度分布
def forward(x: np.ndarray,
            init_data: np.ndarray,
            raw_data: np.ndarray,
            delta_x: float,
            delta_time: float,
            mid: int,
            cp: float,
            cw: float,
            cv: float):
    data      = init_data.copy() # 初始状态拷贝
    lamd      = x[:-2]  # 待优化参数：热导率
    qL        = x[-2]   # 待优化参数：液体通量
    qV        = x[-1]   # 待优化参数：气体通量
    llength   = len(lamd)
    dlength   = raw_data.shape[0] # 时间步长总数
    a         = np.zeros((llength - 1, llength - 1)) # 系数矩阵 A
    b         = np.zeros((llength - 1,))             # 向量 b
    predict_y = np.zeros((dlength, ))

    flat_a = a.ravel()
    flat_a[::llength]            = np.hstack((1+(lamd[2:]+2*lamd[1:-1]+lamd[:-2])*delta_time/(4*cp*delta_x**2), -1)) # type: ignore
    flat_a[1::llength]           = -(lamd[1:-1]+lamd[2:])*delta_time/(4*cp*delta_x**2)+(cw*qL+cv*qV)*delta_time/(4*delta_x*cp)  # type: ignore
    flat_a[llength - 1::llength] = np.hstack((-(lamd[2:-1]+lamd[1:-2])*delta_time/(4*cp*delta_x**2)-(cw*qL+cv*qV)*delta_time/(4*delta_x*cp), 1))  # type: ignore
    
    for i in range(dlength - 1):# 随时间步迭代求解
        b[:-1]        = delta_time/(4*cp*delta_x**2)*((lamd[2:]+lamd[1:-1])*(data[2:-1] - data[1:-2])-(lamd[1:-1]+lamd[:-2])*(data[1:-2]-data[:-3]))+data[1:-2]-(cw*qL+cv*qV)*delta_time/(4*delta_x*cp)*(data[2:-1]-data[:-3])  # type: ignore
        b[0]         += ((lamd[1] + lamd[0]) * delta_time / (4 * cp * delta_x ** 2) + (cw * qL + cv * qV) * delta_time / (4 * delta_x * cp)) * raw_data[i+1, 0]
        temp_i        = LA.lstsq(a, b, rcond=None)[0].reshape((-1))
        data[1 : -1]  = temp_i
        data[0]       = raw_data[i + 1, 0]
        data[llength] = raw_data[i + 1, 2]
        predict_y[i]  = temp_i[mid - 1]
    
    predict_y[-1] = predict_y[-2]
    
    return predict_y
