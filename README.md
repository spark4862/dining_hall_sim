# 食堂排队模拟系统
这是一个使用salabim库构建的食堂排队模拟系统，具有完整的二维动画可视化功能。


## 文件说明
- `main.py`: 主程序，包含完整的模拟功能和动画（已合并原demo_animation.py的功能）
- `instruction.md`: ai提示词
- `README.md`: 本文件，使用说明

## 核心组件

### 1. AnimationManager类
负责管理所有动画元素的创建和更新：
- 创建静态元素（窗口、入口、出口、图例）
- 创建和管理学生动画对象
- 处理动画颜色和位置变化

### 2. Student类
模拟单个学生的行为：
- 根据概率选择窗口
- 移动到队列位置
- 排队等待服务
- 接受服务后离开
- 支持完整的动画展示

### 3. StudentGenerator类
负责持续生成学生实例：
- 按照指数分布的时间间隔生成学生
- 可配置的到达频率

### 4. CanteenSimulation类
主要的模拟管理器：
- 初始化模拟环境
- 管理资源和统计
- 支持多种运行模式
- 收集和报告统计结果

## 动画功能详解

### 动画元素说明

程序运行时会显示一个动画窗口，包含以下元素：

#### 静态元素（固定不动的）
1. **绿色入口区域**：学生进入食堂的地方，位于屏幕底部中央
2. **蓝色窗口区域**：各个售餐窗口，显示窗口名称
3. **标题**：显示"Dining Hall Queue Simulation"

#### 动态元素（会移动的）
1. **学生矩形**：
   - **蓝色矩形**：学生从入口移动到队列的过程
   - **红色矩形**：学生移动到队列尾部的过程
   - **黄色矩形**：学生在队列中等待（通过AnimateQueue显示）

#### 信息显示
每个窗口旁边会显示实时信息：
- 窗口名称（如：snack、dumplings、noodles）
- Queue: X（当前排队人数）
- Serving: X（当前正在服务人数）
- Capacity: X（窗口总容量）

### 动画配置参数

在 `SimulationConfig` 类中可以调整动画参数：

```python
class SimulationConfig:
    def __init__(self) -> None:
        # 动画开关
        self.animation_enabled: bool = True  # True=显示动画，False=纯数据模拟
        
        # 动画速度（数字越大播放越快）
        self.animation_speed: float = 8
        
        # 动画窗口大小
        self.animation_width: int = 1600    # 窗口宽度（像素）
        self.animation_height: int = 1000   # 窗口高度（像素）
        
        # 视频录制
        self.record: bool = False  # True=录制成video.mp4文件
        
        # 移动时间控制
        self.entrance_to_queue_time: float = 27.0  # 入口到队列底部时间（秒）
        self.queue_to_tail_time: float = 3.0       # 移动到队列尾部时间（秒）
        
        # 队列容量
        self.queue_capacity: int = 8  # 每个队列最多排队人数
```

### 动画使用技巧

#### 技巧1：调整播放速度
```python
# 慢速观察（适合理解流程）
self.animation_speed = 2

# 正常速度
self.animation_speed = 8  

# 快速模拟（适合长时间测试）
self.animation_speed = 32
```

#### 技巧2：录制视频
```python
# 开启录制
self.record = True
self.simulation_duration = 60 * 2  # 录制2分钟

# 运行后会生成video.mp4文件
```

#### 技巧3：调整窗口大小
```python
# 小窗口（适合笔记本）
self.animation_width = 1200
self.animation_height = 800

# 大窗口（适合大屏幕）
self.animation_width = 1920
self.animation_height = 1080
```

#### 技巧4：关闭动画提高性能
```python
# 关闭动画，快速获得结果
self.animation_enabled = False
self.simulation_duration = 60 * 60  # 可以设置更长时间
```

## 使用方法

### 快速开始（5分钟上手）

1. **确保已安装Python和依赖包**（见上方安装指南）

