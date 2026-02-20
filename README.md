<div align="center">
  <img src="assets/logo.svg" alt="GMGN CA Query GUI" width="680"/>

  # GMGN CA Query GUI

  **Solana Token CA 信息查询桌面工具**

  [![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-blue?style=flat-square)](https://github.com/TomSchimansky/CustomTkinter)
  [![Status](https://img.shields.io/badge/Status-Deprecated-red?style=flat-square)]()
</div>

---

> **注意**: GMGN 接口已启用反爬机制，本工具当前不可用。仅作为代码参考保留。

## 概述

基于 CustomTkinter 的 Solana Token 信息查询桌面应用。通过 GMGN API 查询代币合约地址（CA）的详细信息，包括市值、成交额、持仓分布、安全评估等，并通过 WebSocket 实时更新交易数据和 K 线图。

## 功能特性

- **CA 查询** -- 输入合约地址查询代币详细信息
- **安全评估** -- 自动分析黑名单、烧池子、老鼠仓、mint 权限等风险指标
- **实时交易流** -- WebSocket 订阅实时买卖交易，标注交易者类型（聪明钱/狙击手/创建者等）
- **K 线图** -- 内嵌浏览器显示实时 K 线图表
- **跑路概率** -- 综合多维度指标评估项目风险

## 技术栈

| 组件 | 技术 |
|:---|:---|
| GUI 框架 | CustomTkinter |
| K 线渲染 | wxPython WebView |
| 实时数据 | WebSocket |
| 数据源 | GMGN API |

## 免责声明

本工具仅供学习研究使用，不构成任何投资建议。加密货币交易存在极高风险。