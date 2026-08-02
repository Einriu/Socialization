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

export interface TopicCategoryNode {
  id: string;
  name: string;
  parent_id: string | null;
  children: TopicCategoryNode[];
}

export interface Topic {
  id: string;
  name: string;
  category_id: string | null;
  description: string | null;
  mastery_level: number;
  last_reviewed_at: string | null;
  created_at: string;
  updated_at: string;
  persons: PersonLite[];
}

export interface TopicInput {
  name: string;
  category_id?: string | null;
  description?: string | null;
  mastery_level?: number;
}

export interface TopicNote {
  topic_id: string;
  content_json: object | null;
  plain_text: string | null;
  updated_at: string | null;
}

export interface Provider {
  id: string;
  name: string;
  provider_type: string;
  base_url: string | null;
  enabled: boolean;
  timeout_seconds: number;
  max_retries: number;
  proxy: string | null;
  default_model_id: string | null;
  last_tested_at: string | null;
  created_at: string;
  updated_at: string;
  has_api_key: boolean;
  key_hint: string | null;
}

export interface ProviderInput {
  name: string;
  provider_type?: string;
  base_url?: string | null;
  api_key?: string | null;
  enabled?: boolean;
  timeout_seconds?: number;
  max_retries?: number;
  proxy?: string | null;
  default_model_id?: string | null;
}

export interface AIModel {
  id: string;
  provider_id: string;
  model_id: string;
  display_name: string | null;
  model_type: string;
  context_length: number | null;
  supports_streaming: boolean;
  supports_tools: boolean;
  supports_json: boolean;
  supports_vision: boolean;
  supports_reasoning: boolean;
  input_price_note: string | null;
  output_price_note: string | null;
  enabled: boolean;
  source: string;
  created_at: string;
}

export interface ConversationLink {
  id: string;
  person_id: string | null;
  topic_id: string | null;
}

export interface Conversation {
  id: string;
  title: string;
  mode: string;
  provider_id: string | null;
  model_id: string | null;
  summary: string | null;
  pinned: boolean;
  created_at: string;
  updated_at: string;
  links: ConversationLink[];
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  role: string;
  content: string | null;
  status: string;
  token_input: number | null;
  token_output: number | null;
  latency_ms: number | null;
  generated_by_ai: boolean;
  created_at: string;
}
