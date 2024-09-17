import numpy as np
import matplotlib.pyplot as plt

# 设置随机数种子以保证结果可重复
np.random.seed(42)

# 生成 N 个随机数
N = 10000

# 从均匀分布生成 y，然后开三次方根得到 x
y = np.random.uniform(0, 1, N)
x = y**(1/3)

# 设置区间宽度
bin_width = 0.05
bins = np.arange(0, 1 + bin_width, bin_width)

# 统计各区间内 x^3 的总合
x_cubed = x**3
hist, _ = np.histogram(x_cubed, bins=bins)

# 绘制结果
plt.figure(figsize=(8, 5))
plt.bar(bins[:-1], hist, width=bin_width, edgecolor='black', align='edge')
plt.xlabel('$x^3$ 区间')
plt.ylabel('频率')
plt.title('$x^3$ 在区间的频率分布')
plt.show()
