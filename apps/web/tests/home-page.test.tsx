import { createElement } from "react";
import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";
import HomePage from "../app/page";

afterEach(() => cleanup());

describe("HomePage", () => {
  it("renders the first-minute authored-proof flow", () => {
    render(createElement(HomePage));

    expect(
      screen.getByRole("heading", {
        name: "What story won’t leave you alone?",
      }),
    ).toBeTruthy();
    expect(
      screen.getByRole("heading", {
        name: "Here’s the pressure point Mythos sees",
      }),
    ).toBeTruthy();
    expect(screen.getByText("Choose the first turn")).toBeTruthy();
    expect(
      screen.getByRole("article", { name: "Opening-scene preview" }),
    ).toBeTruthy();
  });

  it("changes the opening preview when the Writer chooses a fork", async () => {
    const user = userEvent.setup();

    render(createElement(HomePage));

    const opening = screen.getByRole("article", {
      name: "Opening-scene preview",
    });

    expect(within(opening).getByText(/Make it intimate/)).toBeTruthy();
    expect(within(opening).getByText(/wedding ring/)).toBeTruthy();

    await user.click(screen.getByRole("button", { name: /Make it dangerous/ }));

    expect(within(opening).getByText(/Make it dangerous/)).toBeTruthy();
    expect(within(opening).getByText(/standing across the alley/)).toBeTruthy();
  });
});
