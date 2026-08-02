export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Tag {
  id: string;
  name: string;
  color: string | null;
  group_name: string | null;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface Person {
  id: string;
  name: string;
  nickname: string | null;
  avatar_path: string | null;
  relationship_type: string | null;
  familiarity_level: number;
  met_at: string | null;
  met_location: string | null;
  met_via: string | null;
  organization: string | null;
  occupation: string | null;
  location: string | null;
  summary: string | null;
  privacy_level: string;
  archived: boolean;
  created_at: string;
  updated_at: string;
  tags: Tag[];
}

export interface PersonInput {
  name: string;
  nickname?: string | null;
  relationship_type?: string | null;
  familiarity_level?: number;
  met_at?: string | null;
  met_location?: string | null;
  met_via?: string | null;
  organization?: string | null;
  occupation?: string | null;
  location?: string | null;
  summary?: string | null;
  privacy_level?: string;
}

export interface PersonFact {
  id: string;
  person_id: string;
  fact_type: string;
  content: string;
  source_type: string;
  source_id: string | null;
  confidence: string;
  is_sensitive: boolean;
  created_at: string;
  updated_at: string;
}

export interface ImportantDate {
  id: string;
  person_id: string;
  title: string;
  kind: string | null;
  date_value: string;
  note: string | null;
  created_at: string;
}

export interface FollowUpTask {
  id: string;
  person_id: string | null;
  interaction_id: string | null;
  title: string;
  due_at: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TimelineItem {
  type: "interaction" | "fact" | "important_date";
  id: string;
  title: string;
  occurred_at: string;
  summary: string | null;
}

export interface PersonLite {
  id: string;
  name: string;
}

export interface Interaction {
  id: string;
  title: string;
  occurred_at: string;
  location: string | null;
  interaction_type: string;
  duration_minutes: number | null;
  summary: string | null;
  new_info: string | null;
  mood_state: string | null;
  my_performance: string | null;
  positive_feedback: string | null;
  awkward_points: string | null;
  follow_up: string | null;
  privacy_level: string;
  created_at: string;
  updated_at: string;
  persons: PersonLite[];
  topics: PersonLite[];
}

export interface InteractionInput {
  title: string;
  occurred_at?: string | null;
  location?: string | null;
  interaction_type?: string;
  duration_minutes?: number | null;
  summary?: string | null;
  new_info?: string | null;
  mood_state?: string | null;
  my_performance?: string | null;
  positive_feedback?: string | null;
  awkward_points?: string | null;
  follow_up?: string | null;
  privacy_level?: string;
  participant_ids: string[];
}
