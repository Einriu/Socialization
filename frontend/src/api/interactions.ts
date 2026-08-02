import { request } from "@/api/client";
import type { Interaction, InteractionInput, Page } from "@/api/types";

export interface ListInteractionsParams {
  page?: number;
  pageSize?: number;
  personId?: string;
}

function buildQuery(params: Record<string, string | number | undefined>): string {
  const query = Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== "")
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join("&");
  return query ? `?${query}` : "";
}

export function listInteractions(
  params: ListInteractionsParams = {},
): Promise<Page<Interaction>> {
  return request<Page<Interaction>>(
    `/api/interactions${buildQuery({
      page: params.page ?? 1,
      page_size: params.pageSize ?? 20,
      person_id: params.personId,
    })}`,
  );
}

export function createInteraction(input: InteractionInput): Promise<Interaction> {
  return request<Interaction>("/api/interactions", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateInteraction(
  interactionId: string,
  input: Partial<InteractionInput>,
): Promise<Interaction> {
  return request<Interaction>(`/api/interactions/${interactionId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteInteraction(interactionId: string): Promise<void> {
  return request<void>(`/api/interactions/${interactionId}`, { method: "DELETE" });
}
