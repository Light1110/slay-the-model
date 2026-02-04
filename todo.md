# todo

## 2.4 架构逻辑要大改。

game_flow的总循环逻辑，由迭代各个action，改为迭代room.
伪代码：

```text
while curRoom.floor < maxFloor:
    curRoom = map_select()
    curRoom.init()
    res = curRoom.enter()
    if res == "DEATH" or "WIN":
        break
    curRoom.leave()
```

action_queue仍然是必要的，但是应该在room内部进行构建。比如在ShopRoom中：

```text
def enter_room(self, ...):
    ...
    while not self.should_leave:
        # build SelectAction
        action_queue.add_action(select_action)
        action_queue.execute_all()

def LeaveRoomAction(Action):
    ...
    def leave(self, ...):
        game_state.current_room.should_leave = True
        # 其它Action还会指定不同的字段
        # 比如战斗回合结束，就应该是 xxx.player_trun_end = True
```

此外，Event的定义也完全变化了。或许不再需要EventStage。
现在Event本身，只代表 Unknown Room 中可能触发的，随机事件，有很多不同的可能。有些EventRoom也会带来奖励，有的会带来战斗。
由于Combat并不只会被CombatRoom触发，还可能被Event触发，所以主逻辑应该写在单独的Combat类里面。CombatRoom只负责管理Combat的创建和执行。
NeoEvent的逻辑，完全可以写在NeoRoom里面。
UnknownRoom如果随机到其它Room类型，比如CombatRoom/RestRoom/ShopRoom，直接替换当前的currRoom即可；如果是Event的话，则执行相关的Event。

架构和接口实现上，应当参考目前的风格，保证能够复用，不要有太短的工具函数

拟定一份详细的更改说明，要求精细到类的接口和字段

## 2.4 各个room功能检查

## 2.7-2.8 最复杂的是战斗类

## 2.6 基类：enemy

## 2.x 是否支持多选?
