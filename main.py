# -*- coding: utf-8 -*-
"""
食堂排队模拟模型

本模块使用 salabim 库建立一个食堂排队系统的模拟模型。
其主要目的是通过调整不同类型窗口的数量配置，来分析学生平均排队等待时间的变化，
从而找到最优的窗口设置方案。

核心组件:
- CanteenSimulation: 模拟的主类，用于整合和运行整个模拟过程。
- Student: 代表进入食堂的学生，定义了其选择窗口、排队、用餐的行为。
- StudentGenerator: 负责按照设定的时间间隔生成学生。
- AnimationManager: 负责管理动画元素的创建和更新。
"""
import salabim
import numpy as np
from typing import List, Dict, Any, Optional, Generator, Final

class SimulationConfig:
    """
    模拟配置类，包含所有可配置参数。
    """
    
    def __init__(self) -> None:
        """初始化配置参数。"""
        # 模拟总时长（sec）
        self.simulation_duration: int = 60 * 4

        self.generator_stop_time: int = 120
        
        # 学生到达食堂的平均时间间隔（sec），服从指数分布
        self.inter_arrival_time: float = 5
        
        # 动画配置
        self.animation_enabled: bool = True
        self.animation_speed: float = 8
        self.animation_width: int = 1600
        self.animation_height: int = 1000
        self.record: bool = False  # 是否记录动画
        
        # 队列配置
        self.queue_capacity: int = 8
        
        # 移动时间配置
        self.entrance_to_queue_time: float = 27.0  # 从入口到队列的移动时间（秒）
        self.queue_to_tail_time: float = 3.0
        
        # 入口位置配置
        self.entrance_position: Dict[str, float] = {
            "x": self.animation_width / 2,  # 屏幕底部中心
            "y": 100
        }
        
        # 窗口配置
        self.windows_setup: List[Dict[str, Any]] = [
            {
                "name": "snack",
                "service_time": 120,
                "probability": 0.45,
                "num_windows": 3
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
        
        # 学生状态颜色配置
        self.student_colors: Dict[str, str] = {
            "waiting": "blue",
            "serving": "green"
        }
        
        # 根据窗口配置自动生成位置
        self.window_positions: Dict[str, Dict[str, float]] = self._generate_window_positions()
    
    def _generate_window_positions(self) -> Dict[str, Dict[str, float]]:
        """
        根据窗口配置自动生成位置。
        
        Returns:
            Dict[str, Dict[str, float]]: 窗口位置字典
        """
        positions = {}
        start_x = 50
        spacing = 150
        y_position = self.animation_height - 200
        
        for i, window_config in enumerate(self.windows_setup):
            positions[window_config["name"]] = {
                "x": start_x + i * spacing,
                "y": y_position
            }
        
        return positions


class AnimationManager:
    """
    动画管理器，负责管理所有动画元素的创建和更新。
    """
    
    def __init__(self, config: SimulationConfig) -> None:
        """
        初始化动画管理器。
        
        Args:
            config (SimulationConfig): 模拟配置对象
        """
        self.config = config
        self.queue_animations: Dict[str, salabim.AnimateQueue] = {}
        self.queue_info_texts: Dict[str, salabim.AnimateText] = {}
    
    def create_static_elements(self) -> None:
        """创建静态动画元素（窗口等）。"""
        # 创建标题
        salabim.AnimateText(
            text="Dining Hall Queue Simulation",
            textcolor="darkblue",
            fontsize=20,
            x=100,
            y=self.config.animation_height - 30,
            font="source sans 3"
        )
        
        # 创建入口
        salabim.AnimateRectangle(
            x=self.config.entrance_position["x"],
            y=self.config.entrance_position["y"],
            spec=(-50, -20, 50, 20),
            fillcolor="green",
        )
        
        salabim.AnimateText(
            text="entrance",
            textcolor="black",
            fontsize=15,
            x=self.config.entrance_position["x"]-40,
            y=self.config.entrance_position["y"],
        )
        
        # 创建窗口和队列
        for window_name, position in self.config.window_positions.items():
            # 窗口主体
            salabim.AnimateRectangle(
                x=position["x"],
                y=position["y"],
                spec=(-10, 10, 90, 50),
                fillcolor="lightblue",
                linecolor="blue",
                linewidth=1,
            )
            
            # 窗口标签
            salabim.AnimateText(
                text=window_name,
                textcolor="black",
                fontsize=15,
                x=position["x"],
                y=position["y"] + 10,
            )

    
    def create_queue_animations(self, windows: Dict[str, salabim.Resource], 
                               queues: Dict[str, salabim.Queue]) -> None:
        """
        创建队列动画。
        
        Args:
            windows (Dict[str, salabim.Resource]): 窗口资源字典
            queues (Dict[str, salabim.Queue]): 排队队列字典
        """
        for window_name, position in self.config.window_positions.items():
            if window_name in windows and window_name in queues:
                resource = windows[window_name]
                queue = queues[window_name]
                
                # 创建队列动画
                queue_animation = salabim.AnimateQueue(
                    queue=queue,
                    x=int(position["x"] + 20),
                    y=int(position["y"] - 20),
                    direction='s',
                    reverse=True,
                    title=""
                )
                self.queue_animations[window_name] = queue_animation
                
                # 创建队列信息文本
                info_text = salabim.AnimateText(
                    text=lambda w=resource, n=window_name, q=queue: (
                        f"{n}\n"
                        f"Queue: {len(q)}\n"
                        f"Serving: {w.claimed_quantity()}\n"
                        f"Capacity: {w.capacity()}"
                    ),
                    textcolor="black",
                    fontsize=12,
                    x=position["x"] - 10,
                    y=position["y"] + 100,
                )
                self.queue_info_texts[window_name] = info_text


class Student(salabim.Component):
    """
    学生组件，模拟单个学生在食堂的行为。

    学生进入系统后，会根据预设的概率选择一个窗口类型，然后排队等待服务，
    服务结束后离开系统。
    """
    
    LENGTH: Final[int] = 20  
    HEIGHT: Final[int] = 15
    Y_OFFSET: Final[int] = 20

    def __init__(self, *args, windows: Dict[str, salabim.Resource], 
                 queues: Dict[str, salabim.Queue],
                 window_configs: List[Dict[str, Any]], 
                 num_before_queues: Dict[str, int],
                 total_num: List[int],
                 config: SimulationConfig, **kwargs) -> None:
        
        """
        初始化学生对象。

        Args:
            windows (Dict[str, salabim.Resource]): 一个包含所有窗口资源的字典。
            queues (Dict[str, salabim.Queue]): 一个包含所有排队队列的字典。
            window_configs (List[Dict[str, Any]]): 窗口的配置列表。
            config (SimulationConfig): 模拟配置对象。
        """
        super().__init__(*args, **kwargs)
        self.windows: Dict[str, salabim.Resource] = windows
        self.window_queues: Dict[str, salabim.Queue] = queues
        self.window_configs: List[Dict[str, Any]] = window_configs
        self.num_before_queues: Dict[str, int] = num_before_queues
        self.total_num: List[int] = total_num
        self.config: SimulationConfig = config

    def animation_objects(self, id: Any, screen_coordinates: bool = True) -> salabim.Tuple:
        """
        定义学生的动画对象。
        
        Args:
            id: 动画对象ID
            screen_coordinates: 是否使用屏幕坐标
            
        Returns:
            Tuple: 动画对象元组
        """
        # 创建学生矩形
        an = salabim.AnimateRectangle(
            spec=(0, 0, self.LENGTH, self.HEIGHT), 
            fillcolor="yellow"
        )
        return 0, self.Y_OFFSET, an
        

    def process(self) -> None:
        """
        定义学生在食堂中的行为过程。
        """
        # 1. 根据概率分布选择一个窗口
        window_names: List[str] = [wc['name'] for wc in self.window_configs]
        probabilities: List[float] = [wc['probability'] for wc in self.window_configs]
        chosen_window_name: str = np.random.choice(window_names, p=probabilities)

        chosen_window_resource: salabim.Resource = self.windows[chosen_window_name]
        chosen_queue: salabim.Queue = self.window_queues[chosen_window_name]
        service_time: float = next(
            wc['service_time'] for wc in self.window_configs
            if wc['name'] == chosen_window_name
        )

        num_windows: int = sum([x["num_windows"] for x in self.window_configs])

        if self.total_num[0] >= self.config.queue_capacity * len(self.window_configs):
            # 如果总人数超过队列容量，直接离开
            print(f"学生 {self.name} 发现食堂已满，离开食堂。")
            return

        while (len(chosen_queue) + self.num_before_queues[chosen_window_name] >= self.config.queue_capacity):
            # 如果队列已满，直接离开
            # print(f"学生 {self.name} 发现 {chosen_window_name} 队列已满，离开食堂。")
            # return
            chosen_window_name: str = np.random.choice(window_names, p=probabilities)
            chosen_window_resource: salabim.Resource = self.windows[chosen_window_name]
            chosen_queue: salabim.Queue = self.window_queues[chosen_window_name]
            service_time: float = next(
                wc['service_time'] for wc in self.window_configs
                if wc['name'] == chosen_window_name
            )

        # # 2. 计算目标队列位置
        window_position = self.config.window_positions[chosen_window_name]
        queue_bottom_x = window_position["x"] + 20
        queue_bottom_y = window_position["y"] - self.config.queue_capacity * self.Y_OFFSET - 40


        self.total_num[0] += 1
        self.num_before_queues[chosen_window_name] += 1
        now = self.env.now()
        an = salabim.AnimateRectangle(
            x = lambda t: salabim.interpolate(t, now, now + self.config.entrance_to_queue_time, self.config.entrance_position["x"], queue_bottom_x), 
            y = lambda t: salabim.interpolate(t, now, now + self.config.entrance_to_queue_time, self.config.entrance_position["y"], queue_bottom_y),
            spec=(0, 0, self.LENGTH, self.HEIGHT),
            fillcolor="blue",
            layer=-1,
        )
        # # 等待移动完成
        self.hold(self.config.entrance_to_queue_time)
        an.remove()

        now = self.env.now()

        an = salabim.AnimateRectangle(
            x = lambda q, t: salabim.interpolate(t, now, now + self.config.queue_to_tail_time, queue_bottom_x, queue_bottom_x), 
            y = lambda q, t: salabim.interpolate(t, now, now + self.config.queue_to_tail_time, queue_bottom_y, window_position["y"] - len(q) * self.Y_OFFSET - 20),
            spec=(0, 0, self.LENGTH, self.HEIGHT),
            fillcolor="red",
            layer=-1,
            arg=chosen_queue,
        )

        self.hold(self.config.queue_to_tail_time)  # 等待到达队列尾部
        an.remove()
        self.num_before_queues[chosen_window_name] -= 1


        # 4. 进入排队队列
        self.enter(chosen_queue)

        # 5. 排队等待服务
        self.request(chosen_window_resource)

        # 6. 离开排队队列
        self.leave(chosen_queue)
        self.total_num[0] -= 1

        # 7. 接受服务
        self.hold(service_time)

        # 8. 释放资源
        self.release(chosen_window_resource)


class StudentGenerator(salabim.Component):
    """
    学生生成器，用于在模拟过程中持续创建学生实例。
    """
    
    def __init__(self, *args, windows: Dict[str, salabim.Resource], 
                 queues: Dict[str, salabim.Queue],
                 window_configs: List[Dict[str, Any]], 
                total_num: List[int],
                 num_before_queues: Dict[str, int],
                 config: SimulationConfig, **kwargs) -> None:
        """
        初始化学生生成器。

        Args:
            windows (Dict[str, salabim.Resource]): 一个包含所有窗口资源的字典。
            queues (Dict[str, salabim.Queue]): 一个包含所有排队队列的字典。
            window_configs (List[Dict[str, Any]]): 窗口的配置列表。
            config (SimulationConfig): 模拟配置对象。
        """
        super().__init__(*args, **kwargs)
        self.windows: Dict[str, salabim.Resource] = windows
        self.window_queues: Dict[str, salabim.Queue] = queues
        self.window_configs: List[Dict[str, Any]] = window_configs
        self.total_num: List[int] = total_num
        self.num_before_queues: Dict[str, int] = num_before_queues
        self.config: SimulationConfig = config

    def process(self):
        """
        定义生成学生的行为过程。
        """
        while True:
            # 按照指数分布的时间间隔生成一个学生
            if self.env.now() >= self.config.simulation_duration - self.config.generator_stop_time:
                print("生成器已停止。")
                return

            self.hold(salabim.Exponential(self.config.inter_arrival_time).sample())
            Student(
                env=self.env,
                windows=self.windows,
                queues=self.window_queues,
                total_num=self.total_num,
                window_configs=self.window_configs,
                num_before_queues=self.num_before_queues,
                config=self.config
            )


class CanteenSimulation:
    """
    食堂模拟主类。

    该类负责根据给定的配置初始化并运行整个模拟过程，
    并在模拟结束后收集和报告关键性能指标（如平均等待时间）。
    """
    def __init__(self, config: Optional[SimulationConfig] = None) -> None:
        """
        初始化一个食堂模拟实例。

        Args:
            config (SimulationConfig, optional): 模拟配置对象。如果为None，使用默认配置。
        """
        self.config: SimulationConfig = config or SimulationConfig()
        self._validate_config(self.config.windows_setup)
        self.env: salabim.Environment = salabim.Environment(time_unit="seconds")
        
        # 设置动画环境
        if self.config.animation_enabled:
            self.env.animation_parameters(
                animate=True,
                speed=self.config.animation_speed,
                width=self.config.animation_width,
                height=self.config.animation_height,
                title="Dining Hall Queue Simulation",
                background_color="lightgray",
                x0=0,
                y0=0,
                x1=self.config.animation_width,
            )
            self.animation_manager = AnimationManager(self.config)
            self.animation_manager.create_static_elements()
        
        self.windows: Dict[str, salabim.Resource] = self._create_resources()
        self.queues: Dict[str, salabim.Queue] = self._create_queues()
        self.num_before_queues: Dict[str, int] = {x: 0 for x in self.queues.keys()}
        self.total_num: List[int] = [0]
        
        # 创建队列动画
        if self.config.animation_enabled:
            self.animation_manager.create_queue_animations(self.windows, self.queues)
        
        self._start_student_generator()

    def _create_queues(self) -> Dict[str, salabim.Queue]:
        """
        根据配置创建队列。
        
        Returns:
            Dict[str, salabim.Queue]: 队列字典
        """
        queues = {}
        for window_conf in self.config.windows_setup:
            name = window_conf['name']
            queues[name] = salabim.Queue(name=f"{name}_queue", env=self.env, capacity=self.config.queue_capacity)
        return queues

    def _start_student_generator(self) -> None:
        """启动学生生成器。"""
        StudentGenerator(
            env=self.env,
            windows=self.windows,
            queues=self.queues,
            window_configs=self.config.windows_setup,
            total_num=self.total_num,
            num_before_queues=self.num_before_queues,
            config=self.config
        )

    @staticmethod
    def _validate_config(config: List[Dict[str, Any]]) -> None:
        """
        验证配置的有效性。
        
        Args:
            config (List[Dict[str, Any]]): 窗口配置列表
            
        Raises:
            ValueError: 当配置无效时抛出异常
        """
        if not config:
            raise ValueError("窗口配置不能为空")
            
        total_prob = sum(c.get('probability', 0) for c in config)
        if not np.isclose(total_prob, 1.0):
            raise ValueError(f"所有窗口的概率之和必须为1，当前为: {total_prob}")
            
        for window_conf in config:
            required_keys = ['name', 'service_time', 'probability', 'num_windows']
            for key in required_keys:
                if key not in window_conf:
                    raise ValueError(f"窗口配置缺少必需的键: {key}")
                    
            if window_conf['num_windows'] <= 0:
                raise ValueError(f"窗口数量必须大于0: {window_conf['name']}")
                
            if window_conf['service_time'] <= 0:
                raise ValueError(f"服务时间必须大于0: {window_conf['name']}")
                
            if window_conf['probability'] < 0:
                raise ValueError(f"概率必须非负: {window_conf['name']}")

    def _create_resources(self) -> Dict[str, salabim.Resource]:
        """
        根据配置创建 salabim 资源（即服务窗口）。
        
        Returns:
            Dict[str, salabim.Resource]: 窗口资源字典
        """
        resources = {}
        for window_conf in self.config.windows_setup:
            name = window_conf['name']
            capacity = window_conf['num_windows']
            resources[name] = salabim.Resource(
                name=name, 
                capacity=capacity, 
                env=self.env
            )
        return resources

    def run(self, duration: Optional[int] = None) -> Dict[str, Any]:
        """
        运行模拟并返回结果。

        Args:
            duration (int, optional): 模拟运行的总时长（分钟）。如果为None，使用配置中的默认值。

        Returns:
            Dict[str, Any]: 包含各窗口及总体统计信息的字典
        """
        if duration is None:
            duration = self.config.simulation_duration
            
        print(f"开始模拟，时长: {duration}sec")
        
        if self.config.record:
            with self.env.video("video.mp4"):
                self.env.run(till=duration)
        else:
            self.env.run(till=duration)
        return self._collect_results()

    def _collect_results(self) -> Dict[str, Any]:
        """
        从资源中收集统计数据。
        
        Returns:
            Dict[str, Any]: 统计结果字典
        """
        results: Dict[str, Any] = {"window_stats": {}}
        total_customers = 0
        total_waiting_time = 0.0

        for name, resource in self.windows.items():
            # 获取资源的基本统计信息
            capacity = resource.capacity()
            queue_length = len(resource.requesters())
            claimers_count = len(resource.claimers())
            
            # 计算等待时间统计
            waiting_time_mean = resource.requesters().length_of_stay.mean()
            waiting_time = waiting_time_mean if waiting_time_mean and not np.isnan(waiting_time_mean) else 0.0
            
            results["window_stats"][name] = {
                "capacity": capacity,
                "current_queue_length": queue_length,
                "currently_serving": claimers_count,
                "utilization": claimers_count / capacity if capacity > 0 else 0,
                "average_waiting_time": waiting_time
            }
            
            total_customers += queue_length + claimers_count
            total_waiting_time += waiting_time * (queue_length + claimers_count)
        
        # 计算总体信息
        results["total_people_in_system"] = total_customers
        results["overall_average_waiting_time"] = (
            total_waiting_time / total_customers if total_customers > 0 else 0
        )

        return results

def print_results(results: Dict[str, Any], config: List[Dict[str, Any]]) -> None:
    """
    格式化并打印模拟结果。

    Args:
        results (Dict[str, Any]): `CanteenSimulation.run()` 返回的结果字典。
        config (List[Dict[str, Any]]): 用于本次模拟的窗口配置。
    """
    print("-" * 60)
    print("模拟配置:")
    for window_conf in config:
        print(f"  - 窗口: {window_conf['name']}, "
              f"数量: {window_conf['num_windows']}, "
              f"服务时间: {window_conf['service_time']}sec, "
              f"选择概率: {window_conf['probability']:.1%}")
    print("-" * 60)
    print("模拟结果:")
    for name, stats in results["window_stats"].items():
        print(f"  - {name}:")
        print(f"    - 窗口容量: {stats['capacity']} 个")
        print(f"    - 当前队列长度: {stats['current_queue_length']} 人")
        print(f"    - 当前服务人数: {stats['currently_serving']} 人")
        print(f"    - 利用率: {stats['utilization']:.2%}")
        if 'average_waiting_time' in stats and not np.isnan(stats['average_waiting_time']):
            print(f"    - 平均等待时间: {stats['average_waiting_time']:.2f} sec")

    print("-" * 60)
    print(f"系统内总人数: {results['total_people_in_system']} 人")
    if 'overall_average_waiting_time' in results and not np.isnan(results['overall_average_waiting_time']):
        print(f"总体平均等待时间: {results['overall_average_waiting_time']:.2f} sec")
    print("=" * 60 + "\n")


def main() -> None:
    """
    主函数，运行默认配置的模拟。
    """
    print(">>> 食堂排队模拟系统 <<<")
    print("--- 使用默认配置运行 ---")
    
    sim = CanteenSimulation()
    results = sim.run()
    print_results(results, sim.config.windows_setup)


if __name__ == '__main__':
    main()