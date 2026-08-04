import { request } from "@/api/client";

export function generateBriefing(personId: string): Promise<string> {
  return request<{ briefing: string }>(`/api/persons/${personId}/briefing`, {
    method: "POST",
  }).then((data) => data.briefing);
}

export function extractInteraction(interactionId: string): Promise<ExtractionItem[]> {
  return request<ExtractionItem[]>(`/api/interactions/${interactionId}/extract`, {
    method: "POST",
  });
}

export interface ExtractionItem {
  id: string;
  kind: string;
  fact_type: string;
  content: string;
  status: string;
}

export function getPendingExtractions(interactionId: string): Promise<ExtractionItem[]> {
  return request<ExtractionItem[]>(`/api/interactions/${interactionId}/extractions`);
}

export function confirmExtractions(
  interactionId: string,
  ids: string[],
): Promise<{ confirmed: number }> {
  return request(`/api/interactions/${interactionId}/confirm-extractions`, {
    method: "POST",
    body: JSON.stringify({ ids }),
  });
}

export function reviewInteraction(interactionId: string): Promise<string> {
  return request<{ review: string }>(`/api/interactions/${interactionId}/review`, {
    method: "POST",
  }).then((data) => data.review);
}

export interface Scenario {
  id: string;
  scenario_type: string;
  title: string;
  description: string | null;
  channel: string;
  tags: string[];
  custom_prompt: string | null;
  participants: { name: string; role?: string; person_id?: string }[];
}

export function listScenarios(): Promise<Scenario[]> {
  return request<Scenario[]>("/api/practice/scenarios");
}

export interface TagLibrary {
  场合: string[];
  谈话背景: string[];
  对象类型: string[];
}

export function listTagLibrary(): Promise<TagLibrary> {
  return request<TagLibrary>("/api/practice/tag-library");
}

export function generateBackground(input: {
  channel: string;
  tags?: string[];
  custom_prompt?: string | null;
  person_ids?: string[];
  roles?: { name: string; role?: string }[];
}): Promise<string> {
  return request<{ background: string }>("/api/practice/generate-background", {
    method: "POST",
    body: JSON.stringify(input),
  }).then((data) => data.background);
}

export function createCustomScenario(input: {
  title: string;
  channel: string;
  tags?: string[];
  custom_prompt?: string | null;
  participants?: { name: string; role?: string }[];
}): Promise<{ id: string; title: string; channel: string; tags: string[] }> {
  return request("/api/practice/scenarios", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function createPracticeSession(
  scenarioId: string | null,
  options?: {
    channel?: string;
    tags?: string[];
    custom_prompt?: string | null;
    participants?: { name: string; role?: string; person_id?: string }[];
  },
): Promise<{
  id: string;
  title: string;
  channel: string;
  tags: string[];
  custom_prompt: string | null;
  participants: { name: string; role?: string }[];
}> {
  return request("/api/practice/sessions", {
    method: "POST",
    body: JSON.stringify({ scenario_id: scenarioId, ...options }),
  });
}

export interface PracticeSessionInfo {
  id: string;
  title: string;
  status: string;
  channel: string;
  tags: string[];
  custom_prompt: string | null;
  participants: { name: string; role?: string; person_id?: string }[];
  created_at: string;
}

export function listPracticeSessions(): Promise<PracticeSessionInfo[]> {
  return request<PracticeSessionInfo[]>("/api/practice/sessions");
}

export function deletePracticeSession(sessionId: string): Promise<void> {
  return request(`/api/practice/sessions/${sessionId}`, { method: "DELETE" });
}

export interface PracticeMessageItem {
  id: string;
  role: string;
  content: string;
}

export function listPracticeMessages(sessionId: string): Promise<PracticeMessageItem[]> {
  return request<PracticeMessageItem[]>(`/api/practice/sessions/${sessionId}/messages`);
}

export function practiceSendStream(sessionId: string, content: string): Promise<Response> {
  return fetch(`/api/practice/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
}

export function evaluateSession(
  sessionId: string,
): Promise<{ scores: Record<string, number>; summary: string }> {
  return request(`/api/practice/sessions/${sessionId}/evaluate`, { method: "POST" });
}

export function suggestReplies(sessionId: string): Promise<string[]> {
  return request<{ suggestions: string[] }>(
    `/api/practice/sessions/${sessionId}/suggest-replies`,
    { method: "POST" },
  ).then((data) => data.suggestions);
}

export interface ReviewItem {
  id: string;
  topic_id: string;
  topic_name: string;
  due_at: string;
  interval_days: number;
}

export function listDueReviews(): Promise<ReviewItem[]> {
  return request<ReviewItem[]>("/api/reviews/due");
}

export function answerReview(taskId: string, rating: string): Promise<{ interval_days: number }> {
  return request(`/api/reviews/${taskId}/answer?rating=${encodeURIComponent(rating)}`, {
    method: "POST",
  });
}

export interface DashboardData {
  persons: number;
  interactions: number;
  topics: number;
  documents: number;
  due_followups: { id: string; title: string; person_name: string }[];
  due_reviews: ReviewItem[];
  recent_interactions: { id: string; title: string; occurred_at: string }[];
}

export function getDashboard(): Promise<DashboardData> {
  return request<DashboardData>("/api/dashboard");
}

export function weeklyReport(): Promise<string> {
  return request<{ report: string }>("/api/reports/weekly", { method: "POST" }).then(
    (data) => data.report,
  );
}

export interface RelationshipItem {
  id: string;
  other_person_id: string;
  other_person_name: string;
  relation_type: string;
  note: string | null;
}

export function listRelationships(personId: string): Promise<RelationshipItem[]> {
  return request<RelationshipItem[]>(`/api/persons/${personId}/relationships`);
}

export function addRelationship(
  personId: string,
  input: { other_person_id: string; relation_type: string; note?: string | null },
): Promise<RelationshipItem> {
  return request<RelationshipItem>(`/api/persons/${personId}/relationships`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function deleteRelationship(relationshipId: string): Promise<void> {
  return request(`/api/relationships/${relationshipId}`, { method: "DELETE" });
}
