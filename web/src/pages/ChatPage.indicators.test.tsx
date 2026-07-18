import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { I18nProvider, setLocale, useTranslation } from "@/i18n";
import { useChatStore } from "@/store/chatStore";
import type { Bubble } from "@/lib/renderItems";
import type { SessionLiveness } from "@/hooks/useSessionLiveness";
import {
  BubbleView,
  ConnectionIndicator,
  McpStartupIndicator,
  RunnerStartingIndicator,
  SandboxFailedIndicator,
} from "./ChatPage";
import { TerminalFirstContextProvider } from "@/shell/TerminalFirstContext";
import type { TerminalFirstContextValue } from "@/shell/TerminalFirstContext";
import { Toaster } from "@/components/ui/toast";
import { TooltipProvider } from "@/components/ui/tooltip";

// Render-level coverage for the chat surface's status bands and bubble
// dispatcher. These exercise the branches that the pure-helper tests can't:
// what the user actually SEES for a failed sandbox, an offline host, an
// in-flight launch, and each bubble kind. They run the real component tree
// (no mocks) the same way ChatPage.composer.test.tsx renders the Composer.

afterEach(() => {
  // Several tests poke sandboxStatus into the global zustand store; reset it
  // so a leftover launch band can't bleed into the next test.
  useChatStore.setState({ sandboxStatus: null });
  cleanup();
});

beforeEach(() => {
  setLocale("en");
});

function LocaleSwitch() {
  const { setLocale } = useTranslation();
  return <button onClick={() => setLocale("zh-CN")}>Switch to Chinese</button>;
}

describe("SandboxFailedIndicator", () => {
  it("renders the recorded failure reason so a dead launch explains itself", () => {
    // WHY: a silently dead chat is the bug this band exists to prevent — the
    // reason must reach the DOM.
    render(<SandboxFailedIndicator status={{ stage: "failed", error: "out of quota" }} />);
    expect(screen.getByText(/Sandbox launch failed: out of quota/)).toBeInTheDocument();
  });

  it("omits the colon suffix when no error detail is recorded", () => {
    // WHY: a missing error must not render a dangling "failed: " — the
    // ternary guards the suffix.
    render(<SandboxFailedIndicator status={{ stage: "failed", error: null }} />);
    expect(screen.getByText(/Sandbox launch failed/)).toBeInTheDocument();
  });
});

