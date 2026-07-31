# i18n 基础层

此目录提供 Omnigent Web UI 的轻量本地化能力，不依赖 i18next 等额外运行时。

## 使用方式

```tsx
const { t } = useTranslation();

return <button>{t("common.startSession")}</button>;
```

动态文案使用具名变量：

```tsx
t("session.connectedAs", { host: "DESKTOP" });
```

## 规则

- 默认语言为 `zh-CN`，缺失键回退到英语，再回退为键名。
- 面向用户的界面文字可翻译；模型名、CLI 命令、文件路径、代码、日志和 API 字段不翻译。
- 新增文案必须同时写入 `locales/zh-CN.ts` 与 `locales/en.ts`。
- 不要在组件中直接读取或写入 `localStorage`；使用 `setLocale()` 或 `useTranslation()` 暴露的 `setLocale()`。
