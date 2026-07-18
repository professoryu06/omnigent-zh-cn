import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { setLocale } from "@/i18n";
import { AskUserQuestionForm } from "./AskUserQuestionForm";
import type { ClaudeQuestion } from "@/lib/askUserQuestion";

afterEach(() => {
  cleanup();
});

const singleQuestion: ClaudeQuestion[] = [
  {
    question: "Which framework?",
    header: "Framework",
    options: [{ label: "React" }, { label: "Vue" }],
    multiSelect: false,
  },
];

const twoQuestions: ClaudeQuestion[] = [
  {
    question: "First?",
    header: "",
    options: [{ label: "A" }],
    multiSelect: false,
  },
  {
    question: "Second?",
    header: "",
    options: [{ label: "B" }],
    multiSelect: false,
  },
];

describe("AskUserQuestionForm — zh-CN", () => {
  afterEach(() => {
    setLocale("en");
  });

  it("renders progress text in Chinese", () => {
    setLocale("zh-CN");
    render(
      <AskUserQuestionForm
        questions={singleQuestion}
        onSubmit={vi.fn()}
        onReject={vi.fn()}
      />,
    );

    expect(screen.getByTestId("ask-user-question-progress").textContent).toBe(
      "第 1 题，共 1 题：",
    );
  });

  it("renders progress text for multi-question carousel in Chinese", () => {
    setLocale("zh-CN");
    render(
      <AskUserQuestionForm
        questions={twoQuestions}
        onSubmit={vi.fn()}
        onReject={vi.fn()}
      />,
    );

    expect(screen.getByTestId("ask-user-question-progress").textContent).toBe(
      "第 1 题，共 2 题：",
    );

    fireEvent.click(screen.getByTestId("ask-user-question-next"));
    expect(screen.getByTestId("ask-user-question-progress").textContent).toBe(
      "第 2 题，共 2 题：",
    );
  });

  it("renders navigation and action buttons in Chinese", () => {
    setLocale("zh-CN");
    render(
      <AskUserQuestionForm
        questions={twoQuestions}
        onSubmit={vi.fn()}
        onReject={vi.fn()}
      />,
    );

    expect(
      screen.getByRole("button", { name: "上一题" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "下一题" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "取消" }),
    ).toBeInTheDocument();

    // Navigate to the last question to see Submit
    fireEvent.click(screen.getByRole("button", { name: "下一题" }));
    expect(
      screen.getByRole("button", { name: "提交" }),
    ).toBeInTheDocument();
  });

  it("renders the custom input placeholder in Chinese", () => {
    setLocale("zh-CN");
    render(
      <AskUserQuestionForm
        questions={singleQuestion}
        onSubmit={vi.fn()}
        onReject={vi.fn()}
      />,
    );

    expect(
      screen.getByPlaceholderText("输入内容"),
    ).toBeInTheDocument();
  });
});
