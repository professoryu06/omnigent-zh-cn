import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { setLocale } from "@/i18n";
import { TruncatedBanner } from "./TruncatedBanner";

afterEach(() => {
  cleanup();
  setLocale("en");
});

describe("TruncatedBanner", () => {
  it("renders the truncated-file warning in English", () => {
    render(<TruncatedBanner />);
    expect(
      screen.getByText(
        "This file is too large to load fully — showing a truncated preview. Editing is disabled to avoid overwriting the rest of the file; download it to view or edit the full content.",
      ),
    ).toBeInTheDocument();
  });

  it("renders the truncated-file warning in Chinese when locale is zh-CN", () => {
    setLocale("zh-CN");
    render(<TruncatedBanner />);
    expect(
      screen.getByText(
        "此文件过大无法完整加载——仅显示截断预览。编辑功能已禁用，以免覆盖文件其余部分；请下载文件以查看或编辑完整内容。",
      ),
    ).toBeInTheDocument();
    setLocale("en");
  });

  it("renders the warning icon", () => {
    render(<TruncatedBanner />);
    const icon = document.querySelector("svg");
    expect(icon).toBeTruthy();
  });
});
