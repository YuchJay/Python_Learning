import matplotlib.pyplot as plt

input_values = [1, 2, 3, 4, 5]
squares = [1, 4, 9, 16, 25]

plt.style.use('seaborn-v0_8') # 设置绘图风格为seaborn
fig, ax = plt.subplots() # fig表示整张图片，ax表示图片中的各个图表
ax.plot(input_values, squares, linewidth=3) # 绘制折线图，设置线宽为3

# Set chart title and label axes
ax.set_title("Square Numbers", fontsize=24)
ax.set_xlabel("Value", fontsize=14)
ax.set_ylabel("Square of Value", fontsize=14)

# Set size of tick labels
ax.tick_params(axis='both', labelsize=14) # 实参将影响x轴和y轴的刻度标签大小

plt.show()