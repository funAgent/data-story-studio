# 安装到 Codex / Install in Codex

这是一个真实的本地 marketplace 插件包，不是仅将脚本称为插件。解压后请保留隐藏目录 `.agents` 和 `.codex-plugin`。无需发布 GitHub、配置 MCP 或提供额外模型 API key。

## 1. 检查客户端

在你自己的终端执行：

```sh
codex --version
codex plugin --help
```

本文命令已在隔离的 Codex CLI 0.159.2 环境验证。不同版本/客户端是否支持本地 marketplace 可能不同；如果没有 `plugin` 子命令，先依据官方客户端更新说明处理，不要自行猜测安装 flag 或手改配置。此交付没有安装到你的真实 Codex，也没有修改你的配置。

## 2. 注册和安装本地包

把解压后的目录放到一个长期保留的位置。将下列路径替换为实际绝对路径：

```sh
codex plugin marketplace add /absolute/path/to/data-story-studio
codex plugin add data-story-studio@data-story-local
```

这两个命令由你在自己的机器上运行，会注册本地 marketplace 并安装插件。目录包含 `.agents/plugins/marketplace.json`，其中 source.path 相对于整个包的根目录。

安装后开一个新对话，用 `/skills` 选择 Data Story Studio 的 skill。已验证的 CLI 命名方式是 `$data-story-studio:create-dashboard`、`$data-story-studio:create-motion`、`$data-story-studio:data-to-motion`、`$data-story-studio:setup`。优先使用客户端列出的名称；版本不同可用 skill 选择器。

自然语言示例：

- “用 Data Story Studio，把我的 /path/sales.csv 做成按月份和地区分析销售额、利润的仪表盘，项目放在 /path/work/sales-story。”
- “将这个 dashboard 的地区销售额图做成 8 秒视频，先给我看预览，保留可编辑工程。”
- “数据文件更新了，重新读取源文件并刷新 dashboard，再生成一个新的视频版本。”

在支持本地 marketplace 的桌面界面，也可重启客户端、打开插件目录、选择该 marketplace 后安装。界面名称可能随版本变化。

## 3. 首次运行

让 Codex 运行 setup skill。选择一个新的工作目录；运行时将复制到工作目录的 `.data-story-runtime`。所有数据工程、编辑和依赖安装均发生在你的工作目录，绝不写入插件缓存。

- Dashboard: Python 3.10+，仅标准库。
- Motion: Node.js 18+、FFmpeg/ffprobe、`@napi-rs/canvas` 固定版本。请先检查 doctor 输出，确认后再安装缺失依赖。
- 字体：中文及其他语言需系统安装相应字体。缺字体会影响文字显示；检查 PNG 预览。
- 这只是本地 CSV/JSON 工作流，不包含 SaaS 登录、数据仓库、后台自动同步或公共网站发布。

## 卸载

```sh
codex plugin remove data-story-studio@data-story-local
codex plugin marketplace remove data-story-local
```

第二步仅在你不再需要这个 marketplace 时执行。卸载插件不会自动删除你创建的工程、依赖或导出文件。请自行保留/删除工作目录；不要为了卸载而删除其他 Codex 配置。

## 官方依据

- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Plugins](https://learn.chatgpt.com/docs/plugins)
- [Build skills](https://learn.chatgpt.com/docs/build-skills)

验证边界：包结构、隔离 CLI 注册/安装/发现/卸载和本地流水线可测试；用户真实客户端安装、GUI 自动选 skill、用户业务数据正确性仍需在用户环境验收。

Motion 依赖已提供 package-lock.json；在复制到工作目录的 motion 文件夹内执行 `npm ci --omit=dev --ignore-scripts`。公开发布及个人客户端安装状态须单独验证。