2. **下载并运行**
   ```bash
   # 在项目文件夹中打开命令行
   python main.py
   ```

3. **观察结果**
   - 如果开启动画：会弹出动画窗口显示学生移动过程
   - 程序结束后会在命令行显示统计结果

### 详细使用说明

#### 第一次运行
```bash
# 进入项目文件夹
cd /path/to/dining_hall_sim

# 运行程序
python main.py
```

**期望输出：**
```
>>> 食堂排队模拟系统 <<<
--- 使用默认配置运行 ---
开始模拟，时长: 600sec
------------------------------------------------------------
模拟配置:
  - 窗口: snack, 数量: 3, 服务时间: 70sec, 选择概率: 45.0%
  ...
```

#### 修改配置进行实验

**实验1：增加窗口数量**
1. 打开 `main.py` 文件
2. 找到 `SimulationConfig` 类中的 `windows_setup`
3. 修改某个窗口的 `num_windows` 数值：
   ```python
   {
       "name": "snack",
       "service_time": 70,
       "probability": 0.45,
       "num_windows": 5  # 从3改为5
   }
   ```
4. 保存文件并重新运行

**实验2：调整学生到达频率**
```python
# 找到这一行并修改
self.inter_arrival_time: float = 3  # 从5改为3，学生来得更频繁
```

**实验3：关闭动画进行快速测试**
```python
self.animation_enabled: bool = False  # 改为False
self.simulation_duration: int = 60 * 60  # 增加到1小时
```

### 常见使用场景

#### 场景1：优化窗口配置
**目标：**找到最优的窗口数量配置，使平均等待时间最短

**步骤：**
1. 记录当前配置的平均等待时间
2. 逐一增加热门窗口的数量
3. 对比结果，选择等待时间最短的配置

**示例：**
```python
# 配置A：基础配置
"snack": {"num_windows": 3}
"dumplings": {"num_windows": 2} 
"noodles": {"num_windows": 1}
# 结果：平均等待38.5秒

# 配置B：增加热门窗口
"snack": {"num_windows": 4}  # +1
"dumplings": {"num_windows": 2}
"noodles": {"num_windows": 1}
# 结果：平均等待28.3秒 ← 更优

# 配置C：继续增加
"snack": {"num_windows": 5}  # +1
"dumplings": {"num_windows": 2}
"noodles": {"num_windows": 1}
# 结果：平均等待27.8秒 ← 改善不明显，成本效益低
```

#### 场景2：分析高峰时段
**目标：**模拟午餐高峰期的排队情况

**配置：**
```python
self.simulation_duration = 60 * 45        # 45分钟
self.inter_arrival_time = 1               # 每秒来一个学生
self.queue_capacity = 12                  # 允许更长队列
```

#### 场景3：测试新菜品推出
**目标：**假设推出新菜品，分析对现有排队的影响

**配置：**
```python
self.windows_setup = [
    {"name": "传统菜", "service_time": 50, "probability": 0.4, "num_windows": 2},
    {"name": "新菜品", "service_time": 60, "probability": 0.3, "num_windows": 1},  # 新增
    {"name": "快餐", "service_time": 30, "probability": 0.3, "num_windows": 2}
]
```



#### 问题3：配置错误
**错误信息：**`ValueError: 所有窗口的概率之和必须为1`
**解决方法：**检查所有窗口的probability值相加是否等于1.0
```python
# 错误示例（和为0.9）
"probability": 0.4,  # 窗口1
"probability": 0.3,  # 窗口2  
"probability": 0.2,  # 窗口3
# 总和 = 0.9 ≠ 1.0

# 正确示例（和为1.0）
"probability": 0.5,  # 窗口1
"probability": 0.3,  # 窗口2
"probability": 0.2,  # 窗口3  
# 总和 = 1.0 ✓
```