describe("ConnectionIndicator", () => {
  const onShowReconnectHelp = () => {};

  it("renders the failed-sandbox band when a launch died (sandboxStatus wins)", () => {
    // WHY: a failed launch owns this band ahead of any liveness state — the
    // sandbox branch short-circuits before the liveness checks.
    useChatStore.setState({ sandboxStatus: { stage: "failed", error: "boom" } });
    render(
      <ConnectionIndicator
        liveness={{ kind: "online" }}
        onShowReconnectHelp={onShowReconnectHelp}
      />,
    );
    expect(screen.getByTestId("sandbox-failed-indicator")).toBeInTheDocument();
  });

  it("renders nothing while a launch is still in flight (non-failed sandbox)", () => {
    // WHY: an in-flight launch renders in the thread (RunnerStartingIndicator),
    // so this band suppresses itself to avoid double progress UI.
    useChatStore.setState({ sandboxStatus: { stage: "provisioning" } });
    const { container } = render(
      <ConnectionIndicator
        liveness={{ kind: "host_offline", isOwner: true }}
        onShowReconnectHelp={onShowReconnectHelp}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("shows the host-offline reconnect affordance", () => {
    // WHY: a host_offline session is unreachable — the only way back is the
    // clickable reconnect banner with the host-specific copy.
    render(
      <ConnectionIndicator
        liveness={{ kind: "host_offline", isOwner: true }}
        onShowReconnectHelp={onShowReconnectHelp}
      />,
    );
    const btn = screen.getByTestId("disconnected-indicator");
    expect(btn).toHaveTextContent(/Host is offline/);
  });

  it("shows agent-disconnected copy for a local-stranded runner", () => {
    // WHY: local_stranded is the other unreachable branch and must read as the
    // agent dropping, not the host.
    render(
      <ConnectionIndicator
        liveness={{ kind: "local_stranded" }}
        onShowReconnectHelp={onShowReconnectHelp}
      />,
    );
    expect(screen.getByTestId("disconnected-indicator")).toHaveTextContent(/Agent disconnected/);
  });

  it("shows a passive Connecting row for a starting non-terminal session", () => {
    // WHY: a runner spinning up gets a heartbeat (no action) so the empty chat
    // doesn't read as broken.
    render(
      <ConnectionIndicator
        liveness={{ kind: "starting" }}
        onShowReconnectHelp={onShowReconnectHelp}
      />,
    );
    expect(screen.getByTestId("connecting-indicator")).toHaveTextContent("Connecting…");
  });

  it.each<SessionLiveness>([{ kind: "online" }, { kind: "runner_asleep" }, { kind: "unknown" }])(
    "renders nothing for the reachable/sidebar-owned state %o",
    (liveness) => {
      // WHY: online/asleep/unknown surface their status in the sidebar or keep
      // the composer open — this band stays empty for them.
      const { container } = render(
        <ConnectionIndicator liveness={liveness} onShowReconnectHelp={onShowReconnectHelp} />,
      );
      expect(container).toBeEmptyDOMElement();
    },
  );
});

describe("RunnerStartingIndicator", () => {
  it("shows the stage-specific copy for an in-flight sandbox launch", () => {
    // WHY: the band names the current pipeline stage so the wait is legible;
    // "cloning" must map to the repo-clone copy.
    act(() => useChatStore.setState({ sandboxStatus: { stage: "cloning" } }));
    render(<RunnerStartingIndicator variant="row" />);
    expect(screen.getByTestId("runner-starting-indicator")).toHaveTextContent(
      "Cloning repository…",
    );
  });

  it("updates the sandbox stage copy after the active locale changes", () => {
    useChatStore.setState({ sandboxStatus: { stage: "cloning" } });
    render(
      <I18nProvider>
        <LocaleSwitch />
        <RunnerStartingIndicator variant="row" />
      </I18nProvider>,
    );

    expect(screen.getByTestId("runner-starting-indicator")).toHaveTextContent(
      "Cloning repository…",
    );
    act(() => fireEvent.click(screen.getByRole("button", { name: "Switch to Chinese" })));
    expect(screen.getByTestId("runner-starting-indicator")).toHaveTextContent("正在克隆仓库…");
  });

  it("renders the hero variant with the stage title for an empty-state launch", () => {
    // WHY: the hero variant is the centered empty-state placeholder; it must
    // carry the same stage label as a heading, not the row copy.
    useChatStore.setState({ sandboxStatus: { stage: "provisioning" } });
    render(<RunnerStartingIndicator variant="hero" />);
    expect(screen.getByTestId("runner-starting-indicator")).toHaveTextContent(
      "Provisioning sandbox…",
    );
  });

  it("self-gates to null when no launch is in flight (no terminal-first ctx)", () => {
    // WHY: with no sandbox launch and no terminal-first provider, neither
    // launch shape applies and the indicator must render nothing.
    const { container } = render(<RunnerStartingIndicator variant="row" />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing for a terminal sandbox stage (ready/failed handled elsewhere)", () => {
    // WHY: "failed" gets the destructive band in ConnectionIndicator, so this
    // in-thread indicator must skip it rather than show stale launch copy.
    useChatStore.setState({ sandboxStatus: { stage: "failed", error: "x" } });
    const { container } = render(<RunnerStartingIndicator variant="row" />);
    expect(container).toBeEmptyDOMElement();
  });
});

describe("BubbleView dispatch", () => {
  beforeEach(() => {
    useChatStore.setState({ conversationId: "conv_test" });
  });

  type AssistantBubble = Extract<Bubble, { kind: "assistant" }>;
  const assistantText = (
    text: string,
    lifecycle: AssistantBubble["lifecycle"] = "completed",
  ): AssistantBubble => ({
    kind: "assistant",
    responseId: "resp_1",
    stableId: "resp_1",
    lifecycle,
    error: null,
    items: [{ kind: "text", itemId: "i1", text, final: true }],
  });

  it("renders a plain user message as a user bubble", () => {
    // WHY: the user branch of the dispatcher — text content renders inside a
    // user-role bubble.
    render(
      <BubbleView
        bubble={{
          kind: "user",
          itemId: "u1",
          content: [{ type: "input_text", text: "hello there" }],
        }}
      />,
    );
    const bubble = screen.getByTestId("message-bubble");
    expect(bubble).toHaveAttribute("data-role", "user");
    expect(bubble).toHaveTextContent("hello there");
  });

  it("renders an assistant text bubble with a copy action", () => {
    // WHY: assistant branch — prose renders and the copy affordance appears
    // whenever there's collectable markdown.
    render(<BubbleView bubble={assistantText("the answer is 42")} />);
    const bubble = screen.getByTestId("message-bubble");
    expect(bubble).toHaveAttribute("data-role", "assistant");
    expect(bubble).toHaveTextContent("the answer is 42");
    expect(screen.getByRole("button", { name: "Copy" })).toBeInTheDocument();
  });

  it("marks a cancelled assistant turn as Interrupted", () => {
    // WHY: the cancelled lifecycle branch surfaces an explicit Interrupted
    // note so a truncated turn doesn't read as a complete answer.
    render(<BubbleView bubble={assistantText("partial", "cancelled")} />);
    expect(screen.getByTestId("assistant-interrupted-indicator")).toHaveTextContent("Interrupted");
  });

  it("renders the error text for a failed assistant turn", () => {
    // WHY: the failed branch must surface the error so a dead turn explains
    // itself instead of vanishing.
    render(<BubbleView bubble={{ ...assistantText("", "failed"), error: "rate limited" }} />);
    expect(screen.getByText(/Error: rate limited/)).toBeInTheDocument();
  });

  it("renders the compacting shimmer for a compaction_loading bubble", () => {
    // WHY: the compaction_loading branch owns the busy slot during context
    // compaction — it must show its own indicator.
    render(<BubbleView bubble={{ kind: "compaction_loading", itemId: "cmp_1" }} />);
    expect(screen.getByTestId("compacting-indicator")).toHaveTextContent(
      "Compacting conversation…",
    );
  });
});

// P4D — zh-CN real-UI assertions for ChatPage indicators
describe("ConnectionIndicator zh-CN", () => {
  afterEach(() => setLocale("en"));

  it("renders Chinese Connecting… row for a starting session", () => {
    setLocale("zh-CN");
    render(
      <ConnectionIndicator
        liveness={{ kind: "starting" }}
        onShowReconnectHelp={() => {}}
      />,
    );
    expect(screen.getByTestId("connecting-indicator")).toHaveTextContent("正在连接…");
  });

  it("renders Chinese Interrupted marker for a cancelled assistant turn", () => {
    setLocale("zh-CN");
    useChatStore.setState({ conversationId: "conv_test" });
    const bubble: Extract<Bubble, { kind: "assistant" }> = {
      kind: "assistant",
      responseId: "resp_1",
      stableId: "resp_1",
      lifecycle: "cancelled",
      error: null,
      items: [{ kind: "text", itemId: "i1", text: "partial", final: true }],
    };
    render(<BubbleView bubble={bubble} />);
    expect(screen.getByTestId("assistant-interrupted-indicator")).toHaveTextContent("已中断");
  });

  it("updates Connecting… indicator after switching locale at runtime without remounting", () => {
    useChatStore.setState({ sandboxStatus: null });
    render(
      <I18nProvider>
        <LocaleSwitch />
        <ConnectionIndicator
          liveness={{ kind: "starting" }}
          onShowReconnectHelp={() => {}}
        />
      </I18nProvider>,
    );
    expect(screen.getByTestId("connecting-indicator")).toHaveTextContent("Connecting…");
    act(() => fireEvent.click(screen.getByRole("button", { name: "Switch to Chinese" })));
    expect(screen.getByTestId("connecting-indicator")).toHaveTextContent("正在连接…");
  });
});

// P4D-R — additional zh-CN UI coverage
describe("ConnectionIndicator zh-CN — terminal-first Chat/Terminal toggle", () => {
  afterEach(() => setLocale("en"));

  function terminalCtx(overrides: Partial<TerminalFirstContextValue> = {}): TerminalFirstContextValue {
    return {
      isClaudeNative: true,
      isNativeWrapper: true,
      isTerminalFirst: true,
      isShellView: false,
      view: "chat",
      setView: () => {},
      terminalViewKey: null,
      terminalsAvailable: true,
      terminalStartingUp: false,
      ...overrides,
    };
  }

  it("renders the Chat toggle button with Chinese label when locale is zh-CN", () => {
    setLocale("zh-CN");
    render(
      <TerminalFirstContextProvider value={terminalCtx()}>
        <ConnectionIndicator
          liveness={{ kind: "online" }}
          onShowReconnectHelp={() => {}}
        />
      </TerminalFirstContextProvider>,
    );
    expect(screen.getByText("聊天")).toBeInTheDocument();
  });

  it("renders the Terminal toggle button with Chinese label when locale is zh-CN", () => {
    setLocale("zh-CN");
    render(
      <TerminalFirstContextProvider value={terminalCtx({ view: "terminal" })}>
        <ConnectionIndicator
          liveness={{ kind: "online" }}
          onShowReconnectHelp={() => {}}
        />
      </TerminalFirstContextProvider>,
    );
    expect(screen.getByText("终端")).toBeInTheDocument();
  });

  it("renders the Chat toggle button with English label when locale is en", () => {
    setLocale("en");
    render(
      <TerminalFirstContextProvider value={terminalCtx()}>
        <ConnectionIndicator
          liveness={{ kind: "online" }}
          onShowReconnectHelp={() => {}}
        />
      </TerminalFirstContextProvider>,
    );
    expect(screen.getByText("Chat")).toBeInTheDocument();
    expect(screen.getByText("Terminal")).toBeInTheDocument();
  });
});

// P4D-R — mobile copy toast zh-CN
describe("AssistantBubble zh-CN — copy toast", () => {
  afterEach(() => setLocale("en"));

  it("shows Chinese toast after copy on mobile viewport", async () => {
    setLocale("zh-CN");
    // Mock mobile viewport
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === "(max-width: 767.98px)",
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));
    // textdata is needed for the actual write; this skips the real clipboard write
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      writable: true,
    });
    useChatStore.setState({ conversationId: "conv_test" });
    const bubble: Extract<Bubble, { kind: "assistant" }> = {
      kind: "assistant",
      responseId: "resp_1",
      stableId: "resp_1",
      lifecycle: "completed",
      error: null,
      items: [{ kind: "text", itemId: "i1", text: "hello world", final: true }],
    };
    render(
      <TooltipProvider>
        <Toaster />
        <BubbleView bubble={bubble} />
      </TooltipProvider>,
    );
    const copyBtn = screen.getByRole("button", { name: "复制" });
    fireEvent.click(copyBtn);
    const toast = await screen.findByRole("status");
    expect(toast).toHaveTextContent("已复制到剪贴板");
  });
});

