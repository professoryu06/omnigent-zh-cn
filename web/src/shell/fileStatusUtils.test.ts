import { beforeEach, describe, expect, it } from "vitest";
import { setLocale } from "@/i18n";
import { gitStatusLabel } from "./fileStatusUtils";

beforeEach(() => {
  setLocale("en");
});

describe("gitStatusLabel", () => {
  it("returns English 'Added' for created status", () => {
    expect(gitStatusLabel("created")).toBe("Added");
  });

  it("returns English 'Deleted' for deleted status", () => {
    expect(gitStatusLabel("deleted")).toBe("Deleted");
  });

  it("returns English 'Modified' for modified status", () => {
    expect(gitStatusLabel("modified")).toBe("Modified");
  });

  it("returns Chinese '已添加' for created status when locale is zh-CN", () => {
    setLocale("zh-CN");
    expect(gitStatusLabel("created")).toBe("已添加");
    setLocale("en");
  });

  it("returns Chinese '已删除' for deleted status when locale is zh-CN", () => {
    setLocale("zh-CN");
    expect(gitStatusLabel("deleted")).toBe("已删除");
    setLocale("en");
  });

  it("returns Chinese '已修改' for modified status when locale is zh-CN", () => {
    setLocale("zh-CN");
    expect(gitStatusLabel("modified")).toBe("已修改");
    setLocale("en");
  });
});
