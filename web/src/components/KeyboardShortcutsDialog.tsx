// A read-only "Keyboard shortcuts" overlay listing the shortcuts that already
// exist in the chat surface. It is intentionally a mirror of the live
// behavior — every row here corresponds to a handler that ships today
// (composer `handleKeyDown`, the global session-switch / message-nav hotkeys,
// and the approve hotkey). Nothing here binds new behavior except the dialog's
// own opener (⌘/Ctrl + /), which this component registers.
//
// Self-contained: it owns its open state and listens for its opener directly
// (a window keydown for ⌘/Ctrl+/, plus a custom event so a menu entry can open
// it without prop-drilling). Mount it once near the app shell.

import { useEffect, useState, type ReactNode } from "react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { isNativeShell } from "@/lib/nativeBridge";
import { useTranslation } from "@/i18n";

// Custom event the dialog listens for, so non-adjacent surfaces (e.g. the
// account menu) can open it without threading state through the tree.
export const KEYBOARD_SHORTCUTS_EVENT = "omnigent:open-keyboard-shortcuts";

/** Dispatch the open event — used by menu entries that can't reach the state. */
export function openKeyboardShortcuts(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(KEYBOARD_SHORTCUTS_EVENT));
}

// Platform-aware modifier glyphs. macOS shows ⌘/⌥; elsewhere Ctrl/Alt — the
// same split the underlying handlers use (`metaKey || ctrlKey`).
const IS_MAC =
  typeof navigator !== "undefined" &&
  /Mac|iPhone|iPad|iPod/i.test(navigator.platform || navigator.userAgent || "");

/** Modifier label shown in menu hints (⌘ on macOS, Ctrl elsewhere).
 *  Kept for backward compat — Sidebar.tsx imports this. i18n-aware code should
 *  resolve `t("shortcuts.ctrl")` at render time instead. */
export const MOD_KEY = IS_MAC ? "⌘" : "Ctrl";

// Non-translatable key glyphs (symbols).
const CMD = "⌘";
const ENTER = "↵";
const SHIFT = "⇧";
const OPT = "⌥";
const UP = "↑";
const DOWN = "↓";

interface ShortcutDef {
  labelKey: string;
  /** Keys rendered left→right as chips. A chord (held together) or, for the
   *  arrow-pairs, the two interchangeable keys for that action. */
  keys: string[];
}

interface ShortcutGroupDef {
  titleKey: string;
  /** Optional qualifier shown next to the group title (translation key). */
  noteKey?: string;
  items: ShortcutDef[];
}

// ONLY shortcuts that exist today (see file header). Keep in sync with the
// composer's `handleKeyDown` and the global hotkey hooks.
// All title / note / label values are translation keys, resolved at render time.
// Key glyphs (modKey, altKey, escKey, tabKey) are passed in so Ctrl/Alt/Esc/Tab
// can be translated at render time.
function buildShortcutGroups(
  modKey: string,
  altKey: string,
  escKey: string,
  tabKey: string,
  native: boolean,
): ShortcutGroupDef[] {
  const groups: ShortcutGroupDef[] = [
    {
      titleKey: "shortcuts.general",
      items: [
        { labelKey: "shortcuts.openCommandPalette", keys: [modKey, "K"] },
        { labelKey: "shortcuts.showKeyboardShortcuts", keys: [modKey, "/"] },
      ],
    },
    {
      titleKey: "shortcuts.inChats",
      items: [
        { labelKey: "shortcuts.sendMessage", keys: [ENTER] },
        { labelKey: "shortcuts.newLineInMessage", keys: [SHIFT, ENTER] },
        { labelKey: "shortcuts.recallPreviousPrompt", keys: [UP] },
        { labelKey: "shortcuts.recallNextPrompt", keys: [DOWN] },
        { labelKey: "shortcuts.acceptApproval", keys: [modKey, ENTER] },
        { labelKey: "shortcuts.stopResponse", keys: [escKey] },
      ],
    },
    {
      titleKey: "shortcuts.navigation",
      items: [
        { labelKey: "shortcuts.previousSession", keys: [modKey, UP] },
        { labelKey: "shortcuts.nextSession", keys: [modKey, DOWN] },
      ],
    },
    {
      titleKey: "shortcuts.view",
      items: [
        { labelKey: "shortcuts.toggleConversationsSidebar", keys: [modKey, altKey, "["] },
        { labelKey: "shortcuts.toggleWorkspaceSidebar", keys: [modKey, altKey, "]"] },
      ],
    },
    {
      titleKey: "shortcuts.slashCommands",
      noteKey: "shortcuts.whileMenuOpen",
      items: [
        { labelKey: "shortcuts.navigateSuggestions", keys: [UP, DOWN] },
        { labelKey: "shortcuts.applyHighlightedCommand", keys: [tabKey] },
        { labelKey: "shortcuts.dismissMenu", keys: [escKey] },
      ],
    },
  ];

  // Numeric pinned-session jump. The chord is platform-aware (see
  // usePinnedSessionHotkeys): plain Cmd/Ctrl+digit in the Electron shell, but
  // Cmd/Ctrl+Alt+digit in a browser tab, where plain Cmd+digit is reserved for
  // native tab-switching. Shown in both, with the matching glyphs.
  const pinnedKeys = native ? [modKey, "1…0"] : [modKey, altKey, "1…0"];
  return groups.map((group) =>
    group.titleKey === "shortcuts.navigation"
      ? { ...group, items: [...group.items, { labelKey: "shortcuts.jumpToPinned", keys: pinnedKeys }] }
      : group,
  );
}

