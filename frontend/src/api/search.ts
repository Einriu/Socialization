import { request } from "@/api/client";
import type { SearchResult } from "@/api/types";

export function searchAll(q: string): Promise<SearchResult> {
  return request<SearchResult>(`/api/search?q=${encodeURIComponent(q)}`);
}
