# TapTap AI 游戏拜访追踪清单

TapTap 平台上 **AI 原生 / 内容管线深度依赖 AI** 的游戏与团队清单，用于商务追踪与实地拜访。
已明确排除 TapTap Maker（TapTap 制造）产出的约 4000+ 款作品。

数据核准时间：2026-08-17

## 文件说明

| 文件 | 说明 |
|---|---|
| `taptap_ai_games_dashboard.html` | 单文件看板，支持按置信度 / AI 层级 / 可拜访性筛选，双击即可在浏览器打开 |
| `taptap_ai_games_visit_list.csv` | 清单主表，23 列。末 4 列为空白跟进列（拜访状态 / 接触人 / 拜访日期 / 跟进备注） |
| `taptap_probe.py` | TapTap Nuxt payload 解析器（`nuxt_payload` + `deref`） |
| `fetch_live.py` | 按 app id 抓取详情页，核准评分 / 厂商 / 标签 / 预约数 |
| `seeds.py` | 人工核实的候选种子名单及证据来源 |
| `build_list.py` | 主数据 + CSV 生成 |
| `build_dashboard.py` | HTML 看板生成 |
| `taptap_live.json` | 最近一次实时抓取的原始结果 |

## 重新生成

```bash
python fetch_live.py      # 刷新 TapTap 实时数据
python build_list.py      # 生成 CSV
python build_dashboard.py # 生成 HTML 看板
```

纯标准库，无需安装依赖。

## 判定标准

AI 介入程度分四层，本清单收录 L1 与 L2，L3 仅收录已公开披露的案例：

| 层级 | 定义 | 可检测性 |
|---|---|---|
| **L1** 运行时 AI 原生 | AI 即玩法本体，关掉模型游戏就不成立 | 高 |
| **L2** 运行时 AI 增强 | AI 作为局部功能，移除后主体玩法仍完整 | 中高 |
| **L3** 生产管线 AI 重度 | 美术、配音、文案主体由 AI 生成后人工修 | 低 |
| **L4** 生产管线 AI 点缀 | 仅局部使用，如占位图、翻译、代码补全 | 几乎为零 |

置信度：`A` 公司主体与 AI 机制均有公开可查证据 · `B` 权威媒体或研报单一来源 · `C` 仅单一提及，主体待补齐

## 方法论要点

1. **TapTap 官方 AI 标签不可用**：`/tag/AI` 下仅 3 款游戏，而 2026H1 平台新发行 5002 款中 4000+ 款为 AI 制作，标签覆盖率不足 1%。
2. **召回靠多源交叉**：券商研报（华泰 / 东吴传媒 AI 游戏专题）、ChinaJoy 2026 与 CCG EXPO 展会名录、深度报道，再用 TapTap 页面实时抓取核准动态字段。
3. **标签会误伤**：《异常》（app 59622，Kunpo，评分 9.6）带 `ai` 标签但实为黑客 / 编程 / 解谜主题，无 AI 证据，已列入排除项。
4. **L3 不做全量推断**：开发者普遍不主动披露美术与配音的 AI 使用比例，强行推断会把猜测写成结论。

## 抓取技术说明

TapTap 网页为 Nuxt SSR，HTML 中内嵌完整的 flat payload：

- 定位 `[["Reactive"` 后做括号配平即可 `json.loads`
- payload 中的整数是索引引用，需递归解引用（见 `taptap_probe.py` 的 `deref`）
- 可取字段：`id` / `title` / `stat.rating.score` / `developers[].name` / `tags[].value` / `stat.reserve_count` / `stat.fans_count` / `description`

已知限制：

- 标签页每页固定 10 条且无法翻页（`?page=2` 无效，`?sort=new` 返回 400）
- 搜索页为纯客户端渲染，SSR 无结果；`/webapiv2/search/*` 各路径均 404
- Bing `site:taptap.cn` 只返回站点首页，拿不到 app 深链
