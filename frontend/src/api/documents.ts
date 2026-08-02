import { request } from "@/api/client";
import type { DocumentChunkItem, DocumentRecord, Page } from "@/api/types";

export function uploadDocument(file: File): Promise<DocumentRecord> {
  const form = new FormData();
  form.append("file", file);
  return request<DocumentRecord>("/api/documents/upload", {
    method: "POST",
    body: form,
  });
}

export function listDocuments(params: {
  page?: number;
  pageSize?: number;
  personId?: string;
  topicId?: string;
} = {}): Promise<Page<DocumentRecord>> {
  const query = new URLSearchParams();
  query.set("page", String(params.page ?? 1));
  query.set("page_size", String(params.pageSize ?? 20));
  if (params.personId) query.set("person_id", params.personId);
  if (params.topicId) query.set("topic_id", params.topicId);
  return request<Page<DocumentRecord>>(`/api/documents?${query.toString()}`);
}

export function processDocument(documentId: string): Promise<DocumentRecord> {
  return request<DocumentRecord>(`/api/documents/${documentId}/process`, { method: "POST" });
}

export function deleteDocument(documentId: string): Promise<void> {
  return request(`/api/documents/${documentId}`, { method: "DELETE" });
}

export function listChunks(documentId: string): Promise<Page<DocumentChunkItem>> {
  return request<Page<DocumentChunkItem>>(
    `/api/documents/${documentId}/chunks?page=1&page_size=100`,
  );
}

export function setDocumentLinks(
  documentId: string,
  input: { person_id?: string | null; topic_id?: string | null },
): Promise<DocumentRecord> {
  return request<DocumentRecord>(`/api/documents/${documentId}/links`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function saveWebClip(
  url: string,
  title?: string,
): Promise<{ id: string; filename: string; status: string }> {
  return request("/api/web-clips", {
    method: "POST",
    body: JSON.stringify({ url, title: title ?? null }),
  });
}
