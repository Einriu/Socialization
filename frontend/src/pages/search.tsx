import { useState, type FormEvent } from "react";
import { searchAll } from "@/api/search";
import type { SearchResult } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, TextInput } from "@/components/ui/field";
import { useRouter } from "@/lib/router";

export function SearchPage() {
  const { navigate } = useRouter();
  const [q, setQ] = useState("");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async (e: FormEvent) => {
    e.preventDefault();
    if (!q.trim()) {
      return;
    }
    try {
      setResult(await searchAll(q.trim()));
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "搜索失败");
    }
  };

  return (
    <main className="mx-auto w-full max-w-3xl space-y-6 px-6 py-10">
      <h1 className="text-2xl font-semibold tracking-tight">全局搜索</h1>
      <form onSubmit={(e) => void run(e)} className="flex gap-2">
        <TextInput placeholder="搜索人物 / 话题 / 互动 / 笔记 / 文件" value={q} onChange={(e) => setQ(e.target.value)} />
        <Button type="submit">搜索</Button>
      </form>
      <ErrorText message={error} />
      {result && (
        <div className="space-y-4">
          <Group title={`人物（${result.persons.length}）`}>
            {result.persons.map((item) => (
              <Item key={item.id} onClick={() => navigate(`/persons/${item.id}`)}>
                {item.name}
              </Item>
            ))}
          </Group>
          <Group title={`话题（${result.topics.length}）`}>
            {result.topics.map((item) => (
              <Item key={item.id} onClick={() => navigate(`/topics/${item.id}`)}>
                {item.name}
              </Item>
            ))}
          </Group>
          <Group title={`互动（${result.interactions.length}）`}>
            {result.interactions.map((item) => (
              <Item key={item.id} onClick={() => navigate(`/interactions/${item.id}/edit`)}>
                {item.title}
              </Item>
            ))}
          </Group>
          <Group title={`笔记（${result.notes.length}）`}>
            {result.notes.map((item) => (
              <Item key={item.id} onClick={() => navigate(`/topics/${item.id}`)}>
                {item.name}
              </Item>
            ))}
          </Group>
          <Group title={`文件片段（${result.documents.length}）`}>
            {result.documents.map((item) => (
              <Item key={item.id}>文件片段 #{String(item.id).slice(0, 8)}</Item>
            ))}
          </Group>
        </div>
      )}
    </main>
  );
}

function Group({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h2 className="text-sm font-medium text-muted-foreground">{title}</h2>
      {children}
    </section>
  );
}

function Item({ children, onClick }: { children: React.ReactNode; onClick?: () => void }) {
  if (!onClick) {
    return <p className="rounded border bg-card px-3 py-2 text-sm">{children}</p>;
  }
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded border bg-card px-3 py-2 text-left text-sm hover:bg-accent"
    >
      {children}
    </button>
  );
}
