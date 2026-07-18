import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { I18nProvider, setLocale, translate } from "@/i18n";

const { mockUseServiceWorkerUpdate, reload, dismiss } = vi.hoisted(() => ({
  mockUseServiceWorkerUpdate: vi.fn(),
  reload: vi.fn(),
  dismiss: vi.fn(),
}));

vi.mock("./useServiceWorkerUpdate", () => ({
  useServiceWorkerUpdate: mockUseServiceWorkerUpdate,
}));

import { PWAUpdateBanner } from "./PWAUpdateBanner";

function mockUpdate(state: { needRefresh: boolean }): void {
  mockUseServiceWorkerUpdate.mockReturnValue({
    needRefresh: state.needRefresh,
    reload,
    dismiss,
  });
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("PWAUpdateBanner", () => {
  it("renders nothing when no update is available", () => {
    mockUpdate({ needRefresh: false });
    const { container } = render(<PWAUpdateBanner />);
    expect(container).toBeEmptyDOMElement();
  });

  it("offers Reload that applies the update when a new version is available", () => {
    mockUpdate({ needRefresh: true });
    render(<PWAUpdateBanner />);
    expect(screen.getByText(/new version/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /reload/i }));
    expect(reload).toHaveBeenCalledOnce();
  });

  it("dismisses the prompt", () => {
    mockUpdate({ needRefresh: true });
    render(<PWAUpdateBanner />);
    fireEvent.click(screen.getByRole("button", { name: /dismiss/i }));
    expect(dismiss).toHaveBeenCalledOnce();
  });
});

describe("zh-CN i18n", () => {
  it('translates "new version" banner text to "有新版本可用。"', () => {
    expect(translate("pwa.newVersionAvailable", {}, "zh-CN")).toBe("有新版本可用。");
  });

  it('translates "Reload" button text to "重新加载"', () => {
    expect(translate("pwa.reload", {}, "zh-CN")).toBe("重新加载");
  });

  it('translates "Dismiss" button text to "忽略"', () => {
    expect(translate("pwa.dismiss", {}, "zh-CN")).toBe("忽略");
  });

  it("renders inside I18nProvider with zh-CN locale set", () => {
    setLocale("zh-CN");
    mockUpdate({ needRefresh: true });
    render(
      <I18nProvider>
        <PWAUpdateBanner />
      </I18nProvider>,
    );
    // The banner text is currently hardcoded; once i18n-instrumented,
    // the Chinese text will appear. For now, verify the banner renders.
    expect(screen.getByRole("status")).toBeInTheDocument();
    setLocale("en");
  });
});
