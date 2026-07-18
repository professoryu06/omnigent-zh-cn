import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { TooltipProvider } from "@/components/ui/tooltip";
import { SessionStateBadge } from "./SessionStateBadge";
import type { SessionState } from "@/hooks/useSessionState";
import { I18nProvider, setLocale, useTranslation } from "@/i18n";

function renderBadge(state: SessionState) {
  return render(
    <TooltipProvider>
      <SessionStateBadge state={state} />
    </TooltipProvider>,
  );
}

afterEach(cleanup);

describe("SessionStateBadge — per-state rendering", () => {
  it("renders awaiting as a 'Needs response' tag with a count-aware accessible label", () => {
    renderBadge({ kind: "awaiting", count: 3 });
    const badge = screen.getByTestId("session-state-badge");
    expect(badge).toHaveAttribute("data-state", "awaiting");
    expect(badge).toHaveAttribute("aria-label", "3 approval prompts waiting");
    // The approval indicator is a visible text tag (not an icon-only dot), so
    // it reads as "Needs response" at a glance in the row.
    expect(badge).toHaveTextContent("Needs response");
  });

  it("uses singular wording when only one prompt is pending", () => {
    renderBadge({ kind: "awaiting", count: 1 });
    expect(screen.getByTestId("session-state-badge")).toHaveAttribute(
      "aria-label",
      "1 approval prompt waiting",
    );
  });

  it("renders running with a spinning grey spinner", () => {
    const { container } = renderBadge({ kind: "running" });
    const badge = screen.getByTestId("session-state-badge");
    expect(badge).toHaveAttribute("data-state", "running");
    // The running indicator is a grey spinner; a missing spinner
    // (or the old success-tone dot grid) means it regressed.
    const spinner = container.querySelector('[data-testid="running-dot"]');
    expect(spinner).not.toBeNull();
    expect(spinner?.getAttribute("class")).toContain("animate-spin");
    expect(spinner?.getAttribute("class")).toContain("text-muted-foreground");
    expect(container.querySelector(".bg-success")).toBeNull();
  });

  it("renders unseen messages as a solid (non-pulsing) brand-pink dot", () => {
    const { container } = renderBadge({ kind: "unseen" });
    const badge = screen.getByTestId("session-state-badge");
    expect(badge).toHaveAttribute("aria-label", "New messages");
    expect(badge).toHaveAttribute("data-state", "unseen");
    // Unread reuses the brand-pink token but stays static; the pulsing
    // variant (running-pulse-dot) is reserved for the running state.
    const dot = container.querySelector(".bg-brand-accent");
    expect(dot).not.toBeNull();
    expect(dot?.getAttribute("class")).not.toContain("running-pulse-dot");
    expect(container.querySelector(".bg-info")).toBeNull();
  });
});
describe("SessionStateBadge zh-CN", () => {
  afterEach(() => setLocale("en"));

  it("renders Chinese labels when locale is zh-CN", () => {
    setLocale("zh-CN");
    renderBadge({ kind: "awaiting", count: 3 });
    expect(screen.getByText("需要响应")).toBeInTheDocument();
    expect(screen.getByLabelText("3 条审批待处理")).toBeInTheDocument();
  });

  it("renders running label in Chinese", () => {
    setLocale("zh-CN");
    renderBadge({ kind: "running" });
    expect(screen.getByLabelText("会话运行中")).toBeInTheDocument();
  });

  it("renders unseen label in Chinese", () => {
    setLocale("zh-CN");
    renderBadge({ kind: "unseen" });
    expect(screen.getByLabelText("新消息")).toBeInTheDocument();
  });

  it("switches from English to Chinese at runtime without remounting", () => {
    function LocaleSwitch() {
      const { setLocale } = useTranslation();
      return <button onClick={() => setLocale("zh-CN")}>Switch</button>;
    }
    render(
      <I18nProvider>
        <TooltipProvider>
          <LocaleSwitch />
          <SessionStateBadge state={{ kind: "running" }} />
        </TooltipProvider>
      </I18nProvider>,
    );
    const el = screen.getByRole("img", { name: "Session running" });
    expect(el).toBeInTheDocument();
    fireEvent.click(screen.getByText("Switch"));
    const el2 = screen.getByRole("img", { name: /运行/ });
    expect(el2).toBeInTheDocument();
  });
});
