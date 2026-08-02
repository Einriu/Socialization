import { describe, expect, it } from "vitest";
import { matchRoute } from "@/lib/router";

describe("matchRoute", () => {
  it("匹配静态路径", () => {
    expect(matchRoute("/persons", "/persons")).toEqual({ params: {} });
  });

  it("匹配带参数路径", () => {
    expect(matchRoute("/persons/abc-123", "/persons/:id")).toEqual({
      params: { id: "abc-123" },
    });
  });

  it("段数不一致时返回 null", () => {
    expect(matchRoute("/persons/abc/edit", "/persons/:id")).toBeNull();
  });

  it("静态段不一致时返回 null", () => {
    expect(matchRoute("/interactions/new", "/persons/:id")).toBeNull();
  });
});
