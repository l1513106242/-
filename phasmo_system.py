#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
恐鬼症 综合查询系统 - 完整内置数据版（滚动地图预览 + 缩放）
支持外部 data 文件夹覆盖，图片显示原始尺寸，可滚动和缩放。
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
import sys
import base64
from io import BytesIO

# 尝试导入 PIL 以支持更多图片格式和缩放
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ======================== 路径处理 ========================
def get_resource_dir():
    """获取资源目录（优先外部 data 文件夹，否则内部打包 data）"""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    external_dir = os.path.join(exe_dir, "data")
    if os.path.exists(external_dir):
        return external_dir
    if getattr(sys, 'frozen', False):
        internal_dir = os.path.join(sys._MEIPASS, "data")
        if os.path.exists(internal_dir):
            return internal_dir
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

DATA_DIR = get_resource_dir()

# ======================== 内置默认数据 ========================

# ---- 鬼魂名称列表（29只）----
GHOST_NAMES = [
    "阿斯旺", "女妖", "达彦", "恶魔", "雾影", "加鲁", "御灵", "寒魔", "巨灵", "盲灵",
    "梦魇", "魔洛伊", "鬼婴", "幻妖", "奥班博", "赤鬼", "怨灵", "幻影", "骚灵",
    "雷魂", "亡魂", "暗影", "魂魄", "刹耶", "拟魂", "孪魂", "魅影", "幽灵", "妖怪"
]

