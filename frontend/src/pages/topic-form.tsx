import { useEffect, useState, type FormEvent } from "react";
import { createTopic, getTopic, listCategories, updateTopic } from "@/api/topics";
import type { TopicCategoryNode, TopicInput } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, Field, Select, TextArea, TextInput } from "@/components/ui/field";
import { matchRoute, useRouter } from "@/lib/router";

function flatten(nodes: TopicCategoryNode[], depth = 0): { id: string; name: string; depth: number }[] {
  const result: { id: string; name: string; depth: number }[] = [];
  for (const node of nodes) {
    result.push({ id: node.id, name: `${"　".repeat(depth)}${node.name}`, depth });
    result.push(...flatten(node.children, depth + 1));
  }
  return result;
}

export function TopicFormPage() {
  const { path, navigate } = useRouter();
  const editMatch = matchRoute(path, "/topics/:id/edit");
  const topicId = editMatch?.params.id;
  const isEdit = topicId !== undefined;

  const [name, setName] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [description, setDescription] = useState("");
  const [mastery, setMastery] = useState("1");
  const [categories, setCategories] = useState<TopicCategoryNode[]>([]);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void listCategories()
      .then(setCategories)
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!topicId) {
      return;
    }
    void getTopic(topicId)
      .then((topic) => {
        setName(topic.name);
        setCategoryId(topic.category_id ?? "");
        setDescription(topic.description ?? "");
        setMastery(String(topic.mastery_level));
        setLoading(false);
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "加载失败");
        setLoading(false);
      });
  }, [topicId]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("话题名称不能为空");
      return;
    }
    setSaving(true);
    setError(null);
    const input: TopicInput = {
      name: name.trim(),
      category_id: categoryId || null,
      description: description || null,
      mastery_level: Number(mastery) || 1,
    };
    try {
      const saved = topicId ? await updateTopic(topicId, input) : await createTopic(input);
      navigate(`/topics/${saved.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败");
      setSaving(false);
    }
  };

  return (
    <main className="mx-auto w-full max-w-2xl space-y-6 px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">{isEdit ? "编辑话题" : "新建话题"}</h1>
        <Button variant="ghost" onClick={() => navigate(topicId ? `/topics/${topicId}` : "/topics")}>
          返回
        </Button>
      </div>
      {loading ? (
        <p className="text-muted-foreground">加载中…</p>
      ) : (
        <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
          <Field label="名称 *">
            <TextInput value={name} onChange={(e) => setName(e.target.value)} />
          </Field>
          <Field label="分类">
            <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
              <option value="">无分类</option>
              {flatten(categories).map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="掌握程度（1–6）">
            <TextInput
              type="number"
              min={1}
              max={6}
              value={mastery}
              onChange={(e) => setMastery(e.target.value)}
            />
          </Field>
          <Field label="简介">
            <TextArea value={description} onChange={(e) => setDescription(e.target.value)} />
          </Field>
          <ErrorText message={error} />
          <div className="flex gap-3">
            <Button type="submit" disabled={saving}>
              {saving ? "保存中…" : "保存"}
            </Button>
            <Button type="button" variant="outline" onClick={() => navigate("/topics")}>
              取消
            </Button>
          </div>
        </form>
      )}
    </main>
  );
}
