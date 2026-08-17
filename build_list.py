"""生成拜访追踪清单（CSV）+ 单文件 HTML 看板。

清单字段按「实地拜访 / 商务追踪」用途设计，而非单纯游戏数据展示。

召回方法论（2026-08-17 修正后）：
  漏检教训 —— 《历史模拟器：崇祯》(app 813198) 曾被漏掉。它是国内首款 AI 原生
  历史策略游戏，但 TapTap 页面标签只有「策略」，简介全文不含 "AI" 与 "大模型"
  （用「世界推演模型」表述），且因 4 月走 Steam 首发未进 ChinaJoy 研报名单，
  导致标签召回、关键词召回、研报名单召回三条路径同时失效。

  由此确立三条规则：
  1. 平台元数据不可作为判定依据。TapTap 标签与简介均由厂商/平台填写，AI 游戏
     常主动回避 "AI" 字样（国内舆论环境下 AI 是负资产）。
  2. 关键词词表必须做反向验证。新增词表后，须用已知 AI 游戏做召回率抽查，
     确认能命中再投入使用，不能假设"简介里会写"。
     实测（validate_recall.py，5 款已知 AI 游戏）：
       标签召回率 40%（2/5）· 简介召回率 80%（4/5）· 两者取并 80%（4/5）
     漏掉的那一款正是最重要的《历史模拟器：崇祯》。
  3. 证据优先级：玩家评价文本 / 第三方深度报道 > 厂商自述 > 平台标签。
     AI 游戏的真实证据在评论区和媒体报道里，不在商店页。
"""
import csv, json, io

