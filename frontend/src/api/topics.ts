import { request } from "@/api/client";
import type { Page, Topic, TopicCategoryNode, TopicInput, TopicNote } from "@/api/types";

export function listCategories(): Promise<TopicCategoryNode[]> {
  return request<TopicCategoryNode[]>("/api/topic-categories");
}

export function createCategory(input: {
  name: string;
  parent_id?: string | null;
}): Promise<{ id: string; name: string; parent_id: string | null }> {
  return request("/api/topic-categories", { method: "POST", body: JSON.stringify(input) });
}

export function deleteCategory(categoryId: string): Promise<void> {
  return request(`/api/topic-categories/${categoryId}`, { method: "DELETE" });
}

export function listTopics(params: {
  page?: number;
  pageSize?: number;
  q?: string;
  categoryId?: string;
} = {}): Promise<Page<Topic>> {
  const query = new URLSearchParams();
  query.set("page", String(params.page ?? 1));
  query.set("page_size", String(params.pageSize ?? 50));
  if (params.q) query.set("q", params.q);
  if (params.categoryId) query.set("category_id", params.categoryId);
  return request<Page<Topic>>(`/api/topics?${query.toString()}`);
}

export function getTopic(topicId: string): Promise<Topic> {
  return request<Topic>(`/api/topics/${topicId}`);
}

export function createTopic(input: TopicInput): Promise<Topic> {
  return request<Topic>("/api/topics", { method: "POST", body: JSON.stringify(input) });
}

export function updateTopic(topicId: string, input: Partial<TopicInput>): Promise<Topic> {
  return request<Topic>(`/api/topics/${topicId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteTopic(topicId: string): Promise<void> {
  return request(`/api/topics/${topicId}`, { method: "DELETE" });
}

export function setTopicPersons(topicId: string, personIds: string[]): Promise<Topic> {
  return request<Topic>(`/api/topics/${topicId}/persons`, {
    method: "PUT",
    body: JSON.stringify({ person_ids: personIds }),
  });
}

export function getNote(topicId: string): Promise<TopicNote> {
  return request<TopicNote>(`/api/topics/${topicId}/notes`);
}

export function saveNote(
  topicId: string,
  input: { content_json: object; plain_text: string; expected_updated_at?: string | null },
): Promise<TopicNote> {
  return request<TopicNote>(`/api/topics/${topicId}/notes`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}
