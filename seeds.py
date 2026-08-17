"""TapTap AI 游戏候选池 —— 人工核实的种子名单（排除 TapTap Maker 产出）

来源：券商研报（华泰/东吴传媒 AI 游戏专题）、ChinaJoy 2026 展会报道、
GameLook / 触乐 / 腾讯新闻深度报道、TapTap 官方标签页 SSR。

字段说明：
  name        游戏名
  layer       L1 运行时AI原生 / L2 运行时AI增强 / L3 生产管线AI重度
  evidence    判定依据（会在采集后与 TapTap 简介交叉验证）
  src         证据来源
"""

SEEDS = [
    # ===== L1 运行时 AI 原生 =====
    dict(name='群星低语-Whispers from the Star', app_id=746715, layer='L1',
         company='蔡浩宇 AI 创业公司（Anuttacon）', city='美国/新加坡',
         evidence='实时文字、语音、视频通话驱动剧情，玩家话语决定角色命运，无固定选项',
         src='TapTap 官方简介 + 研报'),
    dict(name='福尔摩斯：暗夜追踪者', app_id=None, layer='L1',
         company='上海美酷瑞（MacRoy）', city='上海',
         evidence='数十个 AI 扮演 NPC，无剧情选项，AI 逻辑判定系统按对话逻辑与情绪识别判定任务完成度；自研情绪表演系统 100+ 面部骨骼、实时语音引擎',
         src='字符无限科技报道；创始人为前盛大游戏 VP 朱笑靖、前 B 站游戏事业部负责人吴昀贇'),
    dict(name='乌托', app_id=None, layer='L1',
         company='谦贞数字 / 乌宝工作室', city='待核实',
         evidence='AI 人格化模拟（MBTI 式人格），模拟经营+换装+家园+角色互动，吸收跑团与 OC 企划玩法；团队持 6 个 AI 技术发明专利',
         src='腾讯新闻深度报道 2026-03；TapTap 新品榜第 2、预约榜第 5'),
    dict(name='不问凡尘', app_id=None, layer='L1',
         company='字节跳动 江南工作室', city='上海/杭州',
         evidence='基于 Seedance 模型的 AI 真人 RPG，玩家选择以非剧情方式累积影响数值与世界反馈，内置 AI 驱动 NPC 说服玩法',
         src='东吴传媒 ChinaJoy 2026 点评报告'),
    dict(name='AI小镇：星原', app_id=None, layer='L1',
         company='待核实', city='待核实',
         evidence='玩家养成、观察并引导自主生活的 Agent，不同玩家的 Agent 会互动并相互影响',
         src='东吴传媒 ChinaJoy 2026 点评报告'),
    dict(name='混想局', app_id=None, layer='L1',
         company='待核实', city='待核实',
         evidence='玩家自由输入或词条组合，AI 即时生成角色、技能与流派，随机事件中组建战队',
         src='东吴传媒 ChinaJoy 2026 点评报告'),
    dict(name='黑箱：无限构筑', app_id=None, layer='L1',
         company='待核实', city='待核实',
         evidence='数百种底层原子项动态重组生成独特技能，Roguelike 构筑',
         src='东吴传媒 ChinaJoy 2026 点评报告'),
    dict(name='MoMo', app_id=None, layer='L1',
         company='待核实', city='待核实',
         evidence='实时同步玩家所在城市天气与活动信息，与 AI NPC 玩游戏、办公、看电影，上下文驱动陪伴',
         src='东吴传媒 ChinaJoy 2026 点评报告'),
    dict(name='假如我是人工智能If I am AI', app_id=None, layer='L1',
         company='待核实', city='待核实',
         evidence='TapTap 官方 AI 标签收录，评分 9.5，AI 主题玩法',
         src='TapTap /tag/AI 标签页'),
    dict(name='异常', app_id=None, layer='L1',
         company='待核实', city='待核实',
         evidence='TapTap 官方 AI 标签收录，评分 9.6，标签为策略/编程/烧脑',
         src='TapTap /tag/AI 标签页'),
    dict(name='AIFriends', app_id=771203, layer='L1',
         company='上海惊喜先生科技有限公司', city='上海',
         evidence='AI 伙伴养成，UGC 版本支持上传角色模型、设定人格与故事、克隆音色、亲密度养成',
         src='TapTap 官方详情页；上线 2025-08-30，关注 11 万'),
    dict(name='EVE', app_id=None, layer='L1',
         company='自然选择（深圳）智能有限公司', city='深圳',
         evidence='AI 伴侣，3D 实时通话支持摄像头视觉输入，好感度解锁剧情，陪伴/家园/朋友圈系统',
         src='媒体报道；2026-04-10 上线，iOS + TapTap'),
    dict(name='星眠', app_id=None, layer='L1',
         company='待核实', city='待核实',
         evidence='AI 陪伴乙女手游，AI 动态陪伴系统实时生成对话，Live2D 触摸互动+模拟经营',
         src='媒体报道；2026-07-21 开启预约'),
    dict(name='赎命电波', app_id=None, layer='L1',
         company='待核实', city='待核实',
         evidence='接入 AI 赋予 NPC 自由交互，或玩家与 AI 对话共同续写故事',
         src='东吴传媒 ChinaJoy 2026 点评报告'),
    dict(name='重生之我在产业园当AI', app_id=None, layer='L1',
         company='待核实', city='待核实',
         evidence='AI 对话驱动叙事，玩家在设定世界观下与 AI 共同续写故事',
         src='东吴传媒 ChinaJoy 2026 点评报告'),
    dict(name='流言侦探', app_id=None, layer='L2',
         company='待核实', city='待核实',
         evidence='模拟 AI 社交与真人聊天体验，多线结局；评分 9.2，编辑推荐',
         src='TapTap 首页推荐位'),

    # ===== L2 运行时 AI 增强 =====
    dict(name='超自然行动组', app_id=None, layer='L2',
         company='巨人网络', city='上海',
         evidence='内置 AI 驱动「AI 假人」，接入千问模型，理解玩家语义、复刻真人音色、模拟语言风格与行动逻辑；上线首周 AI NPC 与真人对局超 2500 万次',
         src='腾讯新闻《中国游戏进入与AI同游时代》；上线一年 DAU 破千万、流水超 50 亿'),
    dict(name='麦琪的花园', app_id=None, layer='L2',
         company='待核实', city='待核实',
         evidence='像素沙盒冒险，AI 生成 AI 伙伴的外貌、性格、职业、背景故事及对应任务剧情道具；公开披露用低价模型替换高价模型使 Token 成本降约 80%，将模型消耗封装为「AI 伙伴招募」商品',
         src='东吴传媒 ChinaJoy 2026 点评报告（少见的公开披露 AI 成本结构案例）'),
]
