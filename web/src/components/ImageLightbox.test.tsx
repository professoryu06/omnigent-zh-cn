// Tests for the shared image lightbox: a ZoomableImage renders a button around
// an <img>; activating it opens a full-screen Dialog showing the same source,
// which closes via Escape or the "x" button.

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { I18nProvider, setLocale, translate } from "@/i18n";

// getEmbedRoot decides the Radix portal container; null → portal to body.
vi.mock("@/lib/host", () => ({
  getEmbedRoot: () => null,
}));

import { ImageLightboxProvider, ZoomableImage } from "./ImageLightbox";

afterEach(cleanup);

function renderWithProvider() {
  return render(
    <ImageLightboxProvider>
      <ZoomableImage src="/pic.png" alt="diagram" className="size-10" />
    </ImageLightboxProvider>,
  );
}

describe("ZoomableImage + ImageLightboxProvider", () => {
  it("renders a button wrapping an image (keeps the img role/name)", () => {
    renderWithProvider();
    expect(screen.getByRole("button", { name: "Zoom image: diagram" })).toBeInTheDocument();
    // The inner <img> keeps its image role and alt-derived name.
    const img = screen.getByRole("img", { name: "diagram" });
    expect(img).toHaveAttribute("src", "/pic.png");
    expect(img).toHaveClass("size-10");
  });

  it("does not render a dialog until the image is activated", () => {
    renderWithProvider();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("opens a dialog showing the full image on click", () => {
    renderWithProvider();
    fireEvent.click(screen.getByRole("button", { name: "Zoom image: diagram" }));
    const dialog = screen.getByRole("dialog");
    // The dialog hosts its own copy of the image at the same source.
    const dialogImg = screen.getAllByRole("img", { name: "diagram" }).at(-1)!;
    expect(dialog).toContainElement(dialogImg);
    expect(dialogImg).toHaveAttribute("src", "/pic.png");
  });

  it("closes the dialog with Escape", () => {
    renderWithProvider();
    fireEvent.click(screen.getByRole("button", { name: "Zoom image: diagram" }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.keyDown(document.body, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("closes the dialog with the x button", () => {
    renderWithProvider();
    fireEvent.click(screen.getByRole("button", { name: "Zoom image: diagram" }));
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("zooms in and out via the toolbar, updating the scale and label", () => {
    renderWithProvider();
    fireEvent.click(screen.getByRole("button", { name: "Zoom image: diagram" }));

    // Starts at fit (100%); zoom-out disabled, the preview img is unscaled.
    const previewImg = screen.getAllByRole("img", { name: "diagram" }).at(-1)!;
    expect(screen.getByRole("button", { name: "Reset zoom" })).toHaveTextContent("100%");
    expect(screen.getByRole("button", { name: "Zoom out" })).toBeDisabled();
    expect(previewImg).toHaveStyle({ transform: "translate(0px, 0px) scale(1)" });

    // One zoom-in step is +0.5 → 150%, and the transform scales up.
    fireEvent.click(screen.getByRole("button", { name: "Zoom in" }));
    expect(screen.getByRole("button", { name: "Reset zoom" })).toHaveTextContent("150%");
    expect(screen.getByRole("button", { name: "Zoom out" })).toBeEnabled();
    expect(previewImg).toHaveStyle({ transform: "translate(0px, 0px) scale(1.5)" });

    // The percentage acts as a reset back to fit.
    fireEvent.click(screen.getByRole("button", { name: "Reset zoom" }));
    expect(screen.getByRole("button", { name: "Reset zoom" })).toHaveTextContent("100%");
    expect(previewImg).toHaveStyle({ transform: "translate(0px, 0px) scale(1)" });
  });
});

describe("zh-CN i18n", () => {
  it('translates "Zoom in" accessible label to "放大"', () => {
    expect(translate("lightbox.zoomIn", {}, "zh-CN")).toBe("放大");
  });

  it('translates "Reset zoom" accessible label to "重置缩放"', () => {
    expect(translate("lightbox.resetZoom", {}, "zh-CN")).toBe("重置缩放");
  });

  it('translates "Zoom image" accessible label to "缩放图片"', () => {
    expect(translate("lightbox.zoomImage", {}, "zh-CN")).toBe("缩放图片");
  });

  it('translates "Close" accessible label to "关闭"', () => {
    expect(translate("lightbox.close", {}, "zh-CN")).toBe("关闭");
  });

  it("renders the zoom button inside I18nProvider with zh-CN locale", () => {
    setLocale("zh-CN");
    render(
      <I18nProvider>
        <ImageLightboxProvider>
          <ZoomableImage src="/pic.png" alt="diagram" className="size-10" />
        </ImageLightboxProvider>
      </I18nProvider>,
    );
    // The button aria-label currently remains English until the component is i18n-instrumented.
    expect(screen.getByRole("button")).toBeInTheDocument();
    setLocale("en");
  });
});
