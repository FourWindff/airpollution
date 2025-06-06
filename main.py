import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import random

# 读取监测点元数据
stations = pd.DataFrame({
    "监测点编号": ["1345A", "1346A", "1348A", "1349A", "1350A", "1351A", "1352A",
                "1353A", "1354A", "1355A", "2846A", "3298A", "3299A", "3300A",
                "3301A", "3302A", "3303A", "3304A", "3443A", "3445A", "3446A"],
    "监测点名称": ["广雅中学", "市五中", "广东商学", "市八十六", "番禺中学", "花都师范",
               "市监测站", "九龙镇镇", "越湖", "帽峰山森", "体育西", "从化街口",
               "白云竹科", "白云嘉禾", "黄埔科学", "番禺大学", "南沙黄阁", "南沙街",
               "花都梯面", "从化良口", "增城荔城"],
    "经度": [113.2347, 113.2612, 113.3478, 113.4332, 113.3505, 113.2146, 113.2597,
          113.5618, 113.2765, 113.443, 113.3221, 113.5717, 113.3472, 113.2981,
          113.4256, 113.3942, 113.4922, 113.5342, 113.2902, 113.7858, 113.8051],
    "纬度": [23.1423, 23.105, 23.0916, 23.1047, 22.9483, 23.3916, 23.1331, 23.312,
          23.1544, 23.3035, 23.1322, 23.5491, 23.3692, 23.237, 23.1716, 23.0483,
          22.8168, 22.7896, 23.5544, 23.7478, 23.2614]
})

# 读取所有CSV数据文件
all_files = glob.glob("./data/*.csv")
df_list = []

for file in all_files:
    temp_df = pd.read_csv(file, encoding='utf-8-sig')
    temp_df['datetime'] = pd.to_datetime(
        temp_df['date'].astype(str) + temp_df['hour'].astype(str).str.zfill(2),
        format='%Y%m%d%H'
    )
    df_list.append(temp_df)

full_df = pd.concat(df_list, ignore_index=True)

# 数据清洗
numeric_cols = full_df.columns[3:].tolist()  # 获取所有监测点列
full_df[numeric_cols] = full_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# 转换数据为长格式
melted = full_df.melt(
    id_vars=['datetime', 'type'],
    value_vars=numeric_cols,
    var_name='site_id',
    value_name='value'
)

# 合并地理信息
merged = pd.merge(melted, stations, left_on='site_id', right_on='监测点编号')

# Streamlit 应用
st.title('广州空气质量')

# 侧边栏
with st.sidebar:
    st.header('数据选择')

    # 用户可以选择的地点 (单选)
    available_sites = merged['监测点名称'].unique().tolist()
    selected_site = st.selectbox('选择地点', available_sites, index=0)

    # 用户可以选择的污染物 (多选)
    available_pollutants = merged['type'].unique().tolist()
    selected_pollutants = st.multiselect('选择污染物', available_pollutants, default=[available_pollutants[0]])

    # 用户选择图表类型
    chart_type = st.selectbox('选择图表类型', ['scatter', 'line'])

    # 颜色管理
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']  # 预设颜色列表
    pollutant_colors = {}  # 存储污染物和颜色的对应关系

    # 为每个污染物选择颜色
    for pollutant in selected_pollutants:
        if pollutant not in pollutant_colors:
            available_colors = [color for color in colors if color not in pollutant_colors.values()]
            if available_colors:
                default_color = available_colors[0]  # 选择第一个可用颜色
            else:
                default_color = "#{:06x}".format(random.randint(0, 0xFFFFFF))  # 随机生成颜色
            
            pollutant_colors[pollutant] = st.color_picker(f'选择 {pollutant} 的颜色', default_color)

    # 用户选择标记和线型
    selected_marker = st.selectbox('选择标记', ['circle', 'square', 'triangle-up', 'triangle-down', 'cross', 'x', 'diamond'])  # 常用标记
    if chart_type == 'line':
        selected_linestyle = st.selectbox('选择线型', ['solid', 'dash', 'dot', 'dashdot'])  # 常用线型
    else:
        selected_linestyle = None

    # 用户选择散点大小
    if chart_type == 'scatter':
        selected_size = st.slider('选择散点大小', min_value=5, max_value=20, value=10)
    else:
        selected_size = None

# 过滤数据
filtered_data = merged[
    (merged['监测点名称'] == selected_site) &
    (merged['type'].isin(selected_pollutants))
]

# 绘制交互式图表
if not filtered_data.empty:
    if chart_type == 'line':
        fig = px.line(
            filtered_data,
            x='datetime',
            y='value',
            color='type',  # 使用污染物类型作为颜色区分
            hover_data=['监测点名称', 'value'],  # 鼠标悬停时显示的信息
            title=f'{selected_site} - {", ".join(selected_pollutants)}',
            symbol='type',  # 使用污染物类型作为标记区分
            markers=True,  # 显示标记
            line_dash='type',  # 使用污染物类型作为线型区分
            color_discrete_map=pollutant_colors,  # 使用用户选择的颜色
            symbol_sequence=[selected_marker],  # 使用用户选择的标记
            line_dash_sequence=[selected_linestyle] if selected_linestyle else None,  # 使用用户选择的线型
        )
    elif chart_type == 'scatter':
        # 删除 NaN 值
        filtered_data = filtered_data.dropna(subset=['value'])

        fig = px.scatter(
            filtered_data,
            x='datetime',
            y='value',
            color='type',  # 使用污染物类型作为颜色区分
            hover_data=['监测点名称', 'value'],  # 鼠标悬停时显示的信息
            title=f'{selected_site} - {", ".join(selected_pollutants)}',
            symbol='type',  # 使用污染物类型作为标记区分
            color_discrete_map=pollutant_colors,  # 使用用户选择的颜色
            symbol_sequence=[selected_marker],  # 使用用户选择的标记
            size='value',  # 使用 value 作为散点大小
            size_max=selected_size,  # 设置散点最大大小
        )

    st.plotly_chart(fig)
else:
    st.write('没有选择任何数据。')