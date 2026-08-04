import { describe, expect, it } from "vitest";
import { extractRoleNames } from "@/lib/practice-roles";

describe("extractRoleNames", () => {
  it("从背景文字中识别带角色说明的人物", () => {
    const text =
      "公司年会上，小王（市场部新人）第一次参加，小李（我的同学）也在场。";
    const roles = extractRoleNames(text);
    expect(roles.map((r) => r.name)).toEqual(["小王", "小李"]);
    expect(roles[0]?.role).toBe("市场部新人");
  });

  it("识别对话中的【角色名】", () => {
    const roles = extractRoleNames("【张三】今天天气不错。\n【李四】是啊。");
    expect(roles.map((r) => r.name)).toContain("张三");
    expect(roles.map((r) => r.name)).toContain("李四");
  });

  it("按出现次数排序", () => {
    const roles = extractRoleNames(
      "【小王】在吗。【小李】在。【小王】等下聊。【小王】先忙了。",
    );
    expect(roles[0]?.name).toBe("小王");
  });

  it("过滤通用称谓", () => {
    const roles = extractRoleNames("朋友（性格开朗）和同事（工作很拼）都在场。");
    expect(roles).toEqual([]);
  });

  it("无明确角色时返回空数组", () => {
    expect(extractRoleNames("只是一个普通的场景描述，没有具体人名。")).toEqual([]);
  });
});