# ---- 鬼魂数据 ----
DEFAULT_GHOSTS = {
    "魂魄": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "EMF 通灵盒 笔迹",
        "hunt_threshold": "50%",
        "ability": "能力：①会模仿其他鬼的互动、溜达、低语、脚步、灵异事件、技能(其实并不是真的会，通俗讲学的不完全)(比如猎杀时模仿孪快的脚步，或者模仿双动门，但门和音效的配合并不是标准的双动门)。②点燃圣木后魂魄180s内不可猎杀。\n常用判断方法：①点燃圣木后3分钟不会猎杀。②点燃圣木2分半(160s左右)在鬼附近续一根圣木，观察是否在90s以内猎杀。"
    },
    "魅影": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "EMF 通灵盒 点阵",
        "hunt_threshold": "50%",
        "ability": "能力：①传送到某一玩家处，进行互动或直接猎杀(会留下EMF2级或5级)，传送后走回鬼房，期间可互动。②魅影不会踩盐。三级盐对魅影无效。\n常用判断方法：①自己的位置出现凭空的EMF2级或5级。②鬼魂经过了盐却没有踩盐。"
    },
    "幻影": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "通灵盒 紫外线 点阵",
        "hunt_threshold": "50%",
        "ability": "能力：①幻影会在一名玩家死亡或离开时，选择一名玩家并前往他的位置(物理方式走过去)，并在终点留下EMF2级(不频繁)。②幻影现身或猎杀时，注视其模型每秒扣0.5%理智。③幻影的鬼照(包括鬼魂事件，点阵，猎杀等)通常是清晰照片无鬼(鬼魂事件结束时拍摄也会清晰无鬼)，且现身时拍鬼照使鬼消失，但是仍有音效。④幻影猎杀时闪烁更偏向于全程隐身。\n常用判断方法：①清晰无鬼鬼照。②猎杀时倾向于隐身。"
    },
    "骚灵": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "通灵盒 紫外线 笔迹",
        "hunt_threshold": "50%",
        "ability": "能力：①俗称炸堆，骚灵会一瞬间互动一个位置的多个互动道具。如果没有互动道具，则出现凭空EMF2级。每个被投掷物品(EMF3级)扣除周围玩家2%理智。(若鬼房内没有可投掷物品则骚灵会偏向于更换鬼房)。②骚灵扔东西会比其他鬼更频繁更远。(骚灵猎杀时扔物品的判定为100%(不是50%)，且骚灵互动物品投掷距离为3-6m，普通鬼为1-3m)。\n常用判断方法：①猎杀时扔东西远且特别频繁。②目击或推断或听到发生了炸堆。"
    },
    "女妖": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "紫外线 灵球 点阵",
        "hunt_threshold": "50%",
        "ability": "能力：①非猎杀时，女妖有66.7%的概率跟随目标，需在同一楼层(灯塔/地下室/阁楼发动技能不需要在同层)。②大锅33.3%概率收听到女妖独特尖叫。③女妖在开局会锁定一名玩家(在屋内会跟随且只会杀这个人，在屋外正常猎杀)，猎杀阈值只与被锁定者有关，死亡和复活会改变女妖顺序，猎杀时被锁定者死亡，立刻更换下一个被锁定者。④女妖现身唱歌且对象是锁定者且锁定者撞掉，则此次现身消耗15%理智，而不是10%。\n常用判断方法：①跟随某人②猎杀锁定某人③大锅尖叫。"
    },
    "巨灵": {
        "speed": "常速1.7 → 视野加速2.8，3m外看到玩家2.5",
        "evidence": "EMF 紫外线 刺骨",
        "hunt_threshold": "50%",
        "ability": "能力：①电闸开启时且附近有玩家，巨灵可以扣除房间内或自身周围3m玩家25%理智，电闸会EMF2级或5级。(对象为第一个进入大厅的玩家)。②巨灵永不关闸，但可以开灯造成跳闸。③猎杀时，巨灵在3m外会以2.5m/s的速度冲向玩家，3m内恢复正常，再次超越3m速度会被强制拉低到2.5m/s。④在电闸关闭时，巨灵为常速无特征鬼。\n常用判断方法：①利用巨灵冲刺的特点卡好距离。②在电闸上放EMF，触发EMF而不关闸。"
    },
    "梦魇": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "通灵盒 灵球 笔迹",
        "hunt_threshold": "60%(黑)/40%(亮)",
        "ability": "能力：①梦魇附近4m有灯打开时，12.5%概率秒关灯(不排除自然秒关灯，现身也会关灯)(该能力每个玩家每个开关有10s冷却，冷却时间仅在关灯后重置，关灯10s内开灯会中断冷却)，电闸损坏/爆灯/鬼魂事件时仍可使用。②鬼房开灯时，梦魇可能在附近游荡，寻找黑暗房间作为新的鬼房。抵达一个房间75%概率爆灯，且概率变更为鬼房。③梦魇不会主动开灯(电视，电脑可以打开)。注：开灯时的40%理智判定为灯的开关处于打开状态，与电闸/爆灯无关。\n常用判断方法：①秒关灯(关灯后10s再开灯)(任何鬼都可能秒关灯)。②开启鬼房灯光，观察是否有前往黑暗处的倾向或行为。"
    },
    "亡魂": {
        "speed": "未感知玩家1.0 → 感知玩家3.0",
        "evidence": "灵球 笔迹 刺骨",
        "hunt_threshold": "50%",
        "ability": "能力：①亡魂可以开局互动一下后立刻游荡，高难度可能开局更换鬼房(一般动门)。②猎杀时无玩家视野速度慢，有玩家视野后速度瞬间拉满(视野包括看到玩家或感知到使用电器的玩家)。中途丢失视野(如点圣木)会使亡魂在到达最后感知位置时，以每秒减少0.75m/s的速度回到1m/s。\n常用判断方法：如上，在猎杀时观察速度判断。"
    },
    "暗影": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "EMF 笔迹 刺骨",
        "hunt_threshold": "35%",
        "ability": "能力：①鬼房有人时，暗影会逃到5m外的一个位置，长时间不会鬼房，且在躲避处互动。在躲避处被人找到时，扣除半径7.5m附近玩家至多10%理智，之后暗影会返回鬼房。②灵异事件发生可能性，团队理智每下降1%，提高2%。③多名玩家在附近时，一般不会猎杀，但可到没人的地方猎杀；有人在附近，一般不会互动。④召唤类诅咒道具召唤鬼时，66%概率以黑色透明灵体出现。\n常用判断方法：有人在附近时几乎不互动。"
    },
    "恶魔": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "紫外线 笔迹 刺骨",
        "hunt_threshold": "70%",
        "ability": "能力：①恶魔可以发动无视理智的猎杀(不代表一定早猎)。②十字架对恶魔阻挡范围为150%，点燃圣木后恶魔60s后即可猎杀。恶魔的猎杀间隔为20s。③恶魔的对视很可能来自一次漫游，而不是女妖幻影那样的跟随，通常恶魔不会追出很远发动(类似短距离尾随)。\n常用判断方法：①点燃圣木后60-90s猎杀。②高理智猎杀，过早猎杀。"
    },
    "幽灵": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "灵球 刺骨 点阵",
        "hunt_threshold": "50%",
        "ability": "能力：①幽灵能立刻关闭一扇打开的门(帐篷门不会完全关闭，柜子和杂物间(Closet如R房主卧最里面)的门不会被幽灵技能影响)，并在此门产生两个EMF2级(连续两声动门声，双动门)，每次双动门会降低7.5m内玩家15%理智(所有鬼都可能实现\"双动门\"，幽灵更频繁)。②点燃圣木会被送回鬼房90s，无法离开鬼房，但可以靠灵异传送出来，或直接猎杀(不出门不一定是幽灵)。③非灵异下，只有幽灵会互动大门。\n常用判断方法：①发现双动门(非猎杀或鬼魂事件期间)。②点圣木传送回鬼房且90s不出鬼房。"
    },
    "赤鬼": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "EMF 刺骨 点阵",
        "hunt_threshold": "50%",
        "ability": "能力：①赤鬼发动灵异事件与玩家碰撞后，扣除玩家20%理智(其余为10%)。②赤鬼不会白雾哈气。③赤鬼猎杀时闪烁更偏向于全程显形。④赤鬼很活跃(前期并不活跃)。\n常用判断方法：①白雾哈气排除赤鬼。②猎杀时常显，与幻影相反。"
    },
    "妖怪": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "通灵盒 灵球 点阵",
        "hunt_threshold": "50%(常)/80%(吵)",
        "ability": "能力：①80%理智以下时，当玩家使用游戏内语音或者通灵盒时，妖怪会因为杂音，发动猎杀。②在妖怪附近使用语音聊天会增加他的活跃度。③猎杀时对电器类道具感知很低(2.5m)(包括八音盒)，视线不受影响。\n常用判断方法：在躲藏点附近(离鬼较远的地方)，在较极限距离吸引鬼，若鬼未被吸引或恰好经过附近(没感知玩家)，则为妖怪。"
    },
    "寒魔": {
        "speed": "2.7(<0);2.5(3);2.3(6);2.1(9);1.75(12);1.4(>15)",
        "evidence": "紫外线 灵球 刺骨",
        "hunt_threshold": "50%",
        "ability": "能力：①寒魔的移动速度和当前房间的温度有关，无视野加速。②寒魔猎杀时会降低周围温度(只有大十字架燃烧和篝火会影响周围温度从而影响寒魔，蜡烛打火机不影响)。③寒魔不会开闸，且2倍概率关闸。④电闸关闭时，寒魔在猎杀时头上会冒白气。\n常用判断方法：①观察速度变化。②关闸时猎杀时鬼魂头上有白气。\n注：多证据情况下不要忘记排除拟魂。"
    },
    "御灵": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "EMF 紫外线 点阵",
        "hunt_threshold": "50%",
        "ability": "能力：①御灵不会换鬼房(1%概率会且猴爪可以强制换鬼房)且很少游荡(游荡不会到很远，也不会很久)。②御灵的点阵要求所在房间内无人且只能通过摄像机才可以观察到。③当鬼房有人时，御灵会尝试更多的互动点阵以及物品。\n常用判断方法：基本不出鬼房或很少出鬼房或出鬼房但不远时间也不长。"
    },
    "鬼婴": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "EMF 紫外线 笔迹",
        "hunt_threshold": "50%",
        "ability": "能力：①鬼房内等待一名玩家，当该玩家进入鬼房后，鬼婴会离开鬼房，低语并且留下凭空EMF5/2级。若有人找到鬼婴，鬼婴会尝试去另外一个房间，否则返回鬼房。鬼房外的鬼婴，会选择一名玩家，留下凭空EMF5/2级，并试图跟随回到鬼房，若该玩家不进入鬼房，鬼婴会在鬼房外进行低语尖叫。②鬼婴脚步传播12m，干扰(10m)和脚步几乎同时出现。③收音器能较频繁收到鬼婴的声音(超自然声音)。\n常用判断方法：(同层)脚步声传播范围比正常鬼小。"
    },
    "怨灵": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "通灵盒 灵球 刺骨",
        "hunt_threshold": "60%",
        "ability": "能力：①怨灵在火焰周围(篝火，蜡烛，打火机)不能猎杀。火焰挡猎范围为4m(挡猎优先级高于十字架)，怨灵熄灭火焰范围为4m或更远(正常鬼2m)，火焰不可跨房间挡猎。②阴间每有一个人怨灵吹蜡烛概率加25%。③怨灵每熄灭三根蜡烛，可以无视理智猎杀(大概6s内)。该猎杀可被十字架和火焰阻挡。猎杀过程中被吹灭的火焰也计入计数器。\n常用判断方法：①规避蜡烛猎杀或猛猛吹蜡烛不猎杀。②三吹猎杀(圣木时间内无法猎杀)。\n注：①火焰挡猎4m，可能被2/3级十字架覆盖。②多证据情况下不要忘记排除拟魂。"
    },
    "孪魂": {
        "speed": "主1.53/副1.87 → 视野加速主2.52/副3.08",
        "evidence": "EMF 通灵盒 刺骨",
        "hunt_threshold": "50%",
        "ability": "能力：①主鬼进行互动后，副鬼会随即进行一次互动(有短暂延迟)。主鬼互动范围为半径 3m 的圆形范围，副鬼互动范围为鬼房中心半径 16m 的圆形范围。②证据等只会出现在主鬼房。③猎杀时判定主鬼在十字架范围内即可挡猎。④主副鬼同模型，速度不一，每次猎杀只会出现一个。\n常用判断方法：①几乎在一定距离上同时出现两个互动。②150速副鬼视野加速加满会有3s左右的脚步失真。主鬼比常速鬼慢10%，副鬼快10%。"
    },
    "雷魂": {
        "speed": "常速1.7 → 视野加速2.8(无电)；2.5(有电)",
        "evidence": "EMF 灵球 点阵",
        "hunt_threshold": "50%(无)/65%(有)",
        "ability": "能力：①雷魂附近6/8/10m(小/中/大图)内存在激活的电子设备，会提高猎杀阈值。②可进行远电子互动，但是远处没有脚步。③有人在鬼房时，雷魂会爆麦，声音传感器经常到100%。附近的电子设备经常过载或者失灵(声音传感器常70%↑)。④猎杀时干扰附近15m内的手持电子设备。附近6/8/10m范围内的电器，使雷魂猎杀时速度锁定2.5m/s(内置视野加速)，无电器常速无特征。\n常用判断方法：在激活的电器(仅包含玩家带入的电器)附近锁速，若无，为常速鬼。"
    },
    "幻妖": {
        "speed": "常速1.7 → 视野加速2.8",
        "evidence": "EMF 紫外线 灵球",
        "hunt_threshold": "50%",
        "ability": "能力：①幻妖留下的指纹16.7%概率多一指(6指-门、箱子、帐篷、电线杆，5指-键盘、监狱牢房门，2指-开关)。②幻妖每次本应留下紫外线的互动有25%概率不留下。③猎杀时6.6%概率变换模型，变后变回原模型(一次猎杀至少一次)，死亡玩家无法看到模型变换。④幻妖发动技能，使所有紫外线存续时间减少一半，可多次叠加，存续时间少于15s时，现有紫外线全部消失，后续一段时间互动不再产生指纹。\n常用判断方法：①时有紫外线证据时而没有。②出现多指紫外线证据。③猎杀时观察到改变模型。"
    },
    "拟魂": {
        "speed": "常速1.7 → 视野加速2.8/与拟鬼一致",
        "evidence": "通灵盒 指纹 刺骨",
        "hunt_threshold": "50%/与拟鬼一致",
        "ability": "能力：①拟魂每30-120s会切换一次模拟对象(0理智进门猎可能是拟魂本体)，猎杀时不会切换，且可连续为同一种鬼。②拟魂模拟的鬼，会模仿鬼魂特性(如6指)，猎杀阈值，但无法模拟没有的证据(如御灵的肉眼点阵)。拟魂一定有灵球(灵球算特性而非证据)，灵球会跟随拟魂，会出现鬼房无灵球的情况。\n常用判断方法：①表现特殊技能但所给证据无对应的鬼魂。②0证据发现灵球，或多发现一个证据。③多次猎杀表现不同的鬼魂特点。"
    },
    "魔洛伊": {
        "speed": "1.5-2.25 → 视野加速",
        "evidence": "通灵盒 笔迹 刺骨",
        "hunt_threshold": "50%",
        "ability": "能力：①玩家使用通灵盒被回应/使用大锅被回应，会被诅咒，使该玩家理智降低速度提高200%(无视光照环境)，离开房屋暂停，返回继续，吃理智药可以消除诅咒。②猎杀时圣木效果为150%(7.5s)③猎杀速度与团队平均理智有关。从50%理智开始，每减少1%理智，速度提升0.015m/s，35%理智近常速鬼。\n常用判断方法：①使用过锅/通灵盒且被回应的人掉理智比常人快。②猎杀时点燃圣木，效果时间为7.5s。③0%理智150鬼速视野加速加满有长时间脚步失真。④猎杀时吃理智药恢复理智会导致速度变慢。"
    },
    "雾影": {
        "speed": "3(>6m),1.6(2.5-6m),0.4(<2.5m)",
        "evidence": "通灵盒 笔迹 点阵",
        "hunt_threshold": "40%",
        "ability": "能力：①在雾影1m内使用通灵盒时，有33%概率会听到特殊音效(嘶吼声)。②雾影猎杀时，全图透视，并周期性判定直线距离最短玩家并前往该玩家位置，且起步速度很快。雾影手长，许多躲藏点，无敌点失效。③雾影猎杀时闪烁更偏向显形。\n常用判断方法：起步超级快，到人附近速度骤减。\n注：在雾影猎杀期间点燃圣木，雾影将保持点燃圣木时的速度(＞3m/s时为1.6m/s)。"
    },
    "刹耶": {
        "speed": "锁速2.75-0.125X(技能判定成功次数)",
        "evidence": "灵球 笔迹 点阵",
        "hunt_threshold": "75-6X",
        "ability": "能力：①衰老判断每1-2分钟判定一次，若判定周围有玩家，则衰老一次(判定成功)，若判定失败，则每30s判定一次，直到成功。互动频率为200-15X(X最大为10)。此衰老也可以通过通灵板问年龄发现改变。②开局刹耶从一个房间跑出来，跑到另外一个房间。通常移动10-15m，并且进行两次互动。\n常用判断方法：①互动频率，猎杀频率，猎杀时速度锁速且和游戏时间(年龄)相关。②通灵板发现年龄变大。"
    },
    "奥班博": {
        "speed": "攻1.96/静1.45 → 视野加速攻2.39静1.65",
        "evidence": "笔迹 点阵 紫外线",
        "hunt_threshold": "静15%/攻65%",
        "ability": "在出口门第一次打开后1分钟切换到另一个状态，之后每2分钟一次。状态切换可以在狩猎过程中发生。\n在平静状态下的狩猎理智阈值为10%，在攻击性状态下为65%。如果在攻击状态下开始狩猎，狩猎时间将缩短20%。 \n常用判断方法：①在冷静时，奥班博狩猎起步较慢"
    },
    "达彦": {
        "speed": "10米外1.7,动2.25/,静1.12",
        "evidence": "灵球 EMF 通灵盒",
        "hunt_threshold": "静45%走60%",
        "ability": "当玩家靠近时，理智阈值会降低到玩家静止时的45%，走路时则提高到60%。\n当玩家距离幽灵10米以内时，将以固定速度移动（如果玩家移动）速度为2.25米/秒;若玩家静止，则以固定速度1.12米/秒移动。如果10米内没有玩家，会遵循标准幽灵速度(1.7)，但有一个特殊情况：如果鬼与10米内的玩家有视线，连续视线带来的速度提升会在背景中增加，只有当它不再靠近任何玩家时才会生效.\n只能是女性鬼魂，并且会使用女性鬼魂模型。\n常用判断方法:①靠近玩家时鬼速变慢,玩家移动时鬼速变快②观看是否为男性模型"
    },
    "加鲁": {
        "speed": "正1.7 怒1.96 弱1.36 → 视加正常2.8怒3.23弱2.2",
        "evidence": "EMF 紫外线 通灵盒",
        "hunt_threshold": "正常50%,怒60%弱40%",
        "ability": "有三种可切换状态。默认情况下它以“正常”状态开始。如果踩盐、烧十字架或被香薰影响，如果处于“正常”状态，会切换为“狂怒”状态;如果处于“虚弱”状态，则切换为“正常”状态。一旦狩猎结束于狂暴状态，它会切换到“虚弱”状态。\n理智阈值正常下50%愤怒为60%弱化为40%     正常状态下十字架范围不变.愤怒下-2米.弱化下+1米    鬼魂速度正常状态下1.7m愤怒1.96m弱化1.36m  香的致盲效果正常状态下5秒愤怒4秒弱化6秒\n常用判断方法：:①加鲁在激怒状态下无法踩盐②三次猎杀鬼速不同"
    },
    "阿斯旺": {
        "speed": "1.53 → 视野加速2.52",
        "evidence": "点阵 刺骨 笔迹",
        "hunt_threshold": "50%",
        "ability": "基础速度为1.53米/秒。它的视线加速会以每秒0.0375倍基础速度的速度提升，而非0.025倍，这意味着它在17.33秒后达到最高速度，而大多数其他幽灵需要26秒。"
    },
    "盲灵": {
        "speed": "正常1.7 前往航点2.21",
        "evidence": "灵球 通灵盒 紫外线",
        "hunt_threshold": "正常50% / 冲刺70%",
        "ability": "在狩猎中，鬼没有视线，因此只能通过语音聊天和主动电子设备检测玩家。尽管没有视线，但它仍能通过碰撞杀死玩家。鬼的敏锐听觉能感知移动的玩家(见注1),所有这些情况都会设置“侦测航点”,鬼必须先到达航点，才能前往其他航点。此外，鬼每5-10秒验证并放置探测点（如有），并按以下顺序进行优先级排序：短跑→站立行走→蹲着行走→音色/电子音乐\n如果同时通过移动发现多名玩家，鬼会优先选择最近的航点。鬼速度默认固定为1.7米/秒，前往探测航点时速度固定为2.21米/秒。"
    }
}
# 补全缺失的鬼魂（确保所有名称都有数据）
for name in GHOST_NAMES:
    if name not in DEFAULT_GHOSTS:
        DEFAULT_GHOSTS[name] = {"speed": "", "evidence": "", "hunt_threshold": "", "ability": ""}

