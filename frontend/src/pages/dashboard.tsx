import { HealthStatus } from "@/components/health/health-status";
import { Button } from "@/components/ui/button";
import { useRouter } from "@/lib/router";
import { useEffect, useState } from "react";
import { getDashboard, weeklyReport, type DashboardData } from "@/api/p2";

export function DashboardPage() {
  const { navigate } = useRouter();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [report, setReport] = useState("");

  useEffect(() => {
    void getDashboard()
      .then(setDashboard)
      .catch(() => undefined);
  }, []);

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
      {dashboard && (
        <section className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {[
            ["人物", dashboard.persons],
            ["互动", dashboard.interactions],
            ["话题", dashboard.topics],
            ["文件", dashboard.documents],
          ].map(([label, value]) => (
            <div key={String(label)} className="rounded-lg border bg-card p-4 text-center">
              <p className="text-2xl font-semibold">{value}</p>
              <p className="text-sm text-muted-foreground">{label}</p>
            </div>
          ))}
        </section>
      )}
      {dashboard && dashboard.due_followups.length > 0 && (
        <section className="space-y-2 rounded-lg border bg-card p-4">
          <h2 className="text-sm font-medium text-muted-foreground">待跟进</h2>
          {dashboard.due_followups.map((item) => (
            <p key={item.id} className="text-sm">
              {item.person_name}：{item.title}
            </p>
          ))}
        </section>
      )}
      {dashboard && dashboard.due_reviews.length > 0 && (
        <section className="space-y-2 rounded-lg border bg-card p-4">
          <h2 className="text-sm font-medium text-muted-foreground">今日复习</h2>
          {dashboard.due_reviews.map((item) => (
            <button
              key={item.id}
              type="button"
              className="block text-sm underline"
              onClick={() => navigate(`/topics/${item.topic_id}`)}
            >
              {item.topic_name}
            </button>
          ))}
        </section>
      )}
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
        <Button
          variant="outline"
          onClick={() =>
            void weeklyReport()
              .then(setReport)
              .catch(() => setReport("周报生成失败（请先配置 AI 提供商）"))
          }
        >
          生成周报
        </Button>
      </section>
      {report && (
        <section className="whitespace-pre-wrap rounded-lg border bg-card p-4 text-sm">{report}</section>
      )}
    </main>
  );
}
