import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { setLocale } from "@/i18n";
import { FileMentionMenu } from "./FileMentionMenu";

afterEach(() => {
  cleanup();
  setLocale("en");
});

describe("FileMentionMenu zh-CN", () => {
  it("shows the localized loading state and keyboard hint", () => {
    setLocale("zh-CN");
    render(
      <FileMentionMenu
        currentDir=""
        activeIndex={-1}
        entries={[]}
        loading
        onOpenDir={vi.fn()}
        onAttach={vi.fn()}
      />,
    );

    expect(screen.getByText("工作区")).toBeInTheDocument();
    expect(screen.getByText("加载中…")).toBeInTheDocument();
    expect(screen.getByText("↵ 打开 · ⇥ 附加")).toBeInTheDocument();
  });

  it("localizes file and folder actions while preserving entry names", () => {
    setLocale("zh-CN");
    const onOpenDir = vi.fn();
    const onAttach = vi.fn();
    render(
      <FileMentionMenu
        currentDir=""
        activeIndex={-1}
        entries={[
          { path: "src", name: "src", type: "directory", bytes: 0, modified_at: null },
          { path: "README.md", name: "README.md", type: "file", bytes: 128, modified_at: null },
        ]}
        onOpenDir={onOpenDir}
        onAttach={onAttach}
      />,
    );

    fireEvent.click(screen.getByTitle("打开 src"));
    expect(onOpenDir).toHaveBeenCalledWith("src");

    fireEvent.click(screen.getByTitle("附加 README.md"));
    expect(onAttach).toHaveBeenCalledWith("README.md", false);

    fireEvent.click(screen.getByRole("button", { name: "附加整个文件夹 src" }));
    expect(onAttach).toHaveBeenCalledWith("src", true);
  });
});
