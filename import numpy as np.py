import numpy as np

# 加载结果文件
res = np.load('out.npz')

# 查看里面包含哪些数据键值
print("包含的数据项:", res.files) 

# 获取具体数值
lambdas = res['lambdas']  # 热导率
flux = res['flux']        # 液态水通量 (m/s)
vflux = res['vflux']      # 汽态水通量 (m/s)

# 打印前几个结果看看
print("前五个液态水通量 (m/s):", flux[:5])

import pandas as pd
df = pd.DataFrame({
    'water_flux_ms': flux,
    'vapor_flux_ms': vflux
})
df.to_csv('result_export.csv', index=False)
print("结果已保存为 result_export.csv")


import numpy as np
import matplotlib.pyplot as plt

# 1. 加载数据
res = np.load('out.npz')
# 模型输出的单位通常是 m/s，我们将其转换为更易读的 cm/h
flux_cm_h = res['flux'] * 100 * 3600 
vflux_cm_h = res['vflux'] * 100 * 3600

# 2. 设置绘图风格
plt.figure(figsize=(10, 6))
plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文
plt.rcParams['axes.unicode_minus'] = False 

# 3. 绘制液态水通量 (Water Flux)
plt.plot(flux_cm_h, label='液态水通量 (Water Flux)', color='blue', linewidth=1.5)

# 4. 绘制汽态水通量 (Vapor Flux)
plt.plot(vflux_cm_h, label='汽态水通量 (Vapor Flux)', color='red', linestyle='--', linewidth=1.5)

# 5. 图表修饰
plt.title('土壤水通量随时间变化曲线', fontsize=14)
plt.xlabel('时间步长 (Time Steps)', fontsize=12)
plt.ylabel('通量 (Flux) [cm/h]', fontsize=12)
plt.legend()
plt.grid(True, linestyle=':', alpha=0.6)

# 6. 保存图片并显示
plt.savefig('flux_comparison.png', dpi=300)
print("可视化图表已保存为: flux_comparison.png")
plt.show()