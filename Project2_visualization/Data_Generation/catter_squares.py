import matplotlib.pyplot as plt

x_values = range(1, 1001)
y_values = [x**2 for x in x_values]

plt.style.use('seaborn-v0_8')
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=10) # 绘制散点图，设置点的大小为10

ax.scatter(x_values, y_values, c=y_values, cmap=plt.cm.Blues, s=10) # 绘制散点图，设置点的颜色映射为蓝色，点的大小为10

# Set chart title and label axes
ax.set_title("Square Numbers", fontsize=24)
ax.set_xlabel("Value", fontsize=14)
ax.set_ylabel("Square of Value", fontsize=14)

# Set size of tick labels
ax.tick_params(axis='both', labelsize=14)

ax.axis([0, 1100, 0, 1100000]) # 设置x轴和y轴的取值范围

plt.show()