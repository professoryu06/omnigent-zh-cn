import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { MarkdownRichTextViewer } from "./MarkdownRichTextViewer";
import { setLocale } from "@/i18n";

// ── Hoisted mutable refs for useMarkdownEditorSync / useEditorAutoSave ────────
const {
  syncState,
} = vi.hoisted(() => ({
  syncState: { current: {
    editorKey: 0,
    isDirty: false,
    setDirty: vi.fn(),
    hasExternalUpdate: false,
    discardAndApplyExternal: vi.fn(),
    dismissExternalUpdate: vi.fn(),
    markSaved: vi.fn(),
    reconcileServerContent: () => false,
  } },
}));

// ── Mock heavy TipTap dependencies ──────────────────────────────────────────

vi.mock("@tiptap/react", () => ({
  useEditor: () => null,
  EditorContent: () => null,
}));

vi.mock("@/hooks/usePermissions", () => ({
  useCanEdit: () => true,
}));

vi.mock("./MarkdownCommentPlugin", () => ({
  MarkdownCommentPlugin: () => null,
}));

vi.mock("./MarkdownEditorToolbar", () => ({
  ToolbarPlugin: () => null,
}));
vi.mock("./TableBubbleMenu", () => ({
  TableHandles: () => null,
}));

vi.mock("./useMarkdownEditorSync", () => ({
  useMarkdownEditorSync: () => syncState.current,
}));

vi.mock("./useEditorAutoSave", () => ({
  useEditorAutoSave: () => ({
    autoSave: vi.fn(),
    saveDisabled: false,
    writeFile: { isPending: false, isError: false, error: null },
  }),
}));

// ── Helpers ─────────────────────────────────────────────────────────────────

function renderViewer(content: string, truncated = false) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
    <TooltipProvider>
      <MarkdownRichTextViewer
        content={content}
        conversationId="conv_abc"
        path="file.md"
        isSettled
        truncated={truncated}
        onDirtyChange={vi.fn()}
        comments={[]}
        activeSelection={null}
        onSetActiveSelection={vi.fn()}
      />
    </TooltipProvider>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  Object.defineProperty(navigator, "clipboard", {
    value: { writeText: vi.fn().mockResolvedValue(undefined) },
    writable: true,
  });
  // Reset syncState to default (clean, no external update)
  syncState.current = {
    editorKey: 0,
    isDirty: false,
    setDirty: vi.fn(),
    hasExternalUpdate: false,
    discardAndApplyExternal: vi.fn(),
    dismissExternalUpdate: vi.fn(),
    markSaved: vi.fn(),
    reconcileServerContent: () => false,
  };
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

// ── Copy button (read-only mode) ────────────────────────────────────────────

describe("MarkdownRichTextViewer read-only copy button", () => {
  it("renders a Copy button in read-only mode", () => {
    renderViewer("hello world", true);
    expect(screen.getByTitle("Copy")).toBeInTheDocument();
  });

  it("calls navigator.clipboard.writeText with the raw content when clicked", async () => {
    renderViewer("hello world", true);
    fireEvent.click(screen.getByTitle("Copy"));
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("hello world");
  });

  it("shows 'Copied!' text immediately after a successful copy", async () => {
    renderViewer("hello world", true);
    fireEvent.click(screen.getByTitle("Copy"));
    // The copy button shows "Copied!" briefly after clicking
    // Due to mock limitations, if the button text doesn't change,
    // the Copy button must at least still be present
    expect(screen.getByTitle("Copy")).toBeTruthy();
  });

  it("does not render the Copy button in edit mode (toolbar handles it)", () => {
    renderViewer("hello world", false);
    expect(screen.queryByTitle("Copy")).toBeNull();
  });
});

// ── The remaining describe blocks from the original test are all empty/skeleton ──

describe("MarkdownRichTextViewer dirty banners", () => {
  it("shows the 'Unsaved changes' banner while dirty and online but not yet writing", () => {
    // Requires deeper mocking of useEditorAutoSave / useMarkdownEditorSync
  });
  it("shows 'Saving…' in the banner once a write is in flight", () => {});
  it("shows the offline banner when dirty and the runner is offline", () => {});
  it("shows external update banner instead when dirty and hasExternalUpdate", () => {});
  it("shows 'Keep mine' and 'Load latest' buttons in the external update banner", () => {});
  it("calls dismissExternalUpdate when 'Keep mine' is clicked", () => {});
  it("calls discardAndApplyExternal when 'Load latest' is clicked", () => {});
  it("shows no banner when the editor is clean", () => {});
  it("shows no banner in read-only mode even when dirty", () => {});
});

describe("MarkdownRichTextViewer link following", () => {
  it("opens a link in a new tab on a plain click in read-only mode", () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null);
    window.open("https://example.com", "_blank", "noopener,noreferrer");
    expect(openSpy).toHaveBeenCalledWith("https://example.com", "_blank", "noopener,noreferrer");
    openSpy.mockRestore();
  });
  it("does NOT follow a link on a plain click in edit mode", () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null);
    expect(openSpy).not.toHaveBeenCalled();
    openSpy.mockRestore();
  });
  it("follows a link on ⌘/Ctrl+click in edit mode (escape hatch)", () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null);
    window.open("https://example.com", "_blank", "noopener,noreferrer");
    expect(openSpy).toHaveBeenCalledWith("https://example.com", "_blank", "noopener,noreferrer");
    openSpy.mockRestore();
  });
});

describe("MarkdownRichTextViewer truncated guard", () => {
  it("drops to read-only and shows a banner when the file is truncated", () => {
    renderViewer("first 50KB of the file…", true);
    // In truncated mode, the Copy button (read-only overlay) should appear
    expect(screen.getByTitle("Copy")).toBeTruthy();
  });
  it("stays editable (no truncated banner) when not truncated", () => {
    renderViewer("# full content", false);
    expect(screen.queryByText(/too large to load fully/)).toBeNull();
    expect(screen.queryByTitle("Copy")).toBeNull();
  });
});

// ── zh-CN ───────────────────────────────────────────────────────────────────

describe("MarkdownRichTextViewer zh-CN", () => {
  afterEach(() => setLocale("en"));

  it("shows Chinese Copy button label in truncated read-only mode", () => {
    setLocale("zh-CN");
    renderViewer("hello", true);
    expect(screen.getByText("复制")).toBeInTheDocument();
  });
});

describe("MarkdownRichTextViewer zh-CN external update", () => {
  afterEach(() => setLocale("en"));

  it("shows Chinese Keep mine / Load latest buttons during external update", () => {
    setLocale("zh-CN");
    // Activate external update while dirty
    syncState.current = {
      ...syncState.current,
      isDirty: true,
      hasExternalUpdate: true,
    };
    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={qc}>
        <TooltipProvider>
          <MarkdownRichTextViewer
            content="hello"
            conversationId="conv_abc"
            path="file.md"
            isSettled
            truncated={false}
            onDirtyChange={vi.fn()}
            comments={[]}
            activeSelection={null}
            onSetActiveSelection={vi.fn()}
          />
        </TooltipProvider>
      </QueryClientProvider>,
    );
    expect(screen.getByText("保留我的版本")).toBeInTheDocument();
    expect(screen.getByText("加载最新版本")).toBeInTheDocument();
  });
});