#### 问题4：结果看不懂
**解决方法：**重点关注这几个指标：
- **平均等待时间**：数值越小越好
- **利用率**：接近100%最理想，超过100%说明排队严重
- **队列长度**：数值越小说明排队越少

### 进阶技巧

#### 技巧1：批量测试多种配置
创建测试脚本：
```python
def test_multiple_configs():
    configs = [
        {"snack_windows": 3, "dumplings_windows": 2},
        {"snack_windows": 4, "dumplings_windows": 2}, 
        {"snack_windows": 3, "dumplings_windows": 3},
    ]
    
    for config in configs:
        print(f"测试配置：snack={config['snack_windows']}, dumplings={config['dumplings_windows']}")
        # 运行模拟...
        # 记录结果...
```

#### 技巧2：导出结果到文件
```python
# 在_collect_results方法中添加：
import json
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

#### 技巧3：可视化结果对比
```python
# 安装matplotlib：pip install matplotlib
import matplotlib.pyplot as plt

# 绘制等待时间对比图
waiting_times = [38.5, 28.3, 27.8]  # 不同配置的等待时间
configs = ['配置A', '配置B', '配置C']
plt.bar(configs, waiting_times)
plt.ylabel('平均等待时间(秒)')
plt.title('不同配置的等待时间对比')
plt.show()
```




## 详细安装和使用指南

见salabim文档

### 第四步：下载项目文件

1. 下载项目的所有文件到一个文件夹中
2. 确保以下文件在同一目录下：
   - `main.py`
   - `instruction.md`
   - `README.md`

### 第五步：运行程序

在项目文件夹中打开命令行，输入：

```bash
python main.py
# 或者
python3 main.py
```

## 配置详解

### 基础配置参数

程序的所有配置都在 `main.py` 文件的 `SimulationConfig` 类中。以下是主要配置参数的详细说明：

#### 1. 时间配置
```python
# 模拟总时长（秒）
self.simulation_duration: int = 60 * 10  # 10分钟

# 学生到达间隔时间（秒）
self.inter_arrival_time: float = 5  # 平均每5秒来一个学生
```

#### 2. 动画配置
```python
# 是否启用动画
self.animation_enabled: bool = True  # True=显示动画, False=纯数据模拟

# 动画播放速度
self.animation_speed: float = 8  # 数值越大播放越快

# 动画窗口大小
self.animation_width: int = 1600   # 窗口宽度
self.animation_height: int = 1000  # 窗口高度

# 是否录制视频
self.record: bool = False  # True=录制为video.mp4文件
```

#### 3. 队列配置
```python
# 每个窗口最大排队人数
self.queue_capacity: int = 8