# ---- 装备数据 ----
DEFAULT_EQUIPMENT = {
    "★温度计": {
        "level1": "水银温度计，温度测速但慢，可以扔在地上等待。可在示数较高时带着找鬼房，示数降低可能鬼房。",
        "level2": "温度枪，右键打开，保持长摁右键5s后显示温度(一直摁一直显示温度)温度较精确。",
        "level3": "空气温度计，右键打开，保持长摁右键2.5s后显示温度(一直摁一直显示温度)温度更精确。",
        "note": "5-7℃以下会吐寒气，勿用口吐寒气判断刺骨。开闸后要等回温，等鬼降温鬼房。1℃以下为刺骨。"
    },
    "十字架": {
        "level1": "$等级1:木棍十字架，挡猎基础范围3m，只能挡猎一次。",
        "level2": "$等级2:铸铁十字架，挡猎基础范围4m，可以挡猎2次。",
        "level3": "$等级3:金银镶边十字架，挡猎基础范围5m，挡猎2次，完好十字架可消耗所有挡猎次数，阻挡一次诅咒猎杀。",
        "note": "摁G扔在地上或F放置或手持均有效(不要放在背包里)，对恶魔挡猎范围大50%。"
    },
    "理智药": {
        "level1": "$等级1:复古蛇油，需要20s慢慢恢复理智。",
        "level2": "$等级2:药，恢复理智需要10s。",
        "level3": "$等级3:针，恢复理智需要10s，立刻恢复满体力条且奔跑时不消耗体力10s。",
        "note": "拿起后右键使用后自动丢掉，不可再捡起来，回理智多少取决房间设定，可解除魔洛伊的诅咒。"
    },
    "点火器": {
        "level1": "$等级1:火柴，可以使用10次，每次使用可持续燃烧10s。",
        "level2": "$等级2:塑料打火机，可反复使用，但最多使用5分钟(累计计时)。",
        "level3": "等级3:高级打火机，光照更强，可重复使用，最多使用10分钟(累计计时)，可在雨天使用。",
        "note": "右键使用，打开时可使用F点燃蜡烛或篝火，若在手里，切换到蜡烛/圣木，可直接左键点火使用。"
    },
    "火光(蜡烛)": {
        "level1": "$等级1:蜡烛，光照范围2m，可持续燃烧5分钟，理智消耗减少为33%。烧没后不可再点燃。",
        "level2": "$等级2:烛台，光照范围2m，可持续燃烧10分钟，理智消耗减速为50%。烧没后不可再点燃。",
        "level3": "等级3:汽油灯笼，光照范围2m，不会熄灭，理智消耗减少为66%，雨天也可点亮。",
        "note": "作为光源，F可放置在地上。对怨灵可起到挡猎效果(优先级高于十字架)。附近理智降低速度减缓。"
    },
    "熏香(圣木)": {
        "level1": "$等级1:圣木，效果范围3m，致盲持续时间为5s。",
        "level2": "$等级2:一捆圣木，效果范围4m，燃烧持续时间6s，减速5s，猎杀时点燃可以减缓鬼的移动速度(扔到鬼脸上)。",
        "level3": "等级3:香炉，效果范围5m，燃烧时间7s，猎杀时点燃可以禁锢鬼魂5s。每个当局仅可用一次，但不是消耗品。",
        "note": "右键使用(携带点火器)，致盲鬼且自使用开始一段时间无法猎杀(常90，恶60，魂180s)。魔洛伊致盲时间为7.5s。"
    },
    "盐": {
        "level1": "$等级1:盐瓶，一瓶可使用两次，部署两个小盐堆。",
        "level2": "$等级2:木制容器(粉盐)，可以部署三个长条盐堆(长度和门的长度类似)。",
        "level3": "$等级3:黑盐，等同于等级2，鬼魂非猎杀时踩到盐会使其转身，猎杀时踩到盐会短暂减速。",
        "note": "F放置盐堆，鬼魂经过会踩盐(上一次盐效果结束)，指纹鬼有紫外线可见足迹。魅影不会踩盐。"
    },
    "声音传感器": {
        "level1": "等级1:麦克风，放置后传感器以自身为圆心，收集圆形区域内的声音显示在屏幕上。",
        "level2": "等级2:双麦克风，可以调整圆形范围的大小，可用于缩小找鬼房的范围(车上操作)。",
        "level3": "等级3:高级传感器，拿起右键选择模式(决定范围)，向前-扇形，向外-两个方向相反的小扇形，向内-球形。",
        "note": "可以F放置，放在地图各处，收集到动静会在车内右上角显示屏显示声音分贝。"
    },
    "★EMF": {
        "level1": "等级1:类电流表，范围小1.7m，不够精确，可以通过声音听出来级数(有点像盖格计数器)。",
        "level2": "等级2:K2电表，在1.7m范围的EMF点内移动时，2到5的值会依次亮起，并发出清晰可听见的声音。",
        "level3": "等级3:手机型，可一次跟踪至多三个EMF点，显示方向，距离，上方显示级值，同时有声音，范围3.5m。",
        "note": "右键可开启关闭，五个等级，常态为1级，互动(动门窗灯等)为2级(EMF鬼概率5级)，扔物品3级，现身/哈气4级。"
    },
    "★通灵盒": {
        "level1": "等级1:老式收音机，鬼魂识别范围3m，音质差，鬼魂回复速度慢。",
        "level2": "等级2:通灵盒，鬼魂识别范围4m，音质中，鬼魂回复速度适中。识别未回复×，有回复亮鬼魂标。",
        "level3": "等级3:高级通灵盒，鬼魂识别范围5m，音质高，鬼魂回复速度快。识别未回复下面红灯，回复闪灯。",
        "note": "右键可开启关闭，鬼附近使用可对话，需无光源有时还需要房间只有一个人。识别与恢复情况有亮灯显示。"
    },
    "★鬼魂笔记": {
        "level1": "等级1:小笔记本，笔记判定范围为3m，鬼魂互动率低。",
        "level2": "等级2:笔记本，笔记判定范围为4m，鬼魂互动率中。",
        "level3": "等级3:豪华笔记本，笔记判定范围为5m，鬼魂互动率高。",
        "note": "摁F放置在鬼房或鬼附近，鬼经过时会有概率写(笔记鬼)，同时算作互动。"
    },
    "★点阵投影仪": {
        "level1": "等级1:点阵手电筒，射程5m，光照强度低，手持也可F放置。(不好用且受限于自定义-禁用手电影响)",
        "level2": "等级2:圆形点阵投影仪，半径2.5m，亮度较亮，摁F可贴在物体上或放在地上。",
        "level3": "等级3:扫描型点阵投影仪，辐射范围7m，以一定速率扫描(类似灯塔)。摁F可贴在物体上或放在地上(可互动固定角度)。",
        "note": "点阵鬼经过且触发点阵时有点阵鬼影(肉眼可见)，算作鬼照，御灵点阵需鬼房无人且仅摄像机可见(肉眼不可见)。"
    },
    "★摄像机": {
        "level1": "等级1:老摄像机，画面小，画面质量低，电子干扰很明显，容易被鬼掀翻(互动)。",
        "level2": "等级2:普通摄像机，画面适中，画面质量适中，电子干扰明显，容易被鬼掀翻(互动)。",
        "level3": "等级3:高级摄像机，画面超级大，画质超级好，电子干扰轻微，容易被鬼掀翻(互动)。",
        "note": "拿在手上自动开启，右键切换夜视模式(可用于看路)，可F放置且调整方向，可以看灵球(灵球鬼)。长摁右键开启录制功能。"
    },
    "三脚架": {
        "level1": "等级1:无多余左右，会被鬼魂掀翻(互动)。被掀翻后需要重新摆放。",
        "level2": "等级2:相较于等级1，可以在车内电脑控制相机旋转(左右均可)，稳定性略微提高。",
        "level3": "等级3:相较于等级2，更不易被鬼魂掀翻。",
        "note": "用于放置摄像机，拿起摄像机对三脚架顶端F放置组合在一起，拿起后切换道具或G直接扔在地上。"
    },
    "照相机": {
        "level1": "等级1:拍立得，拍照冷却高，猎杀时拍照才算做吸引鬼魂(算电器)，平常拿在手上不算做电器。",
        "level2": "等级2:数码相机，拍照冷却适中，屏幕上显示画面。",
        "level3": "等级3:单反相机，拍照冷却低，有屏幕显示画面，不易受电子干扰。",
        "note": "右键拍照(拍照时最好靠近拍，一般盐等蹲着拍)，在结束时结算金钱。"
    },
    "手电筒": {
        "level1": "等级1:普通手电筒，光照角度小，亮度低。",
        "level2": "等级2:强光手电筒，光照角度和亮度都有提高。",
        "level3": "等级3:超级手电筒，光照角度和亮度再次提高。",
        "note": "右键可打开关闭，照明。打开后可切换到别的道具仍有光，但猎杀时吸引鬼，可用T键快速开关。"
    },
    "头戴式摄像机": {
        "level1": "等级1:相机头戴，可供车上玩家观看佩戴者视角，可以车上电脑打开夜视，不会吸引鬼。",
        "level2": "等级2:手电筒头戴，长摁T打开关闭，头上有个手电筒(会被禁用)，光照角度小，亮度低，猎杀时打开会吸引鬼。",
        "level3": "等级3:夜视仪，长摁T打开关闭，受电子干扰影响，且猎杀时打开会吸引鬼。",
        "note": "玩家获取后，不会占用手和背包栏。一人仅可使用一个。"
    },
    "运动传感器": {
        "level1": "等级1:初级运传，贴在物体上或放在地面上，检测直线方向是否有鬼魂经过(包括人)，若有会闪白光。",
        "level2": "等级2:中级运传，可以再放之后与之互动切换形态(单线/双线/关闭)，被触发时还有音频提示。",
        "level3": "等级3:高级运传，扫描型，鬼魂进入或离开范围，会移动并闪烁白光并发出声音。",
        "note": "等级1:摁F可放置，鬼，死亡玩家，玩家通过会发光，且车上显示屏会有提示和声音提示。"
    },
    "收音器(大锅)": {
        "level1": "等级1:初级收音器，能够接收的最大范围为20m。",
        "level2": "等级2:带示数收音器，接收声音最大范围为30m，且会在屏幕上显示示数。",
        "level3": "等级3:高级收音器，接收声音最大范围为30m，且会在屏幕上显示声音与本人的位置关系(可以收到楼上楼下一层的声音)。",
        "note": "右键打开或关闭，能够听到瞄准方向的互动声音，在鬼魂附近可以收到低语。"
    },
    "★紫外线手电筒": {
        "level1": "等级1:紫外线手电筒，右键可打开关闭，可用于照明，类手电筒，无法后台使用。充能速度中。",
        "level2": "等级2:荧光棒，右键使用，光照范围会随时间逐渐变小而后不变(右键摇一摇变亮)。充能慢。",
        "level3": "等级3:紫外线手电筒Pro，等同于等级2，光照范围更大，亮度更高，充能最快。",
        "note": "可用于观察指纹和足迹(紫外线照射会充能)，充能一段时间(与充能多少有关)可以肉眼看到拍照。"
    },
    "录音机": {
        "level1": "等级1:录制时提示灯会变为绿色。识别范围3m。",
        "level2": "等级2:录制时会出现进度条。识别范围5m。",
        "level3": "等级3:录制时中间会出现一个圆圈。识别范围5m,会显示距离和方向。",
        "note": "录音机可以被切换至打开,而后其会开始扫描附近鬼魂产生的声音,使用右键可以录制特殊声音。"
    }
}