# ============ 主数据 ============
# conf: A=已核实(公开可查的公司主体+AI机制描述) B=较可靠(权威媒体/研报单一来源) C=待核实
ROWS = [
    dict(
        game='历史模拟器：崇祯', app_id='813198', layer='L1',
        company='青干工作室', city='杭州滨江',
        founder='制作人 追青（游戏文案出身，无计算机背景；2023 年在大厂推 AI 原生管线未成，遂离职创业）；技术侧有算法工程师参与',
        team_size='最初 2 人，现不到 10 人；无美术团队',
        funding='未公开（已实现不亏钱，制作人称"商业化跑通"指未亏损）',
        ai_mech='国内首款 AI 原生历史策略游戏。玩家用自然语言撰写诏书，无固定选项、无预设事件树；AI 解析意图后调用系统数据、逻辑推演、更新上千维度数值（国库/民心/官僚忠诚/军队士气/天灾/义军/后金动向）。多模型协作分工：世界大势推演用强力模型，对话类用小尺寸模型。接入千问 3.5 / Gemini / DeepSeek。架构为大模型作"世界引擎"+ 数据库（PolarDB）作"记忆中枢"，与阿里云在 Prompt 优化与长记忆调优做过 POC 合作。专家模式采用步进式状态机+底层数据库，推演前提正确率 98.7%、Function Call 匹配率 99.86%',
        ai_cost='披露最彻底的案例。单次游玩 Token 消耗达 3000 万级；要求模型输出 80-120 token/秒（主流仅 50-60）才能把等待压到 2 分钟内；玩家成本约 1 元/小时（接近传统点卡）。首发采用 48 元买断+Token 内购，引发大量差评，Steam 好评率仅 54%（1265 条评测）；后开放自定义 API（仅约 20% 玩家使用），6/25 起因国产大模型能力提升与成本下降转为免费游玩',
        stage='2026-05-08 Steam 上线，已转免费；TapTap 评分 7.9、粉丝 3971。次日留存 75.1%，非工作日平均在线 7 小时，留存率 70-78.3%',
        channel='Steam + TapTap（app 813198，含电脑/主机版）',
        contact='TapTap 官方论坛 / Steam 社区；工作室位于杭州滨江',
        expo='未进 ChinaJoy 2026 名单（4 月即公测，走 Steam 首发路线）',
        other_product='已上线创意工坊与官方示范 MOD《罗马：塞维鲁》，框架可套用三国/武侠/修仙等题材',
        visit_value='最高，优先级应排在麦琪的花园之前。理由：一是唯一把 AI 原生做成商业产品并公开完整成本模型的团队（Token 消耗量级、吞吐要求、单位成本、定价翻车全过程都有公开数据）；二是不到 10 人无美术团队却跑出 7 小时日均时长，对你 3 人团队的《除役者》资源配置有直接参照；三是同在杭州，与乌托/谦贞数字可安排同一趟行程；四是制作人对"AI 原生"的定义最锐利——把 AI 剥离后游戏还能不能玩',
        conf='A',
        src='TapTap 详情页实时抓取（2026-08-17）/ 新华财经 2026-04-13 / IT之家 2026-05-12 / 36氪《翻车？第一款AI游戏仅剩54%好评》/ Vista天下次元制作人专访 2026-06-16 / 百度百科',
    ),
    dict(
        game='麦琪的花园 Magi Scapes', app_id='', layer='L1',
        company='深圳奥拓盖母科技有限公司 (AutoGame)', city='深圳',
        founder='张昊阳（前腾讯《和平精英》AI 负责人 / 内部AI项目《伊甸岛》制作人）',
        team_size='约 11 人（早期）',
        funding='多轮共数千万元：奇绩创坛、九合创投、璀璨资本（约10%）',
        ai_mech='全游戏逻辑架构在脚本语言上，可由AI实时生成与更新；上传图片或文字描述生成AI伙伴（含像素立绘），AI生成对话/剧情/物品/实时语音（中日英）；用RAG解决长期记忆',
        ai_cost='公开披露：用低价模型+代码替换高价模型，AI相关Token成本降约80%；将模型消耗封装为「AI伙伴招募」商品',
        stage='已三测，Steam 有 Demo，定档 Steam 新品节后移动端',
        channel='Steam + TapTap',
        contact='contact@autogame.ai / 官网 autogame.ai / B站 space.bilibili.com/1775149662',
        expo='CCG EXPO 2025、ChinaJoy 2026、深圳展 15号馆A47',
        other_product='AI游戏原生编辑器《代号:ADG》—— 自然语言在 UE5 中直接创作游戏',
        visit_value='最高。AI管线+AI玩法双线，且是极少数公开AI成本结构的团队；ADG 与你的 UE5 技术栈直接相关',
        conf='A',
        src='深圳新闻网企业名录/CCG EXPO报道/游戏艺术家专访/东吴传媒研报/企查查股权',
    ),
    dict(
        game='乌托 Agentopia', app_id='773812', layer='L1',
        company='杭州谦贞数字科技有限公司 / 乌宝工作室', city='杭州',
        founder='CEO 王金鹏（法国CNRS博士、之江实验室研究员）；产品 李玉全（哈工大+波尔多双硕士，法国IMS实验室NLP）；技术 贾新宇（前《天天狼人杀》负责人，前阿里云/百度云架构师）',
        team_size='9 人起步',
        funding='已完成第三轮融资',
        ai_mech='自研 JPAF 人格模拟算法（基于荣格八维认知理论），已在 arXiv 开源，为全球AI+分析心理学结合的首发研究之一；角色经历事件后会改变人格类型；深度角色定制+智能剧情生成',
        ai_cost='未公开',
        stage='2026-03-19 起 TapTap 不限量测试；TapTap 新品榜第2、预约榜第5',
        channel='TapTap（安卓+iOS）',
        contact='TapTap 官方入驻页 / 玩家QQ群 671492232',
        expo='待核实',
        other_product='早期复现过 Character.AI 形态与斯坦福小镇（2D/3D多形态）',
        visit_value='高。算法驱动型团队，6项AI发明专利，有可公开引用的学术产出；同在长三角，拜访成本低',
        conf='A',
        src='TapTap官方详情页/腾讯新闻深度专访/游戏矩阵报道',
    ),
    dict(
        game='福尔摩斯：暗夜追踪者', app_id='', layer='L1',
        company='上海美酷瑞 (MacRoy)', city='上海',
        founder='朱笑靖（前盛大游戏VP）、吴昀贇（前B站游戏事业部负责人）；二人曾共创分众游戏、元境界科技',
        team_size='待核实',
        funding='待核实（2024-07 成立）',
        ai_mech='数十个AI扮演NPC，游戏内无任何剧情选项；AI逻辑判定系统综合对话逻辑/情绪识别/行为分析动态判定任务完成度；自研情绪表演系统（面部100+骨骼、8种基础情绪）；自研实时语音引擎毫秒级响应+唇形同步',
        ai_cost='未公开',
        stage='Steam + TapTap 已开启预约；2025-01 登记软著',
        channel='Steam + TapTap',
        contact='待核实',
        expo='待核实',
        other_product='首款产品，公司主攻AI前沿技术创新游戏',
        visit_value='高。团队履历最重（盛大VP+B站游戏负责人），主导过《FGO》《碧蓝航线》《热血传奇手游版》发行；3D大型AI推理游戏是重资产路线，与《除役者》的UE5 ARPG 定位可对标',
        conf='B',
        src='字符无限科技/头条报道 2025-05',
    ),
    dict(
        game='群星低语 Whispers from the Star', app_id='746715', layer='L1',
        company='Anuttacon（蔡浩宇 AI 创业公司）', city='美国/新加坡（非国内，实地拜访不可行）',
        founder='蔡浩宇（米哈游创始人、原CEO）',
        team_size='待核实',
        funding='待核实',
        ai_mech='实时文字、语音、视频通话驱动剧情；玩家话语决定角色斯特拉命运；开放式对话为核心，无固定选项',
        ai_cost='未公开',
        stage='2025-03-15 海外开启测试招募；TapTap 预约 6.8 万、粉丝 6.8 万、评分 8.0',
        channel='TapTap 预约页（海外为主）',
        contact='待核实',
        expo='待核实',
        other_product='—',
        visit_value='仅作标杆参考，团队在海外，实地拜访不可行；但是多模态实时交互AI游戏的行业风向标',
        conf='A',
        src='TapTap官方详情页实时抓取（2026-08-17）+ 研报',
    ),
    dict(
        game='超自然行动组', app_id='', layer='L2',
        company='巨人网络', city='上海',
        founder='—（上市公司）',
        team_size='—',
        funding='上市公司',
        ai_mech='内置AI驱动「AI假人」，接入通义千问模型；能理解玩家语义、复刻真人音色、模拟玩家语言风格与行动逻辑，做出具策略性和迷惑性的伪装动作；上线首周 AI NPC 与真人对局超 2500 万次',
        ai_cost='未公开',
        stage='已上线运营一年+，DAU破千万、累计注册2亿、流水超50亿；TapTap 评分 7.0',
        channel='全渠道 + TapTap',
        contact='巨人网络公开渠道（上海松江）',
        expo='ChinaJoy 常设展台',
        other_product='前CEO吴萌已离职投入AI游戏创业并获融资',
        visit_value='高。国内唯一已验证「AI NPC带动大DAU商业成功」的案例，AI假人是可规模化的范式；同在上海',
        conf='A',
        src='腾讯新闻《中国游戏进入与AI同游时代》2026-08',
    ),
    dict(
        game='不问凡尘', app_id='', layer='L1',
        company='字节跳动 江南工作室', city='上海 / 杭州（待核实具体办公地）',
        founder='—（大厂内部工作室）',
        team_size='—',
        funding='大厂自有',
        ai_mech='基于 Seedance 模型的 AI 真人 RPG；玩家每个选择以非剧情方式累积，影响数值与世界反馈；内置 AI 驱动 NPC 说服玩法',
        ai_cost='未公开',
        stage='ChinaJoy 2026 展出',
        channel='待核实',
        contact='待核实',
        expo='ChinaJoy 2026',
        other_product='Seedance 视频模型（TapTap 制造亦将接入）',
        visit_value='中高。大厂拜访门槛高，但 Seedance 驱动的真人RPG 是视频模型入游的最前沿样本',
        conf='B',
        src='东吴传媒 ChinaJoy 2026 点评报告',
    ),
    dict(
        game='印格 Engram', app_id='', layer='L1',
        company='上海柚衣科技', city='上海',
        founder='待核实',
        team_size='待核实',
        funding='待核实',
        ai_mech='AI驱动 CRPG；玩家与基于AI的NPC对话，NPC根据玩家行动与语言做出不同反应并影响后续剧情',
        ai_cost='未公开',
        stage='完整度低于《麦琪的花园》，计划 Steam 试玩版',
        channel='Steam（TapTap 待核实）',
        contact='待核实',
        expo='CCG EXPO 2025',
        other_product='—',
        visit_value='中高。同在上海，早期团队易接触，CRPG+AI 是叙事重度方向',
        conf='B',
        src='CCG EXPO 2025 报道（OFweek）',
    ),
    dict(
        game='AIFriends', app_id='771203', layer='L1',
        company='上海惊喜先生科技有限公司', city='上海',
        founder='待核实',
        team_size='待核实',
        funding='待核实',
        ai_mech='AI伙伴养成；UGC版本支持通过SDK上传角色模型、设定人格与故事、选择或克隆音色、亲密度养成、角色广场共享',
        ai_cost='未公开',
        stage='2025-08-30 上线；TapTap 评分 7.4、关注 12.1 万',
        channel='TapTap',
        contact='TapTap 官方入驻页',
        expo='待核实',
        other_product='—',
        visit_value='中。AI陪伴+UGC结合，音色克隆与3D模型上传管线值得看；同在上海',
        conf='A',
        src='TapTap官方详情页实时抓取（2026-08-17）',
    ),
    dict(
        game='EVE', app_id='', layer='L1',
        company='自然选择（深圳）智能有限公司', city='深圳',
        founder='待核实（团队含多位女性成员，本身为目标用户）',
        team_size='待核实',
        funding='待核实',
        ai_mech='AI伴侣；支持3D实时通话并可开启摄像头让AI「看见」现实世界；好感度提升解锁剧情；陪伴/家园/朋友圈/送礼系统',
        ai_cost='未公开',
        stage='2026-04-10 上线，已完成两轮测试；仅面向中国地区',
        channel='iOS + TapTap',
        contact='待核实',
        expo='待核实',
        other_product='—',
        visit_value='中。多模态视觉输入的陪伴产品，摄像头实时理解是差异点',
        conf='B',
        src='媒体报道 sounova',
    ),
    dict(
        game='AI小镇：星原', app_id='', layer='L1',
        company='待核实', city='待核实',
        founder='待核实', team_size='待核实', funding='待核实',
        ai_mech='玩家养成、观察并引导一个自主生活的 Agent；不同玩家的 Agent 会互动并相互影响（斯坦福小镇范式的商业化尝试）',
        ai_cost='未公开', stage='ChinaJoy 2026 展出',
        channel='待核实', contact='待核实', expo='ChinaJoy 2026', other_product='—',
        visit_value='中。多玩家Agent互相影响是罕见设计，但主体信息缺失需先补齐',
        conf='C', src='东吴传媒 ChinaJoy 2026 点评报告',
    ),
    dict(
        game='混想局', app_id='', layer='L1',
        company='待核实', city='待核实',
        founder='待核实', team_size='待核实', funding='待核实',
        ai_mech='玩家自由输入或词条组合，AI 即时生成角色、技能与流派，随机事件中组建战队（AI Roguelike 构筑）',
        ai_cost='未公开', stage='ChinaJoy 2026 展出',
        channel='待核实', contact='待核实', expo='ChinaJoy 2026', other_product='—',
        visit_value='中。AI实时生成技能与流派，与你的RTS+塔防构筑思路有交叉参考价值',
        conf='C', src='东吴传媒 ChinaJoy 2026 点评报告',
    ),
    dict(
        game='黑箱：无限构筑', app_id='', layer='L1',
        company='待核实', city='待核实',
        founder='待核实', team_size='待核实', funding='待核实',
        ai_mech='数百种底层原子项动态重组生成独特技能（AI Roguelike 构筑）',
        ai_cost='未公开', stage='ChinaJoy 2026 展出',
        channel='待核实', contact='待核实', expo='ChinaJoy 2026', other_product='—',
        visit_value='中。原子项重组机制对塔防/RTS技能系统设计有直接借鉴',
        conf='C', src='东吴传媒 ChinaJoy 2026 点评报告',
    ),
    dict(
        game='MoMo', app_id='', layer='L1',
        company='待核实', city='待核实',
        founder='待核实', team_size='待核实', funding='待核实',
        ai_mech='实时同步玩家所在城市天气与活动信息，提供与 AI NPC 玩游戏、办公、看电影等体验；丰富上下文构建陪伴感',
        ai_cost='未公开', stage='ChinaJoy 2026 展出',
        channel='待核实', contact='待核实', expo='ChinaJoy 2026', other_product='—',
        visit_value='中低。现实世界上下文接入是亮点，但属陪伴品类，与你主线关联弱',
        conf='C', src='东吴传媒 ChinaJoy 2026 点评报告',
    ),
    dict(
        game='假如我是人工智能 If I am AI', app_id='156070', layer='L1',
        company='内购人生PABL', city='待核实',
        founder='待核实', team_size='个人/小团队', funding='无',
        ai_mech='AI 主题文字点击类；官方 ai 标签收录（需实测确认是否为运行时接入模型，或仅AI题材）',
        ai_cost='未公开',
        stage='已上线；TapTap 评分 9.5、预约 8827、粉丝 9151',
        channel='TapTap', contact='TapTap 官方页', expo='—', other_product='—',
        visit_value='低。评分高但体量小，且存在「AI题材而非AI技术」的可能，需先实测再决定是否拜访',
        conf='C', src='TapTap官方详情页实时抓取（2026-08-17）',
    ),
    dict(
        game='星眠', app_id='', layer='L1',
        company='待核实', city='待核实',
        founder='待核实', team_size='待核实', funding='待核实',
        ai_mech='AI 陪伴乙女；AI 动态陪伴系统实时生成对话（非固定台词），Live2D 触摸互动 + 模拟经营 + 快穿剧情',
        ai_cost='未公开', stage='2026-07-21 开启预约',
        channel='官网 + TapTap', contact='待核实', expo='待核实', other_product='—',
        visit_value='中低。乙女+AI 细分赛道，Live2D与实时对话结合的工程实现可参考',
        conf='C', src='媒体报道 sounova',
    ),
    dict(
        game='赎命电波', app_id='', layer='L1',
        company='待核实', city='待核实',
        founder='待核实', team_size='待核实', funding='待核实',
        ai_mech='接入AI赋予NPC自由交互，或玩家与AI对话共同续写故事',
        ai_cost='未公开', stage='待核实',
        channel='待核实', contact='待核实', expo='待核实', other_product='—',
        visit_value='中低。信息过少，需先补齐主体', conf='C',
        src='东吴传媒 ChinaJoy 2026 点评报告',
    ),
    dict(
        game='重生之我在产业园当AI', app_id='', layer='L1',
        company='待核实', city='待核实',
        founder='待核实', team_size='待核实', funding='待核实',
        ai_mech='AI对话驱动叙事，玩家在设定世界观下与AI共同续写故事',
        ai_cost='未公开', stage='待核实',
        channel='待核实', contact='待核实', expo='待核实', other_product='—',
        visit_value='中低。信息过少，需先补齐主体', conf='C',
        src='东吴传媒 ChinaJoy 2026 点评报告',
    ),
    dict(
        game='流言侦探', app_id='', layer='L2',
        company='待核实', city='待核实',
        founder='待核实', team_size='待核实', funding='待核实',
        ai_mech='模拟AI社交与真人聊天体验，多线结局；需实测确认是否运行时接入模型',
        ai_cost='未公开',
        stage='已上线，番外《白樱抄》已更新；评分 9.2、编辑推荐',
        channel='TapTap', contact='待核实', expo='待核实', other_product='—',
        visit_value='中低。口碑极好但AI成分待核实，可能是脚本模拟而非真AI', conf='C',
        src='TapTap 首页推荐位',
    ),
]

