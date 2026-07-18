import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { setLocale } from "@/i18n";
import { SystemMessageView } from "./SystemMessage";

afterEach(cleanup);

describe("SystemMessageView", () => {
  it("hides sub-agent wake notices instead of rendering a centered System row", () => {
    const { container } = render(
      <SystemMessageView
        message={{
          kind: "subagent_wake",
          label: "Sub-agent result ready",
          body: "",
        }}
      />,
    );

    expect(screen.queryByTestId("system-message")).toBeNull();
    expect(container.textContent).toBe("");
  });

  it("renders generic system message with the System: label", () => {
    render(
      <SystemMessageView
        message={{
          kind: "generic",
          label: "Something happened",
          body: "",
        }}
      />,
    );
    expect(screen.getByTestId("system-message")).toBeInTheDocument();
    expect(screen.getByText(/System:/)).toBeInTheDocument();
  });
});

describe("zh-CN", () => {
  afterEach(() => {
    setLocale("en");
  });

  it("shows the '系统：' label when locale is zh-CN", () => {
    setLocale("zh-CN");
    render(
      <SystemMessageView
        message={{
          kind: "generic",
          label: "某个事件",
          body: "",
        }}
      />,
    );
    expect(screen.getByText("系统：")).toBeInTheDocument();
    expect(screen.getByText("某个事件")).toBeInTheDocument();
  });
});
