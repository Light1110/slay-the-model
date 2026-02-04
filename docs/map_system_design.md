# MapManager 系统设计文档

## 概述

MapManager 系统实现了类似 Slay the Spire 的地图生成和导航功能。系统基于参考资料的设计规则，实现了完整的地图生成算法。

## 核心组件

### 1. RoomType 枚举 (`utils/types.py`)

定义了7种房间类型：
- `MONSTER`: 普通战斗 (53%)
- `ELITE`: 精英战斗 (8%)
- `REST`: 休息站点 (12%)
- `MERCHANT`: 商店 (5%)
- `UNKNOWN`: 未知房间 (22%)
- `TREASURE`: 宝箱 (固定楼层)
- `BOSS`: Boss战 (固定楼层)

### 2. MapNode 类 (`map/map_node.py`)

表示地图上的单个节点（房间位置）。

**属性：**
- `floor`: 层数 (0-16)
- `position`: 在该层的位置索引 (0-5)
- `room_type`: 房间类型 (RoomType枚举)
- `connections_up`: 向上连接的节点position列表
- `visited`: 是否已访问

**方法：**
- `add_connection_up(position)`: 添加向上连接

**注意**：玩家只能向上移动，因此不需要向下连接。

### 3. MapData 类 (`map/map_data.py`)

包含单个Act的所有地图数据和导航状态。

**属性：**
- `act_id`: Act编号
- `nodes`: 二维数组 [floor][position] 的所有节点
- `current_floor`: 当前层数
- `current_position`: 当前位置

**方法：**
- `add_floor(nodes)`: 添加一层到地图
- `get_node(floor, position)`: 获取指定位置的节点
- `get_floor(floor)`: 获取指定层的所有节点
- `get_current_node()`: 获取当前节点
- `set_current_position(floor, position)`: 设置当前位置
- `is_complete`: 检查是否到达Boss层

### 4. MapManager 类 (`map/map_manager.py`)

管理地图生成和导航的核心类。

**核心功能：**

#### 地图生成规则
1. **楼层结构**：每个Act有17层 (0-16)
   - 第0层：3个节点（玩家可从任意位置开始）
   - 第8层：宝箱层
   - 第14层：休息层
   - 第15层：Boss层（1个节点）
   - 第16层：Boss宝箱（不可见，0个节点）
   - 其他层：2-5个节点（随机）

2. **固定楼层规则**：
   - Floor 0: 全部MONSTER (简单池)
   - Floor 8: 全部TREASURE
   - Floor 14: 全部REST
   - Floor 15: BOSS

3. **随机楼层**：根据概率权重分配房间类型
   - MONSTER: 53%
   - ELITE: 8%
   - REST: 12%
   - MERCHANT: 5%
   - UNKNOWN: 22%

4. **连接规则**：
   - 每个节点有1-3条向上连接
   - 玩家只能向上移动，不需要向下连接
   - 第0层无向下连接
   - 第15层无向上连接

5. **未知房间机制**：
   - 进入UNKNOWN房间时才决定实际类型
   - 实现"厄运保护"：未出现的类型概率增加
   - 可能类型：MONSTER, MERCHANT, TREASURE, EVENT

**方法：**
- `generate_map()`: 生成完整地图
- `get_available_moves()`: 获取当前可移动的节点列表
- `move_to_node(floor, position)`: 移动到指定节点并创建房间实例
- `_create_room_instance(room_type)`: 根据房间类型创建Room实例

## 连接线防交叉算法

地图生成实现了防交叉连接算法，确保视觉上连接线不会交叉：

### 算法原理

1. **从左到右处理**：按从左到右的顺序处理每层的节点
2. **维护位置限制**：使用`min_allowed_position`跟踪当前节点可连接的最小位置
3. **避免重复连接**：使用`used_positions`集合防止多个节点连接到同一目标位置
4. **限制下一节点**：当前节点连接到位置i后，下一个节点只能连接到位置>i的节点
5. **移除保证阶段**：删除了"确保向下连接"阶段，避免破坏已建立的防交叉约束

### 防交叉规则

- 如果节点A（位置i）连接到位置j
- 那么所有在A右侧的节点（位置>i）只能连接到位置>j的节点
- 这确保了连接线不会交叉

### 实现代码

```python
# Track used positions to prevent multiple connections to same node
used_positions = set()

# Track the minimum position that can be connected to prevent line crossing
min_allowed_position = 0

# Process nodes from left to right
for current_node in current_floor_nodes:
    # Calculate available positions (from min_allowed to end, excluding used)
    available_positions = [
        pos for pos in range(min_allowed_position, len(next_floor_nodes))
        if pos not in used_positions
    ]
    
    if not available_positions:
        break
    
    # Determine number of connections (1-3, but limited by available positions)
    max_connections = min(3, len(available_positions))
    num_connections = self.rng.randint(1, max_connections)
    
    # Randomly select nodes to connect to from available range
    connected_positions = self.rng.sample(available_positions, num_connections)
    
    for pos in connected_positions:
        current_node.add_connection_up(pos)
        used_positions.add(pos)
    
    # Update min_allowed_position to prevent line crossing
    # Next node (to the right) can only connect to positions > max connected position
    if connected_positions:
        min_allowed_position = max(connected_positions) + 1
```