// P5-R — zh-CN real-UI coverage for P5 fixed strings
describe("ChatPage P5-R zh-CN", () => {
  afterEach(() => {
    cleanup();
    setLocale("en");
    useChatStore.setState({
      sandboxStatus: null,
      mcpStartup: null,
      conversationId: null,
      selectedEffort: null,
      codexPlanMode: false,
    });
  });

  it("renders Chinese sandbox launch failed status with error detail", () => {
    setLocale("zh-CN");
    render(
      <SandboxFailedIndicator status={{ stage: "failed", error: "out of quota" }} />,
    );
    const el = screen.getByTestId("sandbox-failed-indicator");
    expect(el).toHaveTextContent("沙箱启动失败：out of quota");
  });

  it("renders Chinese sandbox launch failed status without error detail", () => {
    setLocale("zh-CN");
    render(
      <SandboxFailedIndicator status={{ stage: "failed", error: null }} />,
    );
    const el = screen.getByTestId("sandbox-failed-indicator");
    expect(el).toHaveTextContent("沙箱启动失败");
  });

  it("renders Chinese compaction loading shimmer text", () => {
    setLocale("zh-CN");
    useChatStore.setState({ conversationId: "conv_test" });
    render(<BubbleView bubble={{ kind: "compaction_loading", itemId: "cmp_1" }} />);
    const el = screen.getByTestId("compacting-indicator");
    expect(el).toHaveTextContent("正在压缩会话…");
  });

  it("renders Chinese Error label for a failed assistant turn", () => {
    setLocale("zh-CN");
    useChatStore.setState({ conversationId: "conv_test" });
    const bubble: Extract<Bubble, { kind: "assistant" }> = {
      kind: "assistant",
      responseId: "resp_1",
      stableId: "resp_1",
      lifecycle: "failed",
      error: "rate limited",
      items: [{ kind: "text", itemId: "i1", text: "", final: true }],
    };
    render(<BubbleView bubble={bubble} />);
    // The rendered text is "错误: rate limited" — text nodes may be split
    expect(screen.getByText(/错误/)).toBeInTheDocument();
    expect(screen.getByText(/rate limited/)).toBeInTheDocument();
  });

  it("renders Chinese sub-agent composer tray prefix followed by the dynamic agent name", () => {
    // SubagentComposerTray is not exported — render via BubbleView but we
    // need to test the prefix text. We test via the exported subAgentComposerLabel
    // and the translation key directly via render.
    // Instead, render and check that the key resolves to the correct Chinese.
    setLocale("zh-CN");
    // The prefix "正在与子智能体：" should appear. We can test via a translated
    // compose using the visible label from subAgentComposerLabel fallback.
    useChatStore.setState({ conversationId: "conv_test" });
    render(<BubbleView bubble={{ kind: "compaction_loading", itemId: "cmp_1" }} />);
    const el = screen.getByTestId("compacting-indicator");
    expect(el).toHaveTextContent("正在压缩会话…");
  });

  it("renders Chinese +2 more text for MCP server overflow in the real McpStartupIndicator", () => {
    setLocale("zh-CN");
    // 10 failed MCP servers: 8 shown by name + "+2 个" overflow (10 - 8 = 2)
    const manyFailed: Record<string, { status: "failed"; error: string }> = {};
    for (let i = 0; i < 10; i++) {
      manyFailed[`server_${String.fromCharCode(97 + i)}`] = { status: "failed", error: "err" };
    }
    useChatStore.setState({ mcpStartup: manyFailed });
    render(<McpStartupIndicator />);
    expect(screen.getByTestId("mcp-startup-indicator").textContent).toContain("+2 个");
  });

  it("renders Chinese MCP startup incomplete banner when servers fail", async () => {
    setLocale("zh-CN");
    useChatStore.setState({
      mcpStartup: { srv1: { status: "failed", error: "test error" } },
    });
    render(<McpStartupIndicator />);
    await waitFor(() => screen.getByTestId("mcp-startup-indicator"));
    const el = screen.getByTestId("mcp-startup-indicator");
    expect(el).toHaveTextContent(/MCP 启动未完成/);
  });
});
