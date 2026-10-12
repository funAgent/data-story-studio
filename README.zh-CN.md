# Data Story Studio

[English](README.md) · [安装](INSTALL.zh-CN.md) · [命令行快速开始](docs/QUICKSTART.md)

把本地 CSV/JSON 做成可交互仪表盘，再将选定图表生成可编辑动画工程和真实 MP4。自然语言规划由 Codex 完成；本地脚本负责受约束的数据处理与确定性渲染。

从 [INSTALL.md](INSTALL.md) 开始。插件在 `plugins/data-story-studio/`，marketplace 清单在 `.agents/plugins/marketplace.json`。请完整解压隐藏目录。

## 能做什么

- CSV/JSON 真实文件导入，多维度/指标和 bar、line、table 仪表盘
- 保存可编辑规格、可交互 HTML、快照和数据溯源
- 显式重新读取源文件并刷新；页面交互不等于数据同步
- 选定 snapshot 图表转换为动画 bar 场景，PNG 预览、FFmpeg MP4 导出
- 保留 JSON 工程，修改后重新渲染
- 插件 setup / create-dashboard / create-motion / data-to-motion 四个 skills

## 能力边界

这是可安装的本地初版，不是 Claude 私有实现，也不是完整 BI 平台或通用视频生成器。没有连接器、任意 SQL、定时同步、云端发布、语音、任意素材视频或额外模型调用。Motion 支持的场景以 runtime schema/README 为准；dashboard 的 line/table 转视频时是 bar 表达，不能称为原图动画复刻。超过当前数量/数值限制的输入会被拒绝，不能静默删数据。

原始数据留在本地处理，但你在 Codex 中提供的数据仍受其当前环境与产品数据政策约束。HTML 和 snapshot 内含源记录；分享前应检查隐私，溯源中也可能有本地路径。

## 验证

查看 `docs/QA.md`（交付前生成）和 `tests/`。测试包括完整解压、真实数据→dashboard→snapshot→MP4，以及输入和路径安全。安装验证使用临时 HOME/CODEX_HOME，不接触用户账户配置。

## 如何复现打包

`python3 tests/build_bundle.py --output /absolute/path/to/new-package.zip`

归档只含源文件，包含隐藏的 marketplace/兼容清单，排除缓存、依赖目录和渲染产物。不会安装插件或修改配置。测试会使用本机已有依赖；没有自动安装步骤。

## 开源发布准备

已加入贡献指南、安全报告说明、CI、可复现 ZIP 打包及 npm 锁文件。原始项目代码采用 [MIT 许可](LICENSE)，第三方依赖保留各自许可，详见 [第三方说明](THIRD_PARTY.md)。GitHub 发布、插件目录发布、安装到个人客户端是三个独立步骤。
