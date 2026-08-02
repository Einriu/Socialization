import { useCallback, useEffect, useRef, useState } from "react";
import { fetchHealth, type HealthData } from "@/api/health";
import { Button } from "@/components/ui/button";

type StatusState =
  | { phase: "loading" }
  | { phase: "ok"; data: HealthData }
  | { phase: "error"; message: string };

const REQUEST_TIMEOUT_MS = 5000;

export function HealthStatus() {
  const [status, setStatus] = useState<StatusState>({ phase: "loading" });
  const requestIdRef = useRef(0);

  const check = useCallback(async () => {
    const requestId = ++requestIdRef.current;
    setStatus({ phase: "loading" });
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      const data = await fetchHealth(controller.signal);
      if (requestId !== requestIdRef.current) {
        return;
      }
      setStatus({ phase: "ok", data });
    } catch (error) {
      if (requestId !== requestIdRef.current) {
        return;
      }
      const message = error instanceof Error ? error.message : "未知错误";
      setStatus({ phase: "error", message });
    } finally {
      window.clearTimeout(timer);
    }
  }, []);

  useEffect(() => {
    void check();
  }, [check]);

  if (status.phase === "loading") {
    return <p className="text-muted-foreground">正在检查后端连接…</p>;
  }

  if (status.phase === "error") {
    return (
      <div className="flex flex-col items-start gap-3">
        <div className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-destructive" aria-hidden />
          <p className="font-medium text-destructive">后端不可用</p>
        </div>
        <p className="text-sm text-muted-foreground">{status.message}</p>
        <Button variant="outline" onClick={() => void check()}>
          重试
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="size-2 rounded-full bg-emerald-500" aria-hidden />
      <p>后端已连接，SQLite 正常</p>
      <span className="text-sm text-muted-foreground">
        （版本 {status.data.version}，journal_mode: {status.data.database.journal_mode}）
      </span>
    </div>
  );
}
