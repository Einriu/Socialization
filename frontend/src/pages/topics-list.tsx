import { useCallback, useEffect, useState, type FormEvent } from "react";
import { createCategory, deleteCategory, listCategories, listTopics } from "@/api/topics";
import type { Topic, TopicCategoryNode } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, TextInput } from "@/components/ui/field";
import { useRouter } from "@/lib/router";

export function TopicsListPage() {
  const { navigate } = useRouter();
  const [categories, setCategories] = useState<TopicCategoryNode[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [total, setTotal] = useState(0);
  const [categoryId, setCategoryId] = useState("");
  const [q, setQ] = useState("");
  const [newCategory, setNewCategory] = useState("");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [tree, data] = await Promise.all([
        listCategories(),
        listTopics({ page: 1, pageSize: 100, categoryId: categoryId || undefined, q: q || undefined }),
      ]);
      setCategories(tree);
      setTopics(data.items);
      setTotal(data.total);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, [categoryId, q]);

  useEffect(() => {
    void load();
  }, [load]);

  const addCategory = async (e: FormEvent) => {
    e.preventDefault();
    if (!newCategory.trim()) {
      return;
    }
    try {
      await createCategory({ name: newCategory.trim() });
      setNewCategory("");
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "创建分类失败");
    }
  };

  const removeCategory = async (node: TopicCategoryNode) => {
    if (!window.confirm(`确认删除分类「${node.name}」？`)) {
      return;
    }
    try {
      await deleteCategory(node.id);
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "删除分类失败");
    }
  };

  const renderTree = (nodes: TopicCategoryNode[], depth: number) =>
    nodes.map((node) => (
      <li key={node.id}>
        <div className="flex items-center justify-between gap-2 py-0.5" style={{ paddingLeft: depth * 14 }}>
          <button
            type="button"
            className={`text-sm ${categoryId === node.id ? "font-medium text-foreground" : "text-muted-foreground hover:text-foreground"}`}
            onClick={() => setCategoryId(node.id === categoryId ? "" : node.id)}
          >
            {node.name}
          </button>
          <Button variant="ghost" size="sm" onClick={() => void removeCategory(node)}>
            删
          </Button>
        </div>
        {node.children.length > 0 && <ul>{renderTree(node.children, depth + 1)}</ul>}
      </li>
    ));

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6 px-6 py-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">话题知识库</h1>
          <p className="text-muted-foreground">共 {total} 个话题</p>
        </div>
        <Button onClick={() => navigate("/topics/new")}>新建话题</Button>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-[220px_1fr]">
        <aside className="space-y-3 rounded-lg border bg-card p-4">
          <h2 className="text-sm font-medium">分类</h2>
          <button
            type="button"
            className={`text-sm ${!categoryId ? "font-medium" : "text-muted-foreground"}`}
            onClick={() => setCategoryId("")}
          >
            全部
          </button>
          <ul>{renderTree(categories, 0)}</ul>
          <form onSubmit={(e) => void addCategory(e)} className="flex gap-2 pt-2">
            <TextInput
              placeholder="新分类名"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
            />
            <Button type="submit" variant="outline" size="sm">
              添加
            </Button>
          </form>
        </aside>

        <section className="space-y-3">
          <div className="flex gap-2">
            <TextInput
              placeholder="搜索话题"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
          <ErrorText message={error} />
          <ul className="space-y-2">
            {topics.map((topic) => (
              <li key={topic.id}>
                <button
                  type="button"
                  onClick={() => navigate(`/topics/${topic.id}`)}
                  className="w-full rounded-lg border bg-card p-4 text-left text-card-foreground shadow-sm hover:bg-accent"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{topic.name}</span>
                    <span className="text-xs text-muted-foreground">掌握度 {topic.mastery_level}/6</span>
                  </div>
                  {topic.description && (
                    <p className="mt-1 text-sm text-muted-foreground line-clamp-1">{topic.description}</p>
                  )}
                </button>
              </li>
            ))}
            {topics.length === 0 && <li className="text-sm text-muted-foreground">暂无话题</li>}
          </ul>
        </section>
      </div>
    </main>
  );
}