function Kbd({ children }: { children: ReactNode }) {
  return (
    <kbd className="inline-flex h-6 min-w-6 items-center justify-center rounded-md border border-border bg-muted px-1.5 font-sans text-xs font-medium text-muted-foreground">
      {children}
    </kbd>
  );
}

/**
 * The shortcut reference, grouped, as plain inline content (no dialog
 * chrome). Shared by the {@link KeyboardShortcutsDialog} overlay and the
 * Settings page, which embeds it directly instead of behind a trigger.
 */
export function KeyboardShortcutsList() {
  const { t } = useTranslation();

  // Translate the few key names that have locale-specific renderings.
  const ctrl = t("shortcuts.ctrl");
  const alt = t("shortcuts.alt");
  const esc = t("shortcuts.esc");
  const tab = t("shortcuts.tab");

  const modKey = IS_MAC ? CMD : ctrl;
  const altKey = IS_MAC ? OPT : alt;

  // Feature-based, stable per session; computed at render so tests can vary it.
  const groups = buildShortcutGroups(modKey, altKey, esc, tab, isNativeShell());

  return (
    <>
      {groups.map((group) => (
        <section key={group.titleKey} className="mb-4 last:mb-0">
          <h3 className="mb-1 text-xs font-medium text-muted-foreground">
            {t(group.titleKey)}
            {group.noteKey ? (
              <span className="ml-1.5 font-normal text-muted-foreground/70">· {t(group.noteKey)}</span>
            ) : null}
          </h3>
          <ul>
            {group.items.map((item) => (
              <li
                key={item.labelKey}
                className="flex items-center justify-between gap-4 border-b border-border/60 py-2.5 last:border-b-0"
              >
                <span className="text-sm text-foreground">{t(item.labelKey)}</span>
                <span className="flex shrink-0 items-center gap-1">
                  {item.keys.map((key) => (
                    <Kbd key={`${item.labelKey}-${key}`}>{key}</Kbd>
                  ))}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </>
  );
}

export function KeyboardShortcutsDialog() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      // ⌘/Ctrl + / toggles the panel. Plain `/` is the composer's slash-menu
      // trigger, so require the modifier and no Shift/Alt to avoid clashing.
      if ((e.metaKey || e.ctrlKey) && !e.altKey && !e.shiftKey && e.key === "/") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    const onOpenEvent = () => setOpen(true);
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener(KEYBOARD_SHORTCUTS_EVENT, onOpenEvent);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener(KEYBOARD_SHORTCUTS_EVENT, onOpenEvent);
    };
  }, []);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("shortcuts.title")}</DialogTitle>
          <DialogDescription className="sr-only">
            {t("shortcuts.description")}
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-[70vh] overflow-y-auto pr-1">
          <KeyboardShortcutsList />
        </div>
      </DialogContent>
    </Dialog>
  );
}
