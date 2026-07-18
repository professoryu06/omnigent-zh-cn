import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { setLocale } from "@/i18n";
import { ExitPlanModeReview } from "./ExitPlanModeReview";

afterEach(() => {
  cleanup();
});

describe("ExitPlanModeReview — zh-CN", () => {
  afterEach(() => {
    setLocale("en");
  });

  it("renders all three plan-review action buttons in Chinese", () => {
    setLocale("zh-CN");
    render(
      <ExitPlanModeReview
        plan="# Test Plan"
        onAcceptAuto={vi.fn()}
        onAccept={vi.fn()}
        onReject={vi.fn()}
      />,
    );

    expect(
      screen.getByRole("button", { name: "是的，并使用自动模式" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "是的，手动批准编辑" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "拒绝并反馈" }),
    ).toBeInTheDocument();
  });

  it("shows reject form buttons in Chinese after clicking 'reject with feedback'", () => {
    setLocale("zh-CN");
    render(
      <ExitPlanModeReview
        plan="# Test Plan"
        onAcceptAuto={vi.fn()}
        onAccept={vi.fn()}
        onReject={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "拒绝并反馈" }));

    expect(
      screen.getByRole("button", { name: "拒绝计划" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "取消" }),
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("对计划有什么修改意见？（可选）"),
    ).toBeInTheDocument();
  });
});
