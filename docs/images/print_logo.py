def get_hollow_D(size):
    lines = []
    for i in range(size):
        line = ""
        for j in range(size):
            if (j == 0) or \
               (j == size - 1 and i != 0 and i != size - 1) or \
               ((i == 0 or i == size - 1) and j != size - 1):
                line += "|"
            else:
                line += " "
        lines.append(line)
    return lines

def get_hollow_E(size):
    lines = []
    for i in range(size):
        line = ""
        for j in range(size):
            if j == 0 or i == 0 or i == size // 2 or i == size - 1:
                line += "|"
            else:
                line += " "
        lines.append(line)
    return lines

def get_hollow_M(size):
    lines = []
    for i in range(size):
        line = ""
        for j in range(size):
            if j == 0 or j == size - 1 or (i <= size // 2 and (i == j or j == size - 1 - i)):
                line += "|"
            else:
                line += " "
        lines.append(line)
    return lines

def get_hollow_G(size):
    lines = []
    for i in range(size):
        line = ""
        for j in range(size):
            if (i == 0 and j != 0) or \
               (i == size - 1 and j != 0) or \
               (j == 0 and i != 0 and i != size - 1) or \
               (j == size - 1 and i >= size // 2) or \
               (i == size // 2 and j >= size // 2):
                line += "|"
            else:
                line += " "
        lines.append(line)
    return lines

def get_hollow_e(size):
    lines = []
    for i in range(size):
        line = ""
        for j in range(size):
            if (i == 0 or i == size - 1 or i == size // 2) and (j > 0 and j < size - 1):
                line += "_"
            elif (j == 0 and (i > 0 and i < size - 1)) or (j == size - 1 and (i < size // 2 and i > 0)):
                line += "|"
            else:
                line += " "
        lines.append(line)
    return lines

def get_hollow_n(size):
    lines = []
    for i in range(size):
        line = ""
        for j in range(size):
            if j == 0 or j == size - 1 or (i != 0 and i == j):
                line += "|"
            else:
                line += " "
        lines.append(line)
    return lines

def combine_letters(*letters):
    combined = ["".join(parts) for parts in zip(*letters)]
    return "\n".join(combined)

# 设置字母大小
size = 7

# 获取每个字母的行列表
lines_D = get_hollow_D(size)
lines_E = get_hollow_E(size)
lines_M = get_hollow_M(size)
lines_G = get_hollow_G(size)
lines_e = get_hollow_e(size)
lines_n = get_hollow_n(size)

# 合并字母行
combined_output = combine_letters(lines_D, ["  "] * size, lines_E, ["  "] * size, lines_M, ["  "] * size, lines_G, ["  "] * size, lines_e, ["  "] * size, lines_n)

# 打印结果
print(combined_output)
