import { HealthStatus } from "@/components/health/health-status";
import { Button } from "@/components/ui/button";
import { useRouter } from "@/lib/router";

export function DashboardPage() {
  const { navigate } = useRouter();
  return (
    <main className="mx-auto w-full max-w-3xl space-y-8 px-6 py-10">
      <section className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">首页</h1>
        <p className="text-muted-foreground">系统状态与快捷入口</p>
      </section>
      <section className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
        <h2 className="mb-3 text-base font-medium">后端服务</h2>
        <HealthStatus />
      </section>
      <section className="flex flex-wrap gap-3">
        <Button onClick={() => navigate("/persons/new")}>新建人物</Button>
        <Button variant="outline" onClick={() => navigate("/persons")}>
          人物列表
        </Button>
        <Button variant="outline" onClick={() => navigate("/interactions/new")}>
          记录互动
        </Button>
        <Button variant="outline" onClick={() => navigate("/interactions")}>
          互动记录
        </Button>
      </section>
    </main>
  );
}
