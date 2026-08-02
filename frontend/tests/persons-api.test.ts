import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/api/client";
import { listPersons } from "@/api/persons";

function jsonResponse(data: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: () => Promise.resolve(data),
  } as Response;
}

describe("listPersons", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("成功时返回分页数据", async () => {
    const data = { items: [{ id: "1", name: "张三" }], total: 1, page: 1, page_size: 20 };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ code: 0, message: "ok", data })),
    );
    const result = await listPersons({ page: 1, pageSize: 20 });
    expect(result.total).toBe(1);
    expect(result.items[0]?.name).toBe("张三");
    expect(vi.mocked(fetch)).toHaveBeenCalledWith(
      expect.stringContaining("/api/persons?page=1&page_size=20"),
      expect.anything(),
    );
  });

  it("后端错误时抛出 ApiError", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          jsonResponse({ code: "NOT_FOUND", message: "资源不存在", data: null }, false, 404),
        ),
    );
    await expect(listPersons()).rejects.toThrow(ApiError);
  });
});
