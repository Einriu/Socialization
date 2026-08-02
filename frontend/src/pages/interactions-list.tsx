import { useCallback, useEffect, useState } from "react";
import { deleteInteraction, listInteractions } from "@/api/interactions";
import { listPersons } from "@/api/persons";
import type { Interaction, Person } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, Select } from "@/components/ui/field";
import { formatDateTime } from "@/lib/datetime";
import { useRouter } from "@/lib/router";

const PAGE_SIZE = 20;

const TYPE_LABELS: Record<string, string> = {
  face_to_face: "面对面聊天",
  phone: "电话",
  wechat: "微信聊天",
  party: "聚会",
  work: "工作交流",
  sports: "一起运动",
  meal: "一起吃饭",
  other: "其他",
};

export function InteractionsListPage() {
  const { navigate } = useRouter();
  const [items, setItems] = useState<Interaction[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [persons, setPersons] = useState<Person[]>([]);
  const [personId, setPersonId] = useState("");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await listInteractions({ page, pageSize: PAGE_SIZE, personId: personId || undefined });
      setItems(data.items);
      setTotal(data.total);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, [page, personId]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    void listPersons({ pageSize: 100 })
      .then((data) => setPersons(data.items))
      .catch(() => undefined);
  }, []);

  const handleDelete = async (item: Interaction) => {
    if (!window.confirm(`确认删除互动「${item.title}」？`)) {
      return;
    }
    try {
      await deleteInteraction(item.id);
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "删除失败");
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <main className="mx-auto w-full max-w-4xl space-y-6 px-6 py-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">互动记录</h1>
          <p className="text-muted-foreground">共 {total} 条</p>
        </div>
        <Button onClick={() => navigate("/interactions/new")}>记录互动</Button>
      </div>

      <Select
        className="w-56"
        value={personId}
        onChange={(e) => {
          setPersonId(e.target.value);
          setPage(1);
        }}
        aria-label="按人物筛选"
      >
        <option value="">全部人物</option>
        {persons.map((p) => (
          <option key={p.id} value={p.id}>
            {p.name}
          </option>
        ))}
      </Select>

      <ErrorText message={error} />

      {items.length === 0 && !error ? (
        <p className="text-muted-foreground">还没有互动记录，点击“记录互动”开始。</p>
      ) : (
        <ul className="space-y-3">
          {items.map((item) => (
            <li key={item.id} className="rounded-lg border bg-card p-4 text-card-foreground shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium">{item.title}</span>
                    <span className="rounded bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">
                      {TYPE_LABELS[item.interaction_type] ?? item.interaction_type}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {formatDateTime(item.occurred_at)}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1 text-xs text-muted-foreground">
                    {item.persons.map((p) => (
                      <span key={p.id} className="rounded border px-1.5 py-0.5">
                        {p.name}
                      </span>
                    ))}
                  </div>
                  {item.summary && <p className="text-sm text-muted-foreground">{item.summary}</p>}
                </div>
                <div className="flex shrink-0 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/interactions/${item.id}/edit`)}
                  >
                    编辑
                  </Button>
                  <Button variant="destructive" size="sm" onClick={() => void handleDelete(item)}>
                    删除
                  </Button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      <div className="flex items-center justify-between">
        <Button variant="outline" disabled={page <= 1} onClick={() => setPage(page - 1)}>
          上一页
        </Button>
        <span className="text-sm text-muted-foreground">
          第 {page} / {totalPages} 页
        </span>
        <Button variant="outline" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
          下一页
        </Button>
      </div>
    </main>
  );
}