# ---- 任务列表 ----
DEFAULT_TASKS = [
    "捕获鬼魂照片——$25",
    "团队成员之一见证灵异事件——$25",
    "让鬼吹灭火光——$30",
    "用十字架阻止鬼猎杀——$25",
    "团队成员之一逃脱猎杀——$25",
    "猎杀时点燃熏香驱散鬼魂——$30",
    "在鬼附近区域使用熏香——$30",
    "用收音器检测超自然声音——$25",
    "拍摄任何成功的EMF读取照片——$25",
    "用运动传感器检测鬼活动——$25",
    "平均理智低于25%——$25",
    "拍摄一个鬼魂的影片——$25",
    "使用照相机捕捉3段独特的照片——$25",
    "使用摄像机捕捉3段独特的影片——$25",
    "使用录音机捕捉2个独特的超自然声音——$25"
]

# ---- 徽章数据 ----
DEFAULT_BADGES = {
    "声望徽章1-10": "静态徽章，升级声望获得。",
    "声望徽章11-20": "动态徽章，升级声望获得。",
    "天启奖杯徽章": "完成天启难度挑战（阳光牧院，单人，正确判鬼，完成三个任务，拍鬼照并活着结算）。",
    "灯塔守望者徽章": "希望角灯塔判对鬼魂50次。",
    "溺魂摆渡者徽章": "完成灯塔隐藏任务（球、齿轮、敲钟、紫光灯照大灯）。",
    "护林员徽章": "营地（大/小）判对鬼魂50次。",
    "病友徽章": "阳光牧院判对鬼魂50次。",
    "猎人徽章": "完成全部54个成就。"
}

