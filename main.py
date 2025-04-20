import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import os
import glob
import plotly.express as px

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取监测点元数据
stations = pd.DataFrame({
    "监测点编号": ["1345A","1346A","1348A","1349A","1350A","1351A","1352A",
                "1353A","1354A","1355A","2846A","3298A","3299A","3300A",
                "3301A","3302A","3303A","3304A","3443A","3445A","3446A"],
    "监测点名称": ["广雅中学","市五中","广东商学","市八十六","番禺中学","花都师范",
               "市监测站","九龙镇镇","越湖","帽峰山森","体育西","从化街口",
               "白云竹科","白云嘉禾","黄埔科学","番禺大学","南沙黄阁","南沙街",
               "花都梯面","从化良口","增城荔城"],
    "经度": [113.2347,113.2612,113.3478,113.4332,113.3505,113.2146,113.2597,
          113.5618,113.2765,113.443,113.3221,113.5717,113.3472,113.2981,
          113.4256,113.3942,113.4922,113.5342,113.2902,113.7858,113.8051],
    "纬度": [23.1423,23.105,23.0916,23.1047,22.9483,23.3916,23.1331,23.312,
          23.1544,23.3035,23.1322,23.5491,23.3692,23.237,23.1716,23.0483,
          22.8168,22.7896,23.5544,23.7478,23.2614]
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
numeric_cols = full_df.columns[3:-1].tolist()  # 获取所有监测点列
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
print(merged[:8])

# 绘制每个地点不同污染物的数据图
def plot_pollutants_by_site(df):
    for site in df['监测点名称'].unique():
        site_data = df[df['监测点名称'] == site]
        for pollutant in site_data['type'].unique():
            pollutant_data = site_data[site_data['type'] == pollutant]
            
            plt.figure(figsize=(12, 6))
            plt.scatter(pollutant_data['datetime'], pollutant_data['value'], marker='o', linestyle='-',s=15)
            plt.title(f'{site} - {pollutant} 时间序列')
            plt.xlabel('时间')
            plt.ylabel('浓度值')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            
            # 保存图片到本地
            output_path = f'./img/{site}-{pollutant}.png'
            plt.savefig(output_path)
            plt.close()
            print(f'已保存 {output_path}')
        break

# 执行可视化
plot_pollutants_by_site(merged)
