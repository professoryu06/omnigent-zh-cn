import assert from "node:assert/strict";
import test from "node:test";

import { buildInventory, extractCopyFromSource } from "./extract-ui-copy.mjs";

test("extracts visible JSX, accessible labels, and toast copy", () => {
  const source = `
    import { toast } from "sonner";

    export function Demo() {
      const command = "git status";
      const endpoint = "https://api.example.test/v1";
      const directory = "C:\\\\work\\\\project";
      const model = "GPT-5.5";

      toast.success("Saved successfully");
      return (
        <section title="Project details">
          Welcome back
          <button aria-label="Close panel" placeholder="Ignored on buttons">Start session</button>
          <input placeholder="Search sessions" />
        </section>
      );
    }
  `;

  const result = extractCopyFromSource(source, "web/src/shell/Demo.tsx");
  const texts = result.candidates.map((candidate) => candidate.text);

  assert.deepEqual(texts, [
    "Close panel",
    "Project details",
    "Saved successfully",
    "Search sessions",
    "Start session",
    "Welcome back",
  ]);
  assert.deepEqual(result.excluded.map((entry) => entry.text), [
    "C:\\work\\project",
    "GPT-5.5",
    "git status",
    "https://api.example.test/v1",
  ]);
});

test("groups candidates by scope and deduplicates identical UI copy", () => {
  const inventory = buildInventory([
    {
      filePath: "web/src/shell/Sidebar.tsx",
      source: `export const Sidebar = () => <button title="Settings">Settings</button>;`,
    },
    {
      filePath: "web/src/pages/SettingsPage.tsx",
      source: `export const SettingsPage = () => <h1>Settings</h1>;`,
    },
  ]);

  assert.equal(inventory.summary.candidateCount, 2);
  assert.equal(inventory.summary.uniqueTextCount, 1);
  assert.deepEqual(inventory.scopes.shell.texts, ["Settings"]);
  assert.deepEqual(inventory.scopes.pages.texts, ["Settings"]);
  assert.deepEqual(inventory.duplicates, [
    {
      text: "Settings",
      occurrences: 2,
      files: ["web/src/pages/SettingsPage.tsx", "web/src/shell/Sidebar.tsx"],
    },
  ]);
});

test("excludes punctuation-only JSX fragments", () => {
  const result = extractCopyFromSource(
    `export const Demo = () => <><span>!</span><span>@</span><span>#</span><span>Ready</span></>;`,
    "web/src/components/Demo.tsx",
  );

  assert.deepEqual(result.candidates.map((candidate) => candidate.text), ["Ready"]);
  assert.deepEqual(result.excluded.map((entry) => entry.reason), [
    "non_copy_literal",
    "non_copy_literal",
    "non_copy_literal",
  ]);
});
