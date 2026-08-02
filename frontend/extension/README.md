# Socialization 网页收藏扩展

Chrome/Edge MV3 扩展：点击图标即可把当前页面的标题与正文收藏到本地 Socialization 应用（存为文档并进入知识库检索）。

## 安装

1. 打开 Chrome/Edge 的 `扩展程序` 页面，开启“开发者模式”。
2. 点击“加载已解压的扩展程序”，选择本目录（`frontend/extension`）。
3. 确保本地应用已启动（`.\scripts\dev.ps1`，后端 `127.0.0.1:8000`）。

## CORS 说明

后端默认 CORS 白名单只含 `http://127.0.0.1:3000`。扩展的请求来源是 `chrome-extension://<扩展ID>`，需要把该来源加入 `.env` 的 `CORS_ORIGINS`（可在扩展管理页查看 ID），然后重启后端；或临时使用 `chrome://flags`/本地调试方案。

## 说明

- 本目录为 P3 的独立模块，不参与前端构建；图标 `icons/icon.png` 未内置，可用任意 PNG（或去掉 `iconUrl` 字段）。
- 权限：`activeTab` + `scripting`（读取当前页正文），`host_permissions` 限定本地 API。
