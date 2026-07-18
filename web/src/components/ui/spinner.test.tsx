import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Spinner } from "./spinner";
import { setLocale } from "@/i18n";

describe("Spinner", () => {
  it("renders a status role with default label", () => {
    render(<Spinner />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });
});

describe("Spinner zh-CN", () => {
  afterEach(() => setLocale("en"));

  it("has accessible name in Chinese when locale is zh-CN", () => {
    setLocale("zh-CN");
    render(<Spinner />);
    expect(screen.getByRole("status", { name: "加载中..." })).toBeInTheDocument();
  });

  it("has accessible name in English when locale is en", () => {
    setLocale("en");
    render(<Spinner />);
    expect(screen.getByRole("status", { name: "Loading..." })).toBeInTheDocument();
  });
});
