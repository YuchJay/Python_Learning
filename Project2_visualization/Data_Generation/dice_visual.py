from plotly.graph_objs import Bar, Layout
from plotly import offline

from Data_Generation.die import Die

# Create one D6 and one D10 die.
die_1 = Die()
die_2 = Die(10)

# Make some rolls, and store results in a list.
results = []
for roll_num in range(50_000):
    result = die_1.roll() + die_2.roll()
    results.append(result)

# Analyze the results.
frequencies = []
max_result = die_1.num_sides + die_2.num_sides
for value in range(1, max_result + 1):
    frequency = results.count(value)
    frequencies.append(frequency)

# Visualize the results.
x_values = list(range(1, max_result + 1))
data = [Bar(x=x_values, y=frequencies)]  # 表示用于绘制条形图的数据

x_axis_config = {"title": "Result", "dtick": 1} # 显示每个刻度值
y_axis_config = {"title": "Frequency of Result"}
my_layout = Layout(
    title="Results of rolling one D6 and one D10 50,000 times",
    xaxis=x_axis_config,
    yaxis=y_axis_config,
)  # 返回一个指定图表布局和配置的对象
offline.plot({"data": data, "layout": my_layout}, filename="Data_Generation/d6_d10.html")
