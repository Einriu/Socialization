export interface DatabaseHealth {
  connected: boolean;
  select_1_ok: boolean;
  journal_mode: string;
}

export interface HealthData {
  version: string;
  app_name: string;
  database: DatabaseHealth;
}

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export async function fetchHealth(signal?: AbortSignal): Promise<HealthData> {
  const response = await fetch("/api/health", { signal });
  if (!response.ok) {
    throw new Error(`健康检查失败：HTTP ${response.status}`);
  }
  const body = (await response.json()) as ApiResponse<HealthData>;
  if (body.code !== 0) {
    throw new Error(body.message || "健康检查失败");
  }
  return body.data;
}
