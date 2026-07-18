import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourceRoot = path.join(repositoryRoot, "web", "src");
const typescriptModule = await import(
  new URL("../web/node_modules/typescript/lib/typescript.js", import.meta.url),
);
const ts = typescriptModule.default ?? typescriptModule;

const COPY_ATTRIBUTES = new Set(["aria-label", "alt", "placeholder", "title"]);
const TOAST_RECEIVERS = new Set(["message", "notification", "notifications", "toast", "toaster"]);
const SCOPES = ["shell", "pages", "components", "lib", "other"];

function normalizeText(value) {
  return value.replace(/\s+/g, " ").trim();
}

function normalizePath(filePath) {
  return filePath.split(path.sep).join("/");
}

function compareText(left, right) {
  return left < right ? -1 : left > right ? 1 : 0;
}

function scopeForPath(filePath) {
  const normalized = normalizePath(filePath);
  return SCOPES.find((scope) => normalized.includes(`/src/${scope}/`)) ?? "other";
}

function protectedLiteralReason(text) {
  if (/^[\p{P}\p{S}]+$/u.test(text)) return "non_copy_literal";
  if (/^(?:https?:)?\/\//i.test(text)) return "url";
  if (/^[a-z]:[\\/]/i.test(text) || /^~?[\\/]/.test(text)) return "file_path";
  if (/\b(?:git|npm|pnpm|yarn|uv|python(?:3)?|node|codex|claude)\s+[\w-]/i.test(text)) {
    return "shell_command";
  }
  if (/\b(?:gpt|claude|deepseek|glm|gemini|minimax|hermes)(?:[- .]\w+)?\b/i.test(text)) {
    return "model_or_harness";
  }
  return null;
}

function jsxElementName(attribute) {
  const opening = attribute.parent?.parent;
  return opening && ts.isJsxOpeningLikeElement(opening)
    ? opening.tagName.getText()
    : undefined;
}

function literalFromInitializer(initializer) {
  if (initializer && ts.isStringLiteral(initializer)) return initializer.text;
  if (initializer && ts.isJsxExpression(initializer) && initializer.expression && ts.isStringLiteral(initializer.expression)) {
    return initializer.expression.text;
  }
  return null;
}

function callReceiverName(expression) {
  if (!ts.isPropertyAccessExpression(expression)) return null;
  if (ts.isIdentifier(expression.expression)) return expression.expression.text;
  return null;
}

function entryFromNode(sourceFile, node, text, source) {
  const position = sourceFile.getLineAndCharacterOfPosition(node.getStart(sourceFile));
  return {
    text,
    source,
    line: position.line + 1,
  };
}

export function extractCopyFromSource(source, filePath) {
  const sourceFile = ts.createSourceFile(filePath, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  const candidates = [];
  const excluded = [];

  function addCandidate(node, rawText, origin) {
    const text = normalizeText(rawText);
    if (!text) return;

    const reason = protectedLiteralReason(text);
    if (reason) {
      excluded.push({ ...entryFromNode(sourceFile, node, text, origin), reason });
      return;
    }

    candidates.push(entryFromNode(sourceFile, node, text, origin));
  }

  function inspect(node) {
    if (ts.isJsxText(node)) {
      addCandidate(node, node.getText(sourceFile), "jsx_text");
    } else if (ts.isJsxAttribute(node)) {
      const attributeName = node.name.getText(sourceFile);
      const elementName = jsxElementName(node);
      const isSupportedPlaceholder = attributeName !== "placeholder" || ["input", "textarea"].includes(elementName);
      const literal = COPY_ATTRIBUTES.has(attributeName) && isSupportedPlaceholder
        ? literalFromInitializer(node.initializer)
        : null;
      if (literal !== null) addCandidate(node, literal, `attribute:${attributeName}`);
    } else if (ts.isCallExpression(node)) {
      const receiver = callReceiverName(node.expression);
      const firstArgument = node.arguments[0];
      if (receiver && TOAST_RECEIVERS.has(receiver) && firstArgument && ts.isStringLiteral(firstArgument)) {
        addCandidate(node, firstArgument.text, `notification:${receiver}`);
      }
    } else if (ts.isStringLiteral(node)) {
      const reason = protectedLiteralReason(node.text);
      if (reason) excluded.push({ ...entryFromNode(sourceFile, node, node.text, "literal"), reason });
    }

    ts.forEachChild(node, inspect);
  }

  inspect(sourceFile);

  const compareEntries = (left, right) => compareText(left.text, right.text) || left.line - right.line || compareText(left.source, right.source);
  return {
    candidates: candidates.sort(compareEntries),
    excluded: excluded.sort(compareEntries),
  };
}

export function buildInventory(files) {
  const occurrences = [];
  for (const { filePath, source } of files) {
    const normalizedFilePath = normalizePath(filePath);
    const seenText = new Set();
    for (const candidate of extractCopyFromSource(source, filePath).candidates) {
      if (seenText.has(candidate.text)) continue;
      seenText.add(candidate.text);
      occurrences.push({ ...candidate, file: normalizedFilePath, scope: scopeForPath(filePath) });
    }
  }
  const scopedEntries = Object.fromEntries(SCOPES.map((scope) => [scope, []]));
  const byText = new Map();

  for (const entry of occurrences) {
    scopedEntries[entry.scope].push(entry);
    byText.set(entry.text, [...(byText.get(entry.text) ?? []), entry]);
  }

  const scopes = Object.fromEntries(
    SCOPES.map((scope) => [scope, {
      count: scopedEntries[scope].length,
      texts: [...new Set(scopedEntries[scope].map((entry) => entry.text))].sort(compareText),
      occurrences: scopedEntries[scope].sort((left, right) => compareText(left.text, right.text) || compareText(left.file, right.file) || left.line - right.line),
    }]),
  );
  const duplicates = [...byText.entries()]
    .filter(([, entries]) => entries.length > 1)
    .map(([text, entries]) => ({
      text,
      occurrences: entries.length,
      files: [...new Set(entries.map((entry) => entry.file))].sort(),
    }))
    .sort((left, right) => compareText(left.text, right.text));

  return {
    schemaVersion: 1,
    sourceRoot: "web/src",
    summary: {
      candidateCount: occurrences.length,
      uniqueTextCount: byText.size,
      duplicateTextCount: duplicates.length,
    },
    scopes,
    duplicates,
  };
}

async function collectSourceFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const children = await Promise.all(entries.map(async (entry) => {
    const entryPath = path.join(directory, entry.name);
    if (entry.isDirectory()) return collectSourceFiles(entryPath);
    return /\.(?:ts|tsx)$/.test(entry.name) && !/\.test\.tsx?$/.test(entry.name) ? [entryPath] : [];
  }));
  return children.flat();
}

function readArgument(name, fallback) {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1];
}

