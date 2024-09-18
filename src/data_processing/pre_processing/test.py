import numpy as np

def inverse_cdf(u, x_max):
    # 对 f(x) = 1 / (x + 1)^3，累积分布函数 (CDF) 是 F(x) = 1 - 1 / (x + 1)^2
    # 在区间 [0, x_max] 上，累积值 F(x_max) = 1 - 1 / (x_max + 1)^2
    F_max = 1 - 1 / (x_max + 1)**2

    # 归一化均匀分布随机数 u 到 [0, F_max]
    u_scaled = u * F_max

    # 通过逆CDF公式生成随机数: x = (1 / sqrt(1 - u)) - 1
    return (1 / np.sqrt(1 - u_scaled)) - 1

# 生成均匀分布的随机数 u (在区间[0, 1]内)
u = np.random.uniform(0, 1, 100000)

# 通过逆CDF生成对应分布的随机数
random_number = inverse_cdf(u, 0.1)

import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.hist(random_number, bins=500, density=True, alpha=0.6, color='g')
plt.tight_layout()
plt.show()