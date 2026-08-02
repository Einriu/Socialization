import { request } from "@/api/client";
import type { AIModel, Page, Provider, ProviderInput } from "@/api/types";

export function listProviders(): Promise<Page<Provider>> {
  return request<Page<Provider>>("/api/providers?page=1&page_size=100");
}

export function createProvider(input: ProviderInput): Promise<Provider> {
  return request<Provider>("/api/providers", { method: "POST", body: JSON.stringify(input) });
}

export function updateProvider(
  providerId: string,
  input: Partial<ProviderInput> & { clear_api_key?: boolean },
): Promise<Provider> {
  return request<Provider>(`/api/providers/${providerId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteProvider(providerId: string): Promise<void> {
  return request(`/api/providers/${providerId}`, { method: "DELETE" });
}

export function testProvider(providerId: string): Promise<{ ok: boolean; models: number; latency_ms: number }> {
  return request(`/api/providers/${providerId}/test`, { method: "POST" });
}

export function syncModels(providerId: string): Promise<{ created: number; updated: number }> {
  return request(`/api/providers/${providerId}/sync-models`, { method: "POST" });
}

export function listModels(providerId: string): Promise<AIModel[]> {
  return request<AIModel[]>(`/api/providers/${providerId}/models`);
}

export function createModel(
  providerId: string,
  input: { model_id: string; display_name?: string },
): Promise<AIModel> {
  return request<AIModel>(`/api/providers/${providerId}/models`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateModel(modelId: string, input: Partial<AIModel>): Promise<AIModel> {
  return request<AIModel>(`/api/ai-models/${modelId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteModel(modelId: string): Promise<void> {
  return request(`/api/ai-models/${modelId}`, { method: "DELETE" });
}