# 移动时间配置
self.entrance_to_queue_time: float = 27.0  # 入口到队列底部时间（秒）
self.queue_to_tail_time: float = 3.0       # 到达队列尾部时间（秒）
```

#### 4. 窗口配置
```python
self.windows_setup: List[Dict[str, Any]] = [
    {
        "name": "snack",        # 窗口名称
        "service_time": 70,     # 服务时间（秒）
        "probability": 0.45,    # 学生选择概率（45%）
        "num_windows": 3        # 窗口数量
    },
    {
        "name": "dumplings",
        "service_time": 40,
        "probability": 0.37,
        "num_windows": 2
    },
    {
        "name": "noodles",
        "service_time": 40,
        "probability": 0.18,
        "num_windows": 1
    }
]
```

### 自定义配置示例

#### 示例1：快速测试配置
```python
# 在SimulationConfig类的__init__方法中修改：
self.simulation_duration = 60 * 2        # 2分钟快速测试
self.inter_arrival_time = 2              # 学生来得更频繁
self.animation_speed = 16                # 动画更快
```

#### 示例2：高峰期配置
```python
self.simulation_duration = 60 * 30       # 30分钟模拟
self.inter_arrival_time = 1              # 每秒来一个学生
self.windows_setup = [
    {
        "name": "rice",
        "service_time": 30,
        "probability": 0.6,
        "num_windows": 5
    },
    {
        "name": "noodles", 
        "service_time": 45,
        "probability": 0.4,
        "num_windows": 3
    }
]
```

#### 示例3：无动画高速模拟
```python
self.animation_enabled = False           # 关闭动画
self.simulation_duration = 60 * 60       # 1小时模拟
self.inter_arrival_time = 0.5            # 学生来得很频繁
```

### 常见配置错误和解决方法

1. **概率和不等于1**
   ```python
   # 错误示例
   "probability": 0.3,  # 第一个窗口
   "probability": 0.4,  # 第二个窗口
   # 总和 = 0.7 ≠ 1.0
   
   # 正确示例
   "probability": 0.3,  # 第一个窗口
   "probability": 0.7,  # 第二个窗口  
   # 总和 = 1.0 ✓
   ```

2. **窗口数量为0**
   ```python
   # 错误
   "num_windows": 0
   
   # 正确
   "num_windows": 1  # 至少要有1个窗口
   ```

3. **服务时间为负数**
   ```python
   # 错误
   "service_time": -10
   
   # 正确
   "service_time": 30  # 必须为正数
   ```

## 运行模式说明

### 1. 默认模式（推荐新手）
```bash
python main.py
```
- 使用预设配置
- 显示动画
- 输出统计结果

### 2. 批量测试模式
修改 `main.py` 底部的 `main()` 函数：
```python
def main() -> None:
    print(">>> 食堂排队模拟系统 <<<")
    
    # 测试多种配置
    configs = [
        {"duration": 300, "arrival": 5},
        {"duration": 300, "arrival": 3},
        {"duration": 300, "arrival": 7}
    ]
    
    for i, config in enumerate(configs):
        print(f"--- 测试配置 {i+1} ---")
        sim_config = SimulationConfig()
        sim_config.simulation_duration = config["duration"]
        sim_config.inter_arrival_time = config["arrival"]
        
        sim = CanteenSimulation(sim_config)
        results = sim.run()
        print_results(results, sim.config.windows_setup)
```

### 3. 无动画模式（适合长时间模拟）
修改配置：
```python
self.animation_enabled = False
self.simulation_duration = 60 * 60  # 1小时
```

## 结果解读

程序运行完成后会显示统计结果：

```
模拟配置:
  - 窗口: snack, 数量: 3, 服务时间: 70sec, 选择概率: 45.0%
  - 窗口: dumplings, 数量: 2, 服务时间: 40sec, 选择概率: 37.0%
  - 窗口: noodles, 数量: 1, 服务时间: 40sec, 选择概率: 18.0%

模拟结果:
  - snack:
    - 窗口容量: 3 个
    - 当前队列长度: 5 人      ← 还在排队的人数
    - 当前服务人数: 3 人      ← 正在被服务的人数  
    - 利用率: 100.00%         ← 窗口使用率
    - 平均等待时间: 45.2 sec  ← 平均排队时间

系统内总人数: 12 人
总体平均等待时间: 38.5 sec
```

### 关键指标说明：
- **利用率**：100%表示窗口满负荷运行，<100%表示有空闲
- **队列长度**：排队人数，数值越高说明窗口不够用
- **平均等待时间**：学生从排队到开始服务的时间
- **总体平均等待时间**：所有窗口的综合等待时间

#

#### 实践：自动化测试脚本
```python
def run_optimization_test():
    """自动测试多种配置找到最优解"""
    best_config = None
    best_wait_time = float('inf')
    
    for snack_count in range(3, 7):  # 测试3-6个snack窗口
        for dumplings_count in range(2, 5):  # 测试2-4个dumplings窗口
            config = create_config(snack_count, dumplings_count)
            result = run_simulation(config)
            
            if result['wait_time'] < best_wait_time:
                best_wait_time = result['wait_time']
                best_config = config
                
    return best_config, best_wait_time
```

