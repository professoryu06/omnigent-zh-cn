import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Dialog, DialogContent, DialogFooter, DialogTitle } from "./dialog";
import { setLocale } from "@/i18n";

// The iOS shell keeps the WKWebView layout viewport full-height when the soft
// keyboard opens, so a modal capped at `85vh` and centered on `50%` would sit
// partly behind the keyboard. DialogContent pins its height cap and centering
// origin to the keyboard-aware `--omnigent-viewport-height` — but only inside
// the iOS shell. These tests pin that gating.

function setIOS(on: boolean): void {
  if (on) {
    (window as unknown as Record<string, unknown>).omnigentNative = { kind: "ios" };
  } else {
    delete (window as unknown as Record<string, unknown>).omnigentNative;
  }
}

afterEach(() => {
  cleanup();
  setIOS(false);
});

function renderDialog() {
  return render(
    <Dialog open onOpenChange={() => {}}>
      <DialogContent>
        <DialogTitle>Test</DialogTitle>
      </DialogContent>
    </Dialog>,
  );
}

describe("DialogContent keyboard-aware sizing", () => {
  it("caps height and centering to the visible viewport inside the iOS shell", () => {
    setIOS(true);
    renderDialog();
    const content = screen.getByRole("dialog");
    // Inline style (not a class) so it wins over any caller's max-h-[85vh].
    expect(content.style.maxHeight).toContain("--omnigent-viewport-height");
    expect(content.style.top).toContain("--omnigent-viewport-height");
  });

  it("applies no viewport inline style off the iOS shell", () => {
    setIOS(false);
    renderDialog();
    const content = screen.getByRole("dialog");
    expect(content.style.maxHeight).toBe("");
    expect(content.style.top).toBe("");
  });
});

// P4D — zh-CN real-UI assertions for dialog accessibility
describe("Dialog zh-CN", () => {
  afterEach(() => setLocale("en"));

  it("uses Chinese sr-only close label in DialogContent", () => {
    setLocale("zh-CN");
    render(
      <Dialog open onOpenChange={() => {}}>
        <DialogContent>
          <DialogTitle>测试</DialogTitle>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.getByText("关闭")).toBeInTheDocument();
  });

  it("renders the Chinese Close text as the aria-label for the X button", () => {
    setLocale("zh-CN");
    render(
      <Dialog open onOpenChange={() => {}}>
        <DialogContent showCloseButton={true}>
          <DialogTitle>测试</DialogTitle>
        </DialogContent>
      </Dialog>,
    );
    // The sr-only span inside the close button renders "关闭"
    const closeBtn = screen.getByText("关闭");
    expect(closeBtn).toBeInTheDocument();
    expect(closeBtn.tagName).toBe("SPAN");
    expect(closeBtn.className).toBe("sr-only");
  });

  it("renders English Close sr-only text when locale is English", () => {
    setLocale("en");
    render(
      <Dialog open onOpenChange={() => {}}>
        <DialogContent>
          <DialogTitle>Test</DialogTitle>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.getByText("Close")).toBeInTheDocument();
  });
});

// P4D-R — DialogFooter showCloseButton Chinese
describe("DialogFooter zh-CN", () => {
  afterEach(() => setLocale("en"));

  it("renders Chinese Close button in DialogFooter and clicking it closes the Dialog", () => {
    setLocale("zh-CN");
    const onOpenChange = vi.fn();
    render(
      <Dialog open onOpenChange={onOpenChange}>
        <DialogContent>
          <DialogTitle>测试</DialogTitle>
          <div>Body content</div>
          <DialogFooter showCloseButton>
            <button>Save</button>
          </DialogFooter>
        </DialogContent>
      </Dialog>,
    );
    const closeBtn = screen.getAllByRole("button", { name: "关闭" })[1]; // the footer one (index 1, after the X button)
    expect(closeBtn).toBeInTheDocument();
    fireEvent.click(closeBtn);
    // Dialog should close — Radix calls onOpenChange(false)
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
