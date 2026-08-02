import { request } from "@/api/client";
import type { CustomField } from "@/api/types";

export function listCustomFields(): Promise<CustomField[]> {
  return request<CustomField[]>("/api/custom-fields");
}

export function createCustomField(input: {
  field_type: string;
  name: string;
  group_name?: string | null;
  options?: string[] | null;
  is_required?: boolean;
}): Promise<CustomField> {
  return request<CustomField>("/api/custom-fields", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function deleteCustomField(fieldId: string): Promise<void> {
  return request(`/api/custom-fields/${fieldId}`, { method: "DELETE" });
}

export function getCustomValues(personId: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/api/persons/${personId}/custom-values`);
}

export function setCustomValues(
  personId: string,
  values: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/api/persons/${personId}/custom-values`, {
    method: "PUT",
    body: JSON.stringify({ values }),
  });
}
