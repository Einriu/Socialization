import { request } from "@/api/client";
import type { Page, Tag } from "@/api/types";

export function listTags(): Promise<Page<Tag>> {
  return request<Page<Tag>>("/api/tags");
}

export function createTag(input: { name: string; color?: string; group_name?: string }): Promise<Tag> {
  return request<Tag>("/api/tags", { method: "POST", body: JSON.stringify(input) });
}

export function deleteTag(tagId: string): Promise<void> {
  return request<void>(`/api/tags/${tagId}`, { method: "DELETE" });
}