# ---- 通灵物数据 ----
DEFAULT_CURSED = {
    "塔罗牌": {
        "usage": "塔罗牌可以被拿起后使用鼠标右键抽取一张牌，塔罗牌仅可在调查区域内抽取。每副塔罗牌有10张牌，每个牌有独特的影响。每张牌的抽取概率随机，即一副牌可能不存在某些牌。注：当10张牌均抽取完毕后，后续所有猎杀时间延长20s，无论是否抽取到猎杀(Death)牌。",
        "curse_hunt": "塔罗牌本身不直接触发诅咒猎杀，但猎杀时抽取塔罗牌均为愚者牌。",
        "other": "10张牌的效果：Tower(互动)、Wheel of Fortune(命运之轮)、Fool(愚者)、Devil(现身)、Death(猎杀)、Hermit(禁锢)、Sun(太阳)、Moon(月亮)、High Priestess(女祭司)、Hanged Man(倒吊人)。"
    },
    "通灵板": {
        "usage": "如果玩家没有拿着通灵板，可以通过鼠标左键单击以激活通灵板，或在拿着通灵板的时候使用鼠标右键激活。当占卜板出现时，标志通灵板已激活。玩家可以使用语音或文本进行提问。",
        "curse_hunt": "激活的通灵板5m内没有玩家、提问的玩家理智不足、触发躲猫猫时通灵板碎裂并触发诅咒猎杀。",
        "other": "可提问：你在哪？(消耗50%理智)、你在附近么？(20%)、骨头位置(20%)、躲猫猫(延迟5s诅咒猎杀)、年龄等(5%)。"
    },
    "闹鬼魔镜": {
        "usage": "在调查区域内可以使用鼠标右键激活魔镜，展示鬼房的全景。",
        "curse_hunt": "使用者的理智流逝到0%或激活前理智低于20%时触发诅咒猎杀。",
        "other": "每次使用消耗理智为max(20%，7.5%×使用秒数)。"
    },
    "八音盒": {
        "usage": "拿起后右键激活，八音盒在猎杀期间无法使用，只能使用一次。激活后若鬼魂在20m内会跟着唱歌，5m内触发鬼魂事件。",
        "curse_hunt": "鬼魂与玩家极近、鬼魂事件移动超过5s、八音盒被扔出、玩家理智0%时触发诅咒猎杀。",
        "other": "激活的八音盒2.5m内玩家理智以2.5%/s流逝，完整一首歌消耗约75%理智。"
    },
    "召唤阵": {
        "usage": "手持点火器点燃所有五根蜡烛，每支蜡烛扣16%理智。",
        "curse_hunt": "五根蜡烛全部点燃后，鬼魂被召唤并实体化，5s后无法移动和猎杀，随后触发诅咒猎杀。",
        "other": "点燃最后一根蜡烛时理智≤16%则无5s禁锢直接猎杀。"
    },
    "巫毒娃娃": {
        "usage": "与巫毒娃娃互动会使随机一根针插入，消耗5%理智并强制互动。摁下心脏位置的针消耗10%理智。",
        "curse_hunt": "摁下心脏位置的针或使用者理智0%时所有剩余针插入触发诅咒猎杀。",
        "other": "强制互动可导致EMF和紫外线，但不会触发笔记和点阵。"
    },
    "猴爪": {
        "usage": "猴爪的可许愿次数与难度倍数相关（0-1.99:5次, 2-2.99:4次, 3以上:3次）。可用语音或文本许愿。",
        "curse_hunt": "希望见鬼、希望困住鬼、渴望知识等愿望会触发诅咒猎杀。",
        "other": "其他愿望：希望鬼活动活动、希望清醒、希望安全、希望离开、希望复活队友、改变天气、希望获得任何东西。"
    }
}

