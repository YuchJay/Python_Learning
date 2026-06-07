import os
from pyvis.network import Network

# 1. 初始化网络对象（设置宽高和背景色）
net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

# 2. 配置物理引擎（让节点具备弹簧飘动特效，鼠标拖拽时非常解压）
net.barnes_hut()

# 配置一些参数
net.set_options("""
var options = {
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -5000,
      "centralGravity": 0.1,
      "springLength": 220,
      "springConstant": 0.04,
      "damping": 0.09,
      "avoidOverlap": 1
    },
    "minVelocity": 0.75
  },
  "nodes": {
    "font": {
      "size": 14,
      "strokeWidth": 2,
      "strokeColor": "#222222"
    }
  },
  "edges": {
    "font": {
      "size": 11,
      "align": "middle"
    },
    "smooth": {
      "type": "dynamic"
    }
  },
  "manipulation": {
    "enabled": true,
    "initiallyActive": true
  }
}
""")

# 3. 定义节点数据（包含信号与系统的核心概念）
# 我们可以通过不同颜色（color）来区分“域”、“变换”和“系统特性”
nodes = [
    # 域 (Domain) - 蓝色
    {"id": "Time_Continuous", "label": "连续时间域 (t)", "color": "#1E90FF", "size": 30},
    {"id": "Time_Discrete", "label": "离散时间域 (n)", "color": "#1E90FF", "size": 30},
    {"id": "Freq_Continuous", "label": "连续频域 (Ω)", "color": "#00BFFF", "size": 30},
    {"id": "Freq_Discrete", "label": "离散频域 (ω)", "color": "#00BFFF", "size": 30},
    {"id": "S_Domain", "label": "s复频域 (拉氏平面)", "color": "#4169E1", "size": 35},
    {"id": "Z_Domain", "label": "z复频域 (Z平面)", "color": "#4169E1", "size": 35},
    
    # 数学变换 (Transforms) - 红色
    {"id": "FT", "label": "傅里叶变换 (FT)", "color": "#FF4500", "size": 40},
    {"id": "FS", "label": "傅里叶级数 (FS)", "color": "#FF6347", "size": 35},
    {"id": "DTFT", "label": "离散时间傅里叶变换\n(DTFT)", "color": "#FF4500", "size": 40},
    {"id": "DFT", "label": "离散傅里叶变换\n(DFT/FFT)", "color": "#FF7F50", "size": 35},
    {"id": "LT", "label": "拉普拉斯变换 (LT)", "color": "#FF1493", "size": 45},
    {"id": "ZT", "label": "Z变换 (ZT)", "color": "#FF1493", "size": 45},
    
    # 核心性质与应用 - 绿色
    {"id": "ROC", "label": "收敛域 (ROC)", "color": "#32CD32", "size": 25},
    {"id": "Stability", "label": "系统稳定性", "color": "#32CD32", "size": 25},
    {"id": "Pole_Zero", "label": "零极点分布", "color": "#2E8B57", "size": 25},
    {"id": "Sampling", "label": "时域抽样定理", "color": "#00FF7F", "size": 25}
]

# 批量添加节点
for node in nodes:
    net.add_node(node["id"], label=node["label"], color=node["color"], size=node["size"])

# 4. 定义边（关系三元组）
edges = [
    # 时域到变换域的映射
    ("Time_Continuous", "FT", "映射到"),
    ("Time_Continuous", "LT", "映射到"),
    ("Time_Discrete", "DTFT", "映射到"),
    ("Time_Discrete", "ZT", "映射到"),
    
    # 变换之间的演变与对偶关系（硬核考点）
    ("FT", "Freq_Continuous", "结果位于"),
    ("DTFT", "Freq_Discrete", "结果位于"),
    ("FT", "LT", "s = jΩ 处的特例"),
    ("DTFT", "ZT", "z = e^(jω) 处的特例 (单位圆)"),
    ("LT", "ZT", "通过冲激响应不变法/双线性变换映射"),
    
    # 频域抽样
    ("DTFT", "DFT", "频域离散抽样得到"),
    ("FS", "FT", "周期信号的傅里叶变换"),
    ("Sampling", "Time_Continuous", "作用于"),
    ("Sampling", "Time_Discrete", "转换至"),
    
    # 性质决定
    ("LT", "ROC", "包含"),
    ("ZT", "ROC", "包含"),
    ("ROC", "Stability", "决定"),
    ("Pole_Zero", "ROC", "边界由其决定"),
    ("Pole_Zero", "Stability", "极点在左半平面/单位圆内")
]

# 批量添加边
for source, to, label in edges:
    net.add_edge(source, to, title=label, label=label, arrows="to")

# 5. 生成本地网页文件并自动打开
output_filename = "signal_system_graph.html"
net.show(output_filename, notebook=False)
print(f"成功！图谱已生成，请在当前目录下双击打开：{output_filename}")