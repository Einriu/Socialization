import { HealthStatus } from "@/components/health/health-status";

export function DashboardPage() {
  return (
    <main className="mx-auto w-full max-w-3xl space-y-8 px-6 py-10">
      <section className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Socialization</h1>
        <p className="text-muted-foreground">系统状态</p>
      </section>
      <section className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
        <h2 className="mb-3 text-base font-medium">后端服务</h2>
        <HealthStatus />
      </section>
    </main>
  );
}