EXCLUDED = [
    dict(game='异常', app_id='59622', company='Kunpo', score='9.6',
         reason='带 ai 标签但实际是黑客/编程/解谜主题，无运行时AI或AI管线证据 —— 官方标签误伤的典型'),
    dict(game='TapTap 制造全部产出（约 4000+ 款）', app_id='810249', company='心动/TapTap 平台',
         score='—', reason='按需求明确排除。含《AI文字冒险》等由 TapTap 制造创作者发布的作品'),
    dict(game='晚安不忧屋', app_id='', company='恺英网络 SOON 平台', score='—',
         reason='属于其他AI创作平台的产出，非独立团队自研管线，与Maker性质相同'),
]

FIELDS = [
    ('game', '游戏名'), ('layer', 'AI介入层级'), ('conf', '置信度'),
    ('company', '公司主体'), ('city', '所在城市'), ('founder', '核心团队背景'),
    ('team_size', '团队规模'), ('funding', '融资情况'),
    ('ai_mech', 'AI机制描述'), ('ai_cost', 'AI成本披露'),
    ('stage', '当前阶段与数据'), ('channel', '发行渠道'),
    ('contact', '联系方式'), ('expo', '展会出没记录'),
    ('other_product', '其他产品/工具链'), ('visit_value', '拜访价值判断'),
    ('app_id', 'TapTap AppID'), ('src', '证据来源'),
]

if __name__ == '__main__':
    with open('taptap_ai_games_visit_list.csv', 'w', encoding='utf-8-sig', newline='') as fp:
        w = csv.writer(fp)
        w.writerow([label for _, label in FIELDS] + ['TapTap链接', '拜访状态', '接触人', '拜访日期', '跟进备注'])
        order = {'L1': 0, 'L2': 1, 'L3': 2}
        conf_order = {'A': 0, 'B': 1, 'C': 2}
        for r in sorted(ROWS, key=lambda x: (conf_order.get(x['conf'], 9), order.get(x['layer'], 9))):
            link = f"https://www.taptap.cn/app/{r['app_id']}" if r['app_id'] else ''
            w.writerow([r.get(k, '') for k, _ in FIELDS] + [link, '未接触', '', '', ''])
        w.writerow([])
        w.writerow(['—— 以下为明确排除项 ——'])
        w.writerow(['游戏名', 'TapTap AppID', '公司', '评分', '排除理由'])
        for e in EXCLUDED:
            w.writerow([e['game'], e['app_id'], e['company'], e['score'], e['reason']])
    print('CSV written:', len(ROWS), 'rows +', len(EXCLUDED), 'excluded')
