import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CreateAgentDialog } from "./CreateAgentDialog";
import { setLocale } from "@/i18n";

vi.mock("@/lib/agentLabels", () => ({
  BRAIN_HARNESS_LABELS: { default: "Default", claude: "Claude" },
  useBrainHarnessLabels: () => ({ default: "Default", claude: "Claude" }),
}));

afterEach(() => {
  cleanup();
  setLocale("en");
});

function renderDialog(props: { open?: boolean } = {}) {
  const onOpenChange = vi.fn();
  const onCreate = vi.fn();
  return render(
    <CreateAgentDialog
      open={props.open ?? true}
      onOpenChange={onOpenChange}
      onCreate={onCreate}
    />,
  );
}

describe("CreateAgentDialog MCP placeholders", () => {
  it("shows English placeholders for the command and args MCP inputs", () => {
    renderDialog();
    // Click "Add server" to reveal MCP inputs
    fireEvent.click(screen.getByTestId("create-agent-add-mcp"));

    const commandInput = screen.getByTestId("create-agent-mcp-command");
    const argsInput = screen.getByTestId("create-agent-mcp-args");

    expect(commandInput).toHaveAttribute("placeholder", "command (e.g. npx)");
    expect(argsInput).toHaveAttribute(
      "placeholder",
      "args (e.g. -y @modelcontextprotocol/server-github)",
    );
  });

  it("shows Chinese placeholders for the command and args MCP inputs when locale is zh-CN", () => {
    setLocale("zh-CN");
    renderDialog();
    fireEvent.click(screen.getByTestId("create-agent-add-mcp"));

    const commandInput = screen.getByTestId("create-agent-mcp-command");
    const argsInput = screen.getByTestId("create-agent-mcp-args");

    expect(commandInput).toHaveAttribute("placeholder", "命令（例如：npx）");
    expect(argsInput).toHaveAttribute(
      "placeholder",
      "参数（例如：-y @modelcontextprotocol/server-github）",
    );
    setLocale("en");
  });
});
