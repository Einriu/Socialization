import { request } from "@/api/client";
import type {
  Conversation,
  ConversationLink,
  ConversationMessage,
  Page,
} from "@/api/types";

export function listConversations(): Promise<Page<Conversation>> {
  return request<Page<Conversation>>("/api/conversations?page=1&page_size=100");
}

export function createConversation(input: {
  title?: string;
  provider_id?: string | null;
  model_id?: string | null;
}): Promise<Conversation> {
  return request<Conversation>("/api/conversations", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateConversation(
  conversationId: string,
  input: Partial<{ title: string; provider_id: string | null; model_id: string | null }>,
): Promise<Conversation> {
  return request<Conversation>(`/api/conversations/${conversationId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteConversation(conversationId: string): Promise<void> {
  return request(`/api/conversations/${conversationId}`, { method: "DELETE" });
}

export function getMessages(conversationId: string): Promise<Page<ConversationMessage>> {
  return request<Page<ConversationMessage>>(
    `/api/conversations/${conversationId}/messages?page=1&page_size=200`,
  );
}

export function sendMessageStream(
  conversationId: string,
  content: string,
  modelId?: string | null,
  signal?: AbortSignal,
): Promise<Response> {
  return fetch(`/api/conversations/${conversationId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, model_id: modelId ?? null }),
    signal,
  });
}

export function cancelGeneration(conversationId: string): Promise<void> {
  return request(`/api/conversations/${conversationId}/cancel`, { method: "POST" });
}

export function regenerateStream(
  conversationId: string,
  messageId: string,
  signal?: AbortSignal,
): Promise<Response> {
  return fetch(
    `/api/conversations/${conversationId}/messages/${messageId}/regenerate`,
    { method: "POST", signal },
  );
}

export function setLinks(
  conversationId: string,
  input: { person_id?: string | null; topic_id?: string | null; document_id?: string | null },
): Promise<ConversationLink[]> {
  return request<ConversationLink[]>(`/api/conversations/${conversationId}/links`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}