async function main() {
  const requestedScope = readArgument("--scope", "all");
  if (requestedScope !== "all" && !SCOPES.includes(requestedScope)) {
    throw new Error(`Unknown scope: ${requestedScope}`);
  }

  const targetDirectory = requestedScope === "all" ? sourceRoot : path.join(sourceRoot, requestedScope);
  const filePaths = await collectSourceFiles(targetDirectory);
  const files = await Promise.all(filePaths.map(async (absolutePath) => ({
    filePath: normalizePath(path.relative(repositoryRoot, absolutePath)),
    source: await readFile(absolutePath, "utf8"),
  })));
  const inventory = buildInventory(files);
  inventory.generatedAt = new Date().toISOString();
  inventory.exclusions = files.flatMap(({ filePath, source }) => extractCopyFromSource(source, filePath).excluded.map((entry) => ({ ...entry, file: filePath })));
  inventory.exclusions.sort((left, right) => compareText(left.text, right.text) || compareText(left.file, right.file) || left.line - right.line);

  const outputPath = path.resolve(repositoryRoot, readArgument("--output", "ops/translation-inventory.json"));
  await mkdir(path.dirname(outputPath), { recursive: true });
  await writeFile(outputPath, `${JSON.stringify(inventory, null, 2)}\n`, "utf8");
  console.log(`Wrote ${path.relative(repositoryRoot, outputPath)} with ${inventory.summary.candidateCount} candidate occurrences.`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main();
}
