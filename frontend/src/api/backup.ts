import { request } from "@/api/client";

export interface BackupRecord {
  id: string;
  filename: string;
  size_bytes: number;
  status: string;
  created_at: string;
}

export function listBackups(): Promise<BackupRecord[]> {
  return request<BackupRecord[]>("/api/backups");
}

export function createBackup(): Promise<BackupRecord> {
  return request<BackupRecord>("/api/backups", { method: "POST" });
}

export function restoreBackup(
  backupId: string,
): Promise<{ restored_from: string; safety_snapshot: string; journal_mode: string }> {
  return request(`/api/backups/${backupId}/restore?confirm=true`, { method: "POST" });
}

export function downloadBackupUrl(backupId: string): string {
  return `/api/backups/${backupId}/download`;
}

export function exportJson(): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>("/api/export/json");
}

export function importJson(payload: Record<string, unknown>): Promise<{ imported: Record<string, number> }> {
  return request("/api/import", { method: "POST", body: JSON.stringify(payload) });
}
