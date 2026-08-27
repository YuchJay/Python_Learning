from plotly.graph_objs import Bar, Layout
from plotly import offline

from Data_Generation.die import Die

# Create a D6 die.
die = Die()

# Make some rolls, and store results in a list.
results = []
for roll_num in range(1000):
    result = die.roll()
    results.append(result)

# Analyze the results.
frequencies = []
for value in range(1, die.num_sides + 1):
    frequency = results.count(value)
    frequencies.append(frequency)

# Visualize the results.
x_values = list(range(1, die.num_sides + 1))
data = [Bar(x=x_values, y=frequencies)]  # 表示用于绘制条形图的数据

x_axis_config = {"title": "Result"}
y_axis_config = {"title": "Frequency of Result"}
my_layout = Layout(
    title="Results of rolling one D6 1000 times",
    xaxis=x_axis_config,
    yaxis=y_axis_config,
)  # 返回一个指定图表布局和配置的对象
offline.plot({"data": data, "layout": my_layout}, filename="Data_Generation/d6.html")