### 测试验证

通过`tests/test_no_crossing.py`验证：
- 测试单个地图的详细连接
- 验证50个随机地图
- 所有测试通过，无交叉连接

运行测试：
```bash
python tests/test_no_crossing.py
```

## GameState 集成

### 新增属性
```python
self.map_manager = None  # MapManager实例
self.map_data = None      # MapData实例
```

### 新增方法
```python
def initialize_map():
    """初始化地图系统并生成第一个Act。"""
    from map import MapManager
    
    self.map_manager = MapManager(self.config.seed, act_id=1)
    self.map_data = self.map_manager.generate_map()
    
    # 设置游戏阶段为map
    self.game_phase = "map"
```

## 使用示例

### 初始化地图
```python
from engine.game_state import game_state

# 初始化地图
game_state.initialize_map()

# 获取可用移动
available_moves = game_state.map_manager.get_available_moves()

# 移动到指定节点
if available_moves:
    target = available_moves[0]
    room = game_state.map_manager.move_to_node(
        target.floor, 
        target.position
    )
    # 进入房间
    room.enter_room()
```

### 手动创建地图（用于测试）
```python
from map import MapNode, MapData
from utils.types import RoomType

map_data = MapData(act_id=1)

# 添加第0层
floor_0 = [
    MapNode(0, 0, RoomType.MONSTER, connections_up=[0, 1]),
    MapNode(0, 1, RoomType.MONSTER, connections_up=[1]),
]
map_data.add_floor(floor_0)
```

## 测试

已创建测试脚本验证系统功能：

### `tests/test_map_core.py`
测试核心功能（无Room依赖）：
- RoomType枚举定义
- 手动地图创建
- 节点导航

运行测试：
```bash
python tests/test_map_core.py
```

### `tests/test_no_crossing.py`
测试防交叉连接算法：
- 单个地图详细连接检查
- 50个随机地图批量验证

运行测试：
```bash
python tests/test_no_crossing.py
```

## 待完成功能

### 1. 房间内容生成
MapManager的`_create_room_instance`方法中标记了TODO：
- 从game_state获取怪物遭遇
- 从game_state获取精英遭遇
- 从game_state获取Boss遭遇
- 实现REST、MERCHANT、TREASURE房间类型

### 2. 多层Act支持
当前架构支持多层Act，但默认只生成1个Act。扩展时：
- 调用`generate_map(act_id=2)`生成第2个Act
- 实现Act切换逻辑
- 处理特殊Act（如Act 4的特殊规则）

### 3. Ascension等级影响
根据参考资料，Ascension等级会影响：
- Ascension 1+: 精英概率增加约60%
- Ascension 3, 8, 18: 精英变得更强大

需要在MapManager中添加：
```python
def __init__(self, seed: int, act_id: int = 1, ascension: int = 0):
    if ascension >= 1:
        self.ROOM_TYPE_WEIGHTS[RoomType.ELITE] = 13  # 8 * 1.6 ≈ 13
```

### 4. 地图种子系统
已实现基础种子支持：
- 使用`random.Random(seed)`确保可重现
- 相同种子产生相同地图布局

### 5. 未知房间EVENT类型
当前`_resolve_unknown_type`中包含`RoomType.EVENT`，但未在`_create_room_instance`中处理。需要：
- 实现EventRoom类
- 在`_create_room_instance`中添加EVENT分支
- 根据game_state选择具体事件

## 设计优势

1. **关注点分离**: 地图只负责结构和类型，房间内容由game_state决定
2. **类型安全**: 使用枚举确保房间类型一致性
3. **可扩展性**: 架构支持多层Act、新房间类型
4. **可测试性**: 核心功能不依赖Room系统，易于单元测试
5. **确定性**: 种子系统确保相同布局可重现
6. **防交叉保证**: 算法确保连接线视觉上不交叉，符合Slay the Spire风格

## 参考资料

- Map Locations: https://slaythespire.wiki.gg/wiki/Map_Locations
- Map Generation: https://slaythespire.wiki.gg/wiki/Map_Generation

## 注意事项

1. **循环导入**: MapManager使用延迟导入（`_create_room_instance`内导入）避免与Room模块的循环依赖
2. **Python版本兼容性**: 使用`TYPE_CHECKING`进行类型注解，避免Python <3.10的类型语法问题
3. **终端编码**: 测试脚本使用ASCII字符避免Windows终端Unicode编码问题