# ---- 媒体数据 ----
DEFAULT_MEDIA = {
    "照片": {
        "鬼照": 10, "点阵鬼影": 10, "鬼魂暗影(虚化的鬼)": 10, "半透明鬼魂": 10, "薄雾形态鬼魂(白雾哈气)": 10,
        "骨头": 5, "燃烧的十字架": 5, "尸体": 5, "脏水": 5, "EMF读数(拍EMF)": 5, "幻妖指纹": 10, "指纹": 5,
        "脚印": 5, "刺骨寒温(拍温度计)": 10, "鬼魂笔记": 10, "互动": 5, "诅咒道具(每个都算)": 5
    },
    "录像": {
        "猎杀中的鬼魂": 20, "鬼照": 10, "点阵鬼影": 10, "鬼魂暗影(虚化的鬼)": 10, "半透明鬼魂": 10,
        "薄雾形态鬼魂(白雾哈气)": 10, "燃烧的十字架": 10, "尸体": 10, "脏水": 5, "踩盐": 5, "动门": 5,
        "吹灭火焰": 5, "点燃火焰": 5, "鬼魂笔记": 10, "灵球": 10, "闪灯": 5, "爆灯": 5, "开关灯": 5,
        "运动传感器": 5, "移动物品": 5, "手机响": 5, "收音机响": 5, "摇椅晃动": 5, "淋雨花洒出水": 5,
        "回应通灵板": 5, "幽灵变形": 20
    },
    "录音": {
        "女妖尖叫": 10, "雾影喘息": 10, "猎杀中的鬼魂": 20, "薄雾形态鬼魂(白雾哈气)": 10, "燃烧的十字架": 5,
        "EMF响": 10, "吹灭火焰": 5, "鬼魂事件": 10, "鬼魂笔记(飞起来写字的音效)": 10, "超自然声音": 5,
        "玩具(鬼互动玩具有小孩笑声)": 5, "收音机响": 5, "通灵盒回复": 10, "八音盒": 5, "通灵板回应": 5
    }
}

# ---- 其他信息（地图、天气、通用设定、证据）----
DEFAULT_MISC = {
    "maps_summary": {
        "小图": "6号房 10号房 13号房 42号房 双层木屋(G开头) 小营地(Camp Woodwind)",
        "中图": "三层木屋(B开头) 灯塔 小阳光牧院 监狱 大营地(Maple Lodge Campsite)",
        "大图": "学校 阳光牧院"
    },
    "maps_detail": [
        {"name": "6号房", "size": "小", "difficulty": "简单", "features": "新手图，结构简单，适合熟悉游戏"},
        {"name": "10号房", "size": "小", "difficulty": "简单", "features": "单层住宅，容易找到鬼房"},
        {"name": "13号房", "size": "小", "difficulty": "中等", "features": "两层结构，有长走廊"},
        {"name": "42号房", "size": "小", "difficulty": "中等", "features": "厨房区域互动多，藏身点较少"},
        {"name": "双层木屋(G开头)", "size": "小", "difficulty": "中等", "features": "木制结构，脚步声明显"},
        {"name": "小营地(Camp Woodwind)", "size": "小", "difficulty": "中等", "features": "户外帐篷区，视野开阔"},
        {"name": "三层木屋(B开头)", "size": "中", "difficulty": "困难", "features": "三层结构，楼梯多，易迷路"},
        {"name": "灯塔", "size": "中", "difficulty": "困难", "features": "垂直型地图，每层空间小，躲藏点稀缺"},
        {"name": "小阳光牧院", "size": "中", "difficulty": "困难", "features": "精神病院风格，房间多"},
        {"name": "监狱", "size": "中", "difficulty": "困难", "features": "金属门，视野受限，回声大"},
        {"name": "大营地(Maple Lodge Campsite)", "size": "中", "difficulty": "困难", "features": "大型户外地图，多帐篷和木屋"},
        {"name": "学校", "size": "大", "difficulty": "专家", "features": "巨大地图，多教室，鬼魂容易换房"},
        {"name": "阳光牧院", "size": "大", "difficulty": "专家", "features": "最大地图，分主楼和庭院"}
    ],
    "weather": {
        "日出": "照明适当 视野适当 噪音适当 温度16℃",
        "晴朗": "照明极差 视野高 噪音低 温度13℃",
        "雾天": "照明适当 视野极差 噪音低 温度13℃",
        "小雨": "照明适当 视野高 噪音适当 温度8℃",
        "暴雨": "照明极差 视野适当 噪音高 温度8℃",
        "刮风": "照明极差 视野高 噪音适当 温度8℃",
        "降雪": "照明适当 视野适当 噪音低 温度5℃",
        "血月": "照明适当 视野高 噪音适当 温度8℃ 互动和事件概率增加 +15%鬼速 50%理智掉落"
    },
    "general": "猎杀间隔25s，圣木燃烧时间5/6/7s，圣木效果5s，再次猎杀需90s\n脚步传播20m，电器影响10m，十字架挡猎3/4/4m\n对电器感知/干扰10m，猎杀时周围物品每0.5s 50%概率互动\n现身哈气有白雾和实体两种。视野加速：1.65倍，持续13s\n猎杀时间(低/中/高)：小图(15/20/40) 中图(20/30/50) 大图(30/40/60)\n诅咒猎杀+20s，模型不更换（睡衣女鬼、小孩鬼有特殊形态）",
    "Evidence": {
        "EMF5级": "互动(2级/3级，包括但不限于咬十字架，动门，敲窗等)的25%概率给EMF5级",
        "紫外线": "鬼在动门，敲窗，动键盘，开关时会留下指纹，踩盐会留下足迹(指纹和足迹均需要紫外线设备)",
        "鬼魂笔迹": "鬼互动笔记在笔记上写下内容(踢笔记代表无证据或隐藏证据)",
        "通灵盒": "在鬼的附近使用，会得到回应(关灯且可能需房间无其他人)",
        "刺骨寒温": "1℃以下，口吐寒气不是刺骨",
        "点阵": "鬼魂进入点阵可见状态时处于点阵范围内会显现(死亡玩家不可见)",
        "灵球": "摄像机的夜视模式可看到漂浮的白点为灵球(三级头戴不可见，出现在鬼房)"
    }
}

# 地图图片 base64（默认为空，使用外部图片）
MAP_IMAGES_BASE64 = {}

# ======================== 数据加载函数 ========================
def load_json_file(filename, default_data):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return default_data

def load_map_image_pil(map_name):
    """加载地图图片，返回 PIL Image 对象（如果可用），否则返回 None"""
    img_dir = os.path.join(DATA_DIR, "map_images")
    if os.path.exists(img_dir):
        exts = [".png", ".gif"]
        if PIL_AVAILABLE:
            exts.extend([".jpg", ".jpeg", ".bmp"])
        for ext in exts:
            img_path = os.path.join(img_dir, f"{map_name}{ext}")
            if os.path.exists(img_path):
                try:
                    if PIL_AVAILABLE:
                        return Image.open(img_path)
                    else:
                        return None
                except Exception:
                    continue
    b64 = MAP_IMAGES_BASE64.get(map_name)
    if b64 and PIL_AVAILABLE:
        try:
            img_data = base64.b64decode(b64)
            return Image.open(BytesIO(img_data))
        except Exception:
            pass
    return None

