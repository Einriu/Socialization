import { request } from "@/api/client";
import type {
  FollowUpTask,
  ImportantDate,
  Page,
  Person,
  PersonFact,
  PersonInput,
  TimelineItem,
} from "@/api/types";

export interface ListPersonsParams {
  page?: number;
  pageSize?: number;
  q?: string;
  tagId?: string;
}

function buildQuery(params: Record<string, string | number | undefined>): string {
  const query = Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== "")
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join("&");
  return query ? `?${query}` : "";
}

export function listPersons(params: ListPersonsParams = {}): Promise<Page<Person>> {
  return request<Page<Person>>(
    `/api/persons${buildQuery({
      page: params.page ?? 1,
      page_size: params.pageSize ?? 20,
      q: params.q,
      tag_id: params.tagId,
    })}`,
  );
}

export function getPerson(personId: string): Promise<Person> {
  return request<Person>(`/api/persons/${personId}`);
}

export function createPerson(input: PersonInput): Promise<Person> {
  return request<Person>("/api/persons", { method: "POST", body: JSON.stringify(input) });
}

export function updatePerson(personId: string, input: Partial<PersonInput>): Promise<Person> {
  return request<Person>(`/api/persons/${personId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deletePerson(personId: string): Promise<void> {
  return request<void>(`/api/persons/${personId}`, { method: "DELETE" });
}

export function permanentDeletePerson(personId: string): Promise<void> {
  return request<void>(`/api/persons/${personId}/permanent?confirm=true`, { method: "DELETE" });
}

export function setPersonTags(personId: string, tagIds: string[]): Promise<Person> {
  return request<Person>(`/api/persons/${personId}/tags`, {
    method: "PUT",
    body: JSON.stringify({ tag_ids: tagIds }),
  });
}

export function listFacts(personId: string): Promise<Page<PersonFact>> {
  return request<Page<PersonFact>>(`/api/persons/${personId}/facts?page=1&page_size=100`);
}

export function createFact(
  personId: string,
  input: {
    fact_type: string;
    content: string;
    source_type?: string;
    confidence?: string;
    is_sensitive?: boolean;
  },
): Promise<PersonFact> {
  return request<PersonFact>(`/api/persons/${personId}/facts`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function deleteFact(factId: string): Promise<void> {
  return request<void>(`/api/person-facts/${factId}`, { method: "DELETE" });
}

export function listDates(personId: string): Promise<Page<ImportantDate>> {
  return request<Page<ImportantDate>>(`/api/persons/${personId}/dates?page=1&page_size=100`);
}

export function createDate(
  personId: string,
  input: { title: string; kind?: string; date_value: string; note?: string },
): Promise<ImportantDate> {
  return request<ImportantDate>(`/api/persons/${personId}/dates`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function deleteDate(dateId: string): Promise<void> {
  return request<void>(`/api/important-dates/${dateId}`, { method: "DELETE" });
}

export function listFollowUps(personId: string): Promise<Page<FollowUpTask>> {
  return request<Page<FollowUpTask>>(`/api/persons/${personId}/follow-ups?page=1&page_size=100`);
}

export function createFollowUp(
  personId: string,
  input: { title: string; due_at?: string | null; completed?: boolean },
): Promise<FollowUpTask> {
  return request<FollowUpTask>(`/api/persons/${personId}/follow-ups`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateFollowUp(
  taskId: string,
  input: Partial<{ title: string; due_at: string | null; completed: boolean }>,
): Promise<FollowUpTask> {
  return request<FollowUpTask>(`/api/follow-up-tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteFollowUp(taskId: string): Promise<void> {
  return request<void>(`/api/follow-up-tasks/${taskId}`, { method: "DELETE" });
}

export function getTimeline(personId: string): Promise<Page<TimelineItem>> {
  return request<Page<TimelineItem>>(`/api/persons/${personId}/timeline?page=1&page_size=100`);
}
