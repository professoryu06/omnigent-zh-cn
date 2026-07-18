import { render, screen } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  __pinDefaultLocale,
  DEFAULT_LOCALE,
  getLocale,
  setLocale,
  translate,
  TRANSLATION_STORAGE_KEY,
  useTranslation,
} from "./index";

beforeEach(() => {
  __pinDefaultLocale(null);
});

afterEach(() => {
  __pinDefaultLocale(null);
  localStorage.clear();
  document.documentElement.lang = "";
});

describe("locale preferences", () => {
  it("uses Simplified Chinese when no preference is stored", () => {
    expect(DEFAULT_LOCALE).toBe("zh-CN");
    expect(getLocale()).toBe("zh-CN");
  });

  it("persists a valid locale and updates the document language", () => {
    setLocale("en");

    expect(getLocale()).toBe("en");
    expect(localStorage.getItem(TRANSLATION_STORAGE_KEY)).toBe("en");
    expect(document.documentElement.lang).toBe("en");
  });

  it("falls back to Simplified Chinese for an invalid stored locale", () => {
    localStorage.setItem(TRANSLATION_STORAGE_KEY, "fr");

    expect(getLocale()).toBe("zh-CN");
  });

  it("allows the test environment to pin a locale without changing the production default", () => {
    __pinDefaultLocale("en");

    expect(getLocale()).toBe("en");

    __pinDefaultLocale(null);
    expect(getLocale()).toBe("zh-CN");
  });
});

describe("translate", () => {
  it("uses Chinese as the default locale", () => {
    expect(translate("common.startSession")).toBe("开始会话");
  });

  it("uses the selected locale", () => {
    expect(translate("common.startSession", {}, "en")).toBe("Start session");
  });

  it("interpolates named values", () => {
    expect(translate("session.connectedAs", { name: "DESKTOP" })).toBe(
      "已连接到 DESKTOP",
    );
  });

  it("provides Chinese copy for the chat empty, loading, and recovery states", () => {
    expect(translate("chat.emptyStateHeading", {}, "zh-CN")).toBe("想做什么？");
    expect(translate("chat.loadingConversation", {}, "zh-CN")).toBe("正在加载会话…");
    expect(translate("chat.conversationNotFound", {}, "zh-CN")).toBe("未找到会话");
    expect(
      translate("chat.sessionLoadFailed", { conversationId: "conv_123", reason: "请求失败" }, "zh-CN"),
    ).toBe("无法加载会话 conv_123：请求失败");
    expect(translate("chat.startNewChat", {}, "zh-CN")).toBe("新建会话");
    expect(translate("chat.replyShortcut", {}, "zh-CN")).toBe("回复 ↵");
  });

  it("falls back to English when a Chinese key is absent", () => {
    expect(translate("shared.englishFallback")).toBe("English fallback");
  });

  it("returns the key when no locale contains it", () => {
    expect(translate("missing.key")).toBe("missing.key");
  });
});

describe("useTranslation", () => {
  it("uses the default translation context when a legacy component has no provider", () => {
    function LegacyComponent() {
      const { t } = useTranslation();
      return createElement("span", null, t("common.startSession"));
    }

    render(createElement(LegacyComponent));

    expect(screen.getByText("开始会话")).toBeInTheDocument();
  });
});