def load_map_image_photo(map_name):
    """直接返回 PhotoImage（无缩放能力，仅用于无 PIL 时）"""
    img_dir = os.path.join(DATA_DIR, "map_images")
    if os.path.exists(img_dir):
        exts = [".png", ".gif"]
        for ext in exts:
            img_path = os.path.join(img_dir, f"{map_name}{ext}")
            if os.path.exists(img_path):
                try:
                    return tk.PhotoImage(file=img_path)
                except Exception:
                    continue
    return None

# ======================== GUI 程序 ========================
class PhasmoSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("恐鬼症数据exe 作者闲鱼  数据来源玥猫cat 英文Wiki")
        self.root.geometry("1100x750")
        # 设置全局默认字体（加大）
        default_font = ("微软雅黑", 12)
        self.root.option_add("*Font", default_font)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.ghosts = load_json_file("ghosts.json", DEFAULT_GHOSTS)
        self.equipment = load_json_file("equipment.json", DEFAULT_EQUIPMENT)
        self.tasks = load_json_file("tasks.json", DEFAULT_TASKS)
        self.badges = load_json_file("badges.json", DEFAULT_BADGES)
        self.cursed = load_json_file("cursed_items.json", DEFAULT_CURSED)
        self.media = load_json_file("media.json", DEFAULT_MEDIA)
        self.misc = load_json_file("misc.json", DEFAULT_MISC)
        self.map_data = self.misc.get("maps_detail", [])

        # 缩放相关属性
        self.current_map_pil = None
        self.current_map_photo = None
        self.current_map_name = None
        self.current_zoom = 1.0
        self.map_canvas = None
        self.map_image_id = None
        self.zoom_label = None

        self.create_ghost_tab()
        self.create_equipment_tab()
        self.create_tasks_badges_tab()
        self.create_cursed_tab()
        self.create_media_tab()
        self.create_map_tab()
        self.create_misc_tab()

    # ------------------- 鬼魂标签页 -------------------
    def create_ghost_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="鬼魂特性")
        left = tk.Frame(frame, width=220)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Label(left, text="鬼魂列表", font=("Arial",12,"bold")).pack(pady=5)
        self.ghost_list = tk.Listbox(left, height=28, font=("Arial",10))
        self.ghost_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(left, orient=tk.VERTICAL, command=self.ghost_list.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.ghost_list.config(yscrollcommand=sb.set)

        for name in GHOST_NAMES:
            self.ghost_list.insert(tk.END, name)

        right = tk.Frame(frame)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.ghost_title = tk.Label(right, text="", font=("Arial",14,"bold"))
        self.ghost_title.pack(pady=5)

        info = tk.LabelFrame(right, text="基本信息")
        info.pack(fill=tk.X, pady=5)
        tk.Label(info, text="速度：").grid(row=0, column=0, sticky='w', padx=5)
        self.speed = tk.Label(info, text="", anchor='w')
        self.speed.grid(row=0, column=1, sticky='w', padx=5)
        tk.Label(info, text="证据：").grid(row=1, column=0, sticky='w', padx=5)
        self.evidence = tk.Label(info, text="", anchor='w')
        self.evidence.grid(row=1, column=1, sticky='w', padx=5)
        tk.Label(info, text="猎杀阈值：").grid(row=2, column=0, sticky='w', padx=5)
        self.threshold = tk.Label(info, text="", anchor='w')
        self.threshold.grid(row=2, column=1, sticky='w', padx=5)

        ability_frame = tk.LabelFrame(right, text="能力描述")
        ability_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.ability_text = scrolledtext.ScrolledText(ability_frame, wrap=tk.WORD, height=14, state='disabled')
        self.ability_text.pack(fill=tk.BOTH, expand=True)

        self.ghost_list.bind('<<ListboxSelect>>', self.on_ghost_select)
        if GHOST_NAMES:
            self.ghost_list.selection_set(0)
            self.on_ghost_select(None)

    def on_ghost_select(self, event):
        sel = self.ghost_list.curselection()
        if not sel: return
        name = self.ghost_list.get(sel[0])
        data = self.ghosts.get(name, {})
        self.ghost_title.config(text=name)
        self.speed.config(text=data.get("speed", ""))
        self.evidence.config(text=data.get("evidence", ""))
        self.threshold.config(text=data.get("hunt_threshold", ""))
        self.ability_text.config(state='normal')
        self.ability_text.delete(1.0, tk.END)
        self.ability_text.insert(tk.END, data.get("ability", ""))
        self.ability_text.config(state='disabled')

    # ------------------- 装备标签页 -------------------
    def create_equipment_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="装备道具")
        left = tk.Frame(frame, width=250)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Label(left, text="装备列表", font=("Arial",12,"bold")).pack(pady=5)
        equip_list = tk.Listbox(left, height=25)
        equip_list.pack(fill=tk.BOTH, expand=True)
        for name in sorted(self.equipment):
            equip_list.insert(tk.END, name)

        right = tk.Frame(frame)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        title = tk.Label(right, text="", font=("Arial",14,"bold"))
        title.pack(pady=5)
        note = tk.Label(right, text="", wraplength=500, fg="blue")
        note.pack(fill=tk.X, pady=5)
        text_area = scrolledtext.ScrolledText(right, wrap=tk.WORD, height=20, state='disabled')
        text_area.pack(fill=tk.BOTH, expand=True)

        def on_select(event):
            sel = equip_list.curselection()
            if not sel: return
            name = equip_list.get(sel[0])
            data = self.equipment[name]
            title.config(text=name)
            note.config(text=data.get("note", ""))
            info = f"【等级1】\n{data.get('level1','')}\n\n【等级2】\n{data.get('level2','')}\n\n【等级3】\n{data.get('level3','')}"
            text_area.config(state='normal')
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, info)
            text_area.config(state='disabled')

        equip_list.bind('<<ListboxSelect>>', on_select)

    # ------------------- 任务与徽章 -------------------
    def create_tasks_badges_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="任务与徽章")
        task_frame = tk.LabelFrame(frame, text="游戏任务")
        task_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)
        task_list = tk.Listbox(task_frame)
        task_list.pack(fill=tk.BOTH, expand=True)
        for t in self.tasks:
            task_list.insert(tk.END, t)

        badge_frame = tk.LabelFrame(frame, text="徽章与名片")
        badge_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=5, pady=5)
        badge_text = scrolledtext.ScrolledText(badge_frame, wrap=tk.WORD, state='normal')
        badge_text.pack(fill=tk.BOTH, expand=True)
        for name, desc in self.badges.items():
            badge_text.insert(tk.END, f"【{name}】\n{desc}\n\n")
        badge_text.config(state='disabled')

    # ------------------- 通灵物 -------------------
    def create_cursed_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="通灵物")
        left = tk.Frame(frame, width=200)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Label(left, text="诅咒道具", font=("Arial",12,"bold")).pack(pady=5)
        cursed_list = tk.Listbox(left)
        cursed_list.pack(fill=tk.BOTH, expand=True)
        for name in self.cursed:
            cursed_list.insert(tk.END, name)

        right = tk.Frame(frame)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        title = tk.Label(right, text="", font=("Arial",14,"bold"))
        title.pack(pady=5)
        text_area = scrolledtext.ScrolledText(right, wrap=tk.WORD, height=25, state='disabled')
        text_area.pack(fill=tk.BOTH, expand=True)

        def on_select(event):
            sel = cursed_list.curselection()
            if not sel: return
            name = cursed_list.get(sel[0])
            data = self.cursed[name]
            title.config(text=name)
            info = f"【使用方法】\n{data.get('usage','')}\n\n【诅咒猎杀条件】\n{data.get('curse_hunt','')}\n\n【其他影响】\n{data.get('other','')}"
            text_area.config(state='normal')
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, info)
            text_area.config(state='disabled')

        cursed_list.bind('<<ListboxSelect>>', on_select)

    # ------------------- 媒体系统 -------------------
    def create_media_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="媒体系统")
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        for cat, data in self.media.items():
            sub = ttk.Frame(notebook)
            notebook.add(sub, text=cat)
            tree = ttk.Treeview(sub, columns=("item","reward"), show="headings")
            tree.heading("item", text="类型")
            tree.heading("reward", text="独特奖励")
            tree.column("item", width=250)
            tree.column("reward", width=100)
            for item, reward in data.items():
                tree.insert("", tk.END, values=(item, reward))
            tree.pack(fill=tk.BOTH, expand=True)
            sb = ttk.Scrollbar(sub, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=sb.set)
            sb.pack(side=tk.RIGHT, fill=tk.Y)

    # ------------------- 地图标签页（滚动 Canvas 支持缩放）-------------------
    def create_map_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="地图")

        left = tk.Frame(frame, width=200)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Label(left, text="地图列表", font=("Arial",12,"bold")).pack(pady=5)
        self.map_listbox = tk.Listbox(left, height=20, font=("Arial",10))
        self.map_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(left, orient=tk.VERTICAL, command=self.map_listbox.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.map_listbox.config(yscrollcommand=sb.set)

        for m in self.map_data:
            self.map_listbox.insert(tk.END, m.get("name", ""))

        right = tk.Frame(frame)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.map_title = tk.Label(right, text="", font=("Arial",14,"bold"))
        self.map_title.pack(pady=5)

        info_frame = tk.LabelFrame(right, text="地图信息")
        info_frame.pack(fill=tk.X, pady=5, padx=5)
        tk.Label(info_frame, text="尺寸：").grid(row=0, column=0, sticky='w', padx=5)
        self.map_size = tk.Label(info_frame, text="", anchor='w')
        self.map_size.grid(row=0, column=1, sticky='w', padx=5)
        tk.Label(info_frame, text="难度：").grid(row=1, column=0, sticky='w', padx=5)
        self.map_difficulty = tk.Label(info_frame, text="", anchor='w')
        self.map_difficulty.grid(row=1, column=1, sticky='w', padx=5)
        tk.Label(info_frame, text="特点：").grid(row=2, column=0, sticky='w', padx=5)
        self.map_features = tk.Label(info_frame, text="", anchor='w', wraplength=400, justify=tk.LEFT)
        self.map_features.grid(row=2, column=1, sticky='w', padx=5)

        # 缩放按钮区
        btn_frame = tk.Frame(right)
        btn_frame.pack(fill=tk.X, pady=5, padx=5)
        zoom_in_btn = tk.Button(btn_frame, text="🔍 放大", command=self.zoom_in, width=8)
        zoom_in_btn.pack(side=tk.LEFT, padx=5)
        zoom_out_btn = tk.Button(btn_frame, text="🔍 缩小", command=self.zoom_out, width=8)
        zoom_out_btn.pack(side=tk.LEFT, padx=5)
        reset_zoom_btn = tk.Button(btn_frame, text="⟳ 重置", command=self.reset_zoom, width=8)
        reset_zoom_btn.pack(side=tk.LEFT, padx=5)
        self.zoom_label = tk.Label(btn_frame, text="100%", width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=10)

        # 带滚动条的 Canvas 预览区
        img_frame = tk.LabelFrame(right, text="地图预览（滚轮缩放 / 拖动滚动条）")
        img_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        canvas_container = tk.Frame(img_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.map_canvas = tk.Canvas(canvas_container, bg="gray90", highlightthickness=0)
        h_scroll = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.map_canvas.xview)
        v_scroll = tk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.map_canvas.yview)
        self.map_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        self.map_canvas.grid(row=0, column=0, sticky="nsew")
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)

        # 绑定鼠标滚轮事件
        def on_mousewheel(event):
            # 按下 Ctrl 键时缩放，否则滚动
            if event.state & 0x0004:  # Ctrl 键
                if event.delta > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()
            else:
                self.map_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.map_canvas.bind("<MouseWheel>", on_mousewheel)
        # 绑定水平滚动（Shift+滚轮）
        def on_shift_mousewheel(event):
            self.map_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        self.map_canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel)

        self.map_image_id = None

        self.map_listbox.bind('<<ListboxSelect>>', self.on_map_select)
        if self.map_data:
            self.map_listbox.selection_set(0)
            self.on_map_select(None)

    def on_map_select(self, event):
        sel = self.map_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        m = self.map_data[idx]
        name = m.get("name", "")
        self.current_map_name = name
        self.map_title.config(text=name)
        self.map_size.config(text=m.get("size", ""))
        self.map_difficulty.config(text=m.get("difficulty", ""))
        self.map_features.config(text=m.get("features", ""))

        # 加载图片（PIL 图像）
        self.current_map_pil = load_map_image_pil(name)
        if self.current_map_pil:
            self.current_zoom = 1.0
            self.update_zoom_label()
            self.display_map_image()
        else:
            # 无 PIL，尝试加载直接 PhotoImage
            photo = load_map_image_photo(name)
            if self.map_image_id:
                self.map_canvas.delete(self.map_image_id)
            if photo:
                width = photo.width()
                height = photo.height()
                self.map_canvas.config(scrollregion=(0, 0, width, height))
                self.map_image_id = self.map_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.current_map_photo = photo
            else:
                self.map_canvas.config(scrollregion=(0, 0, 400, 300))
                self.map_image_id = self.map_canvas.create_text(200, 150, text="暂无预览图", anchor=tk.CENTER, font=("Arial",14))

    def display_map_image(self):
        """根据当前 self.current_map_pil 和 self.current_zoom 缩放并显示图片"""
        if not self.current_map_pil:
            return
        orig_w, orig_h = self.current_map_pil.size
        new_w = int(orig_w * self.current_zoom)
        new_h = int(orig_h * self.current_zoom)
        resized = self.current_map_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        if self.map_image_id:
            self.map_canvas.delete(self.map_image_id)
        self.map_canvas.config(scrollregion=(0, 0, new_w, new_h))
        self.map_image_id = self.map_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.current_map_photo = photo

    def zoom_in(self):
        if not self.current_map_pil:
            return
        self.current_zoom *= 1.25
        if self.current_zoom > 4.0:
            self.current_zoom = 4.0
        self.update_zoom_label()
        self.display_map_image()

    def zoom_out(self):
        if not self.current_map_pil:
            return
        self.current_zoom /= 1.25
        if self.current_zoom < 0.1:
            self.current_zoom = 0.1
        self.update_zoom_label()
        self.display_map_image()

    def reset_zoom(self):
        if not self.current_map_pil:
            return
        self.current_zoom = 1.0
        self.update_zoom_label()
        self.display_map_image()

    def update_zoom_label(self):
        if self.zoom_label:
            percent = int(self.current_zoom * 100)
            self.zoom_label.config(text=f"{percent}%")

    # ------------------- 其他信息标签页 -------------------
    def create_misc_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="恐鬼症通用信息")
        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("微软雅黑", 12))
        text.pack(fill=tk.BOTH, expand=True)

        # 地图分类
        text.insert(tk.END, "【地图分类】\n")
        for size, maps in self.misc.get("maps_summary", {}).items():
            text.insert(tk.END, f"{size}：{maps}\n")

        # 天气效果
        text.insert(tk.END, "\n【天气效果】\n")
        for weather, effect in self.misc.get("weather", {}).items():
            text.insert(tk.END, f"{weather}：{effect}\n")

        # 通用设定
        text.insert(tk.END, "\n【通用设定】\n" + self.misc.get("general", ""))

        # 证据说明（字典格式）
        evidence_dict = self.misc.get("Evidence", {})
        text.insert(tk.END, "\n\n【证据说明】\n")
        if evidence_dict:
            for ev_name, ev_desc in evidence_dict.items():
                text.insert(tk.END, f"• {ev_name}：{ev_desc}\n")
        else:
            text.insert(tk.END, "暂无证据数据\n")

        text.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = PhasmoSystem(root)
    root.mainloop()