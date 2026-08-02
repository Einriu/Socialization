import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { HealthStatus } from "@/components/health/health-status";

function okResponse(): Response {
  return {
    ok: true,
    status: 200,
    json: () =>
      Promise.resolve({
        code: 0,
        message: "ok",
        data: {
          version: "0.1.0",
          app_name: "Socialization",
          database: { connected: true, select_1_ok: true, journal_mode: "wal" },
        },
      }),
  } as Response;
}

describe("HealthStatus", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(okResponse()));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("后端正常时显示已连接状态", async () => {
    render(<HealthStatus />);
    expect(await screen.findByText("后端已连接，SQLite 正常")).toBeInTheDocument();
    expect(screen.getByText(/journal_mode: wal/)).toBeInTheDocument();
  });

  it("后端不可用时显示错误状态", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("网络错误")));
    render(<HealthStatus />);
    expect(await screen.findByText("后端不可用")).toBeInTheDocument();
    expect(screen.getByText("网络错误")).toBeInTheDocument();
  });

  it("点击重试后恢复为已连接状态", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new Error("网络错误"))
      .mockResolvedValueOnce(okResponse());
    vi.stubGlobal("fetch", fetchMock);
    render(<HealthStatus />);
    expect(await screen.findByText("后端不可用")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "重试" }));
    expect(await screen.findByText("后端已连接，SQLite 正常")).toBeInTheDocument();
  });
});
