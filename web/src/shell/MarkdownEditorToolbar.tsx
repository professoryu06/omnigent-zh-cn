// Toolbar for the TipTap markdown rich-text editor.
//
// Receives the TipTap Editor instance as a prop and uses editor.chain() for
// formatting commands, editor.isActive() for active-state badges, and
// editor.storage.markdown.getMarkdown() for copy / save.

import { useCallback, useEffect, useRef, useState } from "react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useEditorState } from "@tiptap/react";
import {
  AlignCenter,
  AlignLeft,
  AlignRight,
  Bold,
  Check,
  Code,
  Copy,
  Heading1,
  Heading2,
  Heading3,
  Italic,
  List,
  ListOrdered,
  ListTodo,
  Pilcrow,
  Quote,
  Redo2,
  Strikethrough,
  Table2,
  Undo2,
} from "lucide-react";
import type { Editor } from "@tiptap/react";
// Side-effect import: applies @tiptap/markdown's Editor interface augmentation
// (adds editor.getMarkdown()) so TypeScript resolves the method correctly.
import "@tiptap/markdown";
import { useTranslation } from "@/i18n";
// Type-only import: activates @tiptap/extension-table's TypeScript module
// augmentation so editor.chain() includes table commands (insertTable, etc.)
// without pulling the full extension into the runtime bundle.
// eslint-disable-next-line import/no-empty-named-blocks -- deliberate type-only augmentation trigger, not a stray empty import
import type {} from "@tiptap/extension-table";
// Same trick for the list package's command augmentation (toggleTaskList).
// eslint-disable-next-line import/no-empty-named-blocks -- deliberate type-only augmentation trigger, not a stray empty import
import type {} from "@tiptap/extension-list";
import { TableMap, cellAround, colCount, findTable, isInTable } from "@tiptap/pm/tables";
import { cn } from "@/lib/utils";

export function ToolbarBtn({
  children,
  active = false,
  title,
  onClick,
  className,
}: {
  children: React.ReactNode;
  active?: boolean;
  title: string;
  onClick: () => void;
  className?: string;
}) {
  return (
    <button
      type="button"
      title={title}
      aria-label={title}
      // Prevent the mousedown from stealing focus away from the editor.
      onMouseDown={(e) => e.preventDefault()}
      onClick={onClick}
      className={cn(
        "min-w-[1.75rem] rounded px-1.5 py-0.5 text-xs transition-colors",
        active
          ? "bg-accent text-accent-foreground"
          : "text-muted-foreground hover:bg-muted hover:text-foreground",
        className,
      )}
    >
      {children}
    </button>
  );
}

export function Divider() {
  return <div className="mx-1 h-4 w-px shrink-0 bg-border" />;
}

function TableBtn({ editor }: { editor: Editor | null }) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [hovered, setHovered] = useState({ rows: 0, cols: 0 });
  const MAX = 6;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        title={t("editor.insertTable")}
        aria-label={t("editor.insertTable")}
        disabled={!editor}
        onMouseDown={(e) => e.preventDefault()}
        className="min-w-[1.75rem] rounded px-1.5 py-0.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:pointer-events-none disabled:opacity-40"
      >
        <Table2 className="size-3.5" />
      </PopoverTrigger>
      <PopoverContent
        className="w-auto p-2"
        align="start"
        onMouseLeave={() => setHovered({ rows: 0, cols: 0 })}
      >
        <p className="mb-1.5 text-xs text-muted-foreground">
          {hovered.rows > 0
            ? t("editor.tableGridDesc", { rows: hovered.rows, cols: hovered.cols })
            : t("editor.insertTable")}
        </p>
        <div className="flex flex-col gap-0.5">
          {Array.from({ length: MAX }, (_, r) => (
            <div key={r} className="flex gap-0.5">
              {Array.from({ length: MAX }, (_, c) => (
                <button
                  key={c}
                  type="button"
                  aria-label={t("editor.tableGridLabel", { rows: r + 1, cols: c + 1 })}
                  onMouseDown={(e) => e.preventDefault()}
                  onMouseEnter={() => setHovered({ rows: r + 1, cols: c + 1 })}
                  onClick={() => {
                    // Use stable loop indices rather than async hovered state to
                    // avoid a 0×0 insert on fast clicks before state flushes.
                    editor
                      ?.chain()
                      .focus()
                      .insertTable({
                        rows: r + 1,
                        cols: c + 1,
                        withHeaderRow: true,
                      })
                      .run();
                    setOpen(false);
                  }}
                  className={cn(
                    "h-5 w-5 cursor-pointer rounded-sm border transition-colors",
                    r < hovered.rows && c < hovered.cols
                      ? "border-primary bg-primary/20"
                      : "border-border bg-muted hover:border-primary/50 hover:bg-primary/10",
                  )}
                />
              ))}
            </div>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}

type ColumnAlign = "left" | "center" | "right";

function setColumnAlign(editor: Editor, align: ColumnAlign | null): boolean {
  const { state } = editor.view;
  if (!isInTable(state)) return false;
  const $cell = cellAround(state.selection.$head);
  if (!$cell) return false;
  const col = colCount($cell);
  const tableResult = findTable(state.selection.$from);
  if (!tableResult) return false;
  const map = TableMap.get(tableResult.node);
  const cellPositions = map.cellsInRect({
    left: col,
    right: col + 1,
    top: 0,
    bottom: map.height,
  });
  if (cellPositions.length === 0) return false;
  const tr = state.tr;
  let changed = false;
  cellPositions.forEach((nodePos) => {
    const node = tableResult.node.nodeAt(nodePos);
    const absPos = nodePos + tableResult.start;
    if (node && node.attrs.align !== align) {
      tr.setNodeMarkup(absPos, null, { ...node.attrs, align });
      changed = true;
    }
  });
  if (changed) {
    editor.view.dispatch(tr);
    editor.view.focus();
  }
  return true;
}

function TableAlignControls({ editor }: { editor: Editor }) {
  const { t } = useTranslation();
  const state = useEditorState({
    editor,
    selector: (ctx) => ({
      inTable: (ctx.editor?.isActive("tableCell") || ctx.editor?.isActive("tableHeader")) ?? false,
      align:
        (ctx.editor?.getAttributes("tableCell").align as ColumnAlign | undefined) ??
        (ctx.editor?.getAttributes("tableHeader").align as ColumnAlign | undefined) ??
        null,
    }),
  });

  if (!state?.inTable) return null;

  const current = state.align;

  return (
    <>
      <Divider />
      <ToolbarBtn
        active={current === "left"}
        title={t("editor.alignColumnLeft")}
        onClick={() => setColumnAlign(editor, "left")}
      >
        <AlignLeft className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={current === "center"}
        title={t("editor.alignColumnCenter")}
        onClick={() => setColumnAlign(editor, "center")}
      >
        <AlignCenter className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={current === "right"}
        title={t("editor.alignColumnRight")}
        onClick={() => setColumnAlign(editor, "right")}
      >
        <AlignRight className="size-3.5" />
      </ToolbarBtn>
    </>
  );
}

export function ToolbarPlugin({
  editor,
  onSave,
  isSaving,
  isDirty,
  saveError,
  saveDisabled,
  hasExternalUpdate,
}: {
  editor: Editor | null;
  onSave: (markdown: string) => void;
  isSaving: boolean;
  isDirty: boolean;
  saveError: boolean;
  saveDisabled: boolean;
  // True while an external-edit conflict is unresolved. Blocks manual saves
  // (⌘S / pill click) so the user can't clobber the change without first
  // picking Keep mine / Load latest.
  hasExternalUpdate: boolean;
}) {
  // Re-render only when the values that drive the toolbar UI actually change.
  const editorState = useEditorState({
    editor,
    selector: (ctx) => ({
      canUndo: ctx.editor?.can().undo() ?? false,
      canRedo: ctx.editor?.can().redo() ?? false,
      isParagraph:
        (ctx.editor?.isActive("paragraph") &&
          !ctx.editor?.isActive("heading") &&
          !ctx.editor?.isActive("blockquote")) ??
        false,
      isH1: ctx.editor?.isActive("heading", { level: 1 }) ?? false,
      isH2: ctx.editor?.isActive("heading", { level: 2 }) ?? false,
      isH3: ctx.editor?.isActive("heading", { level: 3 }) ?? false,
      isBlockquote: ctx.editor?.isActive("blockquote") ?? false,
      isBold: ctx.editor?.isActive("bold") ?? false,
      isItalic: ctx.editor?.isActive("italic") ?? false,
      isStrike: ctx.editor?.isActive("strike") ?? false,
      isCode: ctx.editor?.isActive("code") ?? false,
      isTaskList: ctx.editor?.isActive("taskList") ?? false,
    }),
  });

  const [isCopied, setIsCopied] = useState(false);
  const copyTimeoutRef = useRef<number>(0);

  const { t } = useTranslation();

  const getMarkdown = useCallback(() => editor?.getMarkdown() ?? "", [editor]);

  const handleCopy = useCallback(() => {
    const md = getMarkdown();
    if (!navigator?.clipboard?.writeText) return;
    navigator.clipboard
      .writeText(md)
      .then(() => {
        setIsCopied(true);
        window.clearTimeout(copyTimeoutRef.current);
        copyTimeoutRef.current = window.setTimeout(() => setIsCopied(false), 2000);
      })
      .catch(() => {
        // ignore clipboard errors
      });
  }, [getMarkdown]);

  const handleSave = useCallback(() => {
    if (!isDirty || saveDisabled || hasExternalUpdate) return;
    onSave(getMarkdown());
  }, [getMarkdown, onSave, isDirty, saveDisabled, hasExternalUpdate]);

  // Cmd/Ctrl+S to save.
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave]);

  const {
    canUndo,
    canRedo,
    isParagraph,
    isH1,
    isH2,
    isH3,
    isBlockquote,
    isBold,
    isItalic,
    isStrike,
    isCode,
    isTaskList,
  } = editorState ?? {};

  // Auto-save status pill (replaces the explicit Save button). ⌘S / clicking
  // an actionable status flushes via onSave; the label reflects live state:
  //   saveDisabled → "Offline"; saveError + dirty → "Retry"; isSaving →
  //   "Saving…"; isDirty (debounce pending) → "Unsaved"; else "Saved".
  // Offline takes precedence so we never surface a clickable status that
  // silently no-ops. "Retry" requires isDirty too: a stale error with nothing
  // to save (e.g. after "Load latest" clears dirty) would otherwise show a
  // dead "Retry" — fall through to "Saved" instead.
  const saveStatus = saveDisabled
    ? {
        label: t("editor.offline"),
        title: t("editor.runnerOfflineSave"),
        tone: "offline" as const,
      }
    : saveError && isDirty
      ? { label: t("editor.retry"), title: t("editor.saveFailedRetry"), tone: "error" as const }
      : isSaving
        ? { label: t("editor.saving"), title: t("editor.saving"), tone: "pending" as const }
        : isDirty
          ? {
              label: t("editor.unsaved"),
              title: t("editor.unsavedChangesHint"),
              tone: "pending" as const,
            }
          : { label: t("editor.saved"), title: t("editor.allChangesSaved"), tone: "saved" as const };
  // Clickable only when there are unsaved edits and a write can land: never
  // while offline, mid-conflict, or when there's nothing to persist.
  const saveClickable = !saveDisabled && !hasExternalUpdate && isDirty;

  return (
    <div className="flex flex-wrap items-center gap-0.5 border-b border-border bg-card px-2 py-1 shrink-0">
      <ToolbarBtn
        title={t("editor.undo")}
        onClick={() => editor?.chain().focus().undo().run()}
        className={!canUndo ? "opacity-30 cursor-default" : ""}
      >
        <Undo2 className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        title={t("editor.redo")}
        onClick={() => editor?.chain().focus().redo().run()}
        className={!canRedo ? "opacity-30 cursor-default" : ""}
      >
        <Redo2 className="size-3.5" />
      </ToolbarBtn>
      <Divider />
      <ToolbarBtn
        active={isParagraph}
        title={t("editor.normal")}
        onClick={() => editor?.chain().focus().setParagraph().run()}
      >
        <Pilcrow className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={isH1}
        title={t("editor.heading1")}
        onClick={() => editor?.chain().focus().toggleHeading({ level: 1 }).run()}
      >
        <Heading1 className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={isH2}
        title={t("editor.heading2")}
        onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
      >
        <Heading2 className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={isH3}
        title={t("editor.heading3")}
        onClick={() => editor?.chain().focus().toggleHeading({ level: 3 }).run()}
      >
        <Heading3 className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={isBlockquote}
        title={t("editor.quote")}
        onClick={() => editor?.chain().focus().toggleBlockquote().run()}
      >
        <Quote className="size-3.5" />
      </ToolbarBtn>
      <Divider />
      <ToolbarBtn
        active={isBold}
        title={t("editor.bold")}
        onClick={() => editor?.chain().focus().toggleBold().run()}
      >
        <Bold className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={isItalic}
        title={t("editor.italic")}
        onClick={() => editor?.chain().focus().toggleItalic().run()}
      >
        <Italic className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={isStrike}
        title={t("editor.strikethrough")}
        onClick={() => editor?.chain().focus().toggleStrike().run()}
      >
        <Strikethrough className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={isCode}
        title={t("editor.inlineCode")}
        onClick={() => editor?.chain().focus().toggleCode().run()}
      >
        <Code className="size-3.5" />
      </ToolbarBtn>
      <Divider />
      <ToolbarBtn
        title={t("editor.bulletList")}
        onClick={() => editor?.chain().focus().toggleBulletList().run()}
      >
        <List className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        title={t("editor.numberedList")}
        onClick={() => editor?.chain().focus().toggleOrderedList().run()}
      >
        <ListOrdered className="size-3.5" />
      </ToolbarBtn>
      <ToolbarBtn
        active={isTaskList}
        title={t("editor.taskList")}
        onClick={() => editor?.chain().focus().toggleTaskList().run()}
      >
        <ListTodo className="size-3.5" />
      </ToolbarBtn>
      <Divider />
      <TableBtn editor={editor} />
      {editor && <TableAlignControls editor={editor} />}
      <div className="ml-auto flex items-center gap-2">
        <ToolbarBtn title={t("editor.copy")} onClick={handleCopy}>
          {isCopied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
        </ToolbarBtn>
        <button
          type="button"
          title={saveStatus.title}
          aria-label={saveStatus.title}
          // Keep editor focus so a manual flush doesn't blur mid-edit.
          onMouseDown={(e) => e.preventDefault()}
          onClick={saveClickable ? handleSave : undefined}
          disabled={!saveClickable}
          className={cn(
            "flex items-center gap-1 rounded px-2 py-0.5 text-xs transition-colors",
            saveStatus.tone === "error" &&
              "text-destructive hover:bg-destructive/10 cursor-pointer",
            saveStatus.tone === "offline" && "text-warning cursor-default",
            saveStatus.tone === "pending" &&
              (saveClickable
                ? "text-muted-foreground hover:bg-muted hover:text-foreground cursor-pointer"
                : "text-muted-foreground cursor-default"),
            saveStatus.tone === "saved" && "text-muted-foreground cursor-default",
          )}
        >
          {saveStatus.tone === "saved" && <Check className="size-3.5" />}
          {saveStatus.label}
        </button>
      </div>
    </div>
  );
}
