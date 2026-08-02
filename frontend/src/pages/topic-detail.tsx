import { useCallback, useEffect, useRef, useState } from "react";
import { listPersons } from "@/api/persons";
import { listDocuments, setDocumentLinks } from "@/api/documents";
import { deleteTopic, getNote, getTopic, saveNote, setTopicPersons } from "@/api/topics";
import type { DocumentRecord, Person, Topic, TopicNote } from "@/api/types";
import { NoteEditor } from "@/components/editor/note-editor";
import { Button } from "@/components/ui/button";
import { ErrorText, Select } from "@/components/ui/field";
import { matchRoute, useRouter } from "@/lib/router";

export function TopicDetailPage() {
  const { path, navigate } = useRouter();
  const topicId = matchRoute(path, "/topics/:id")?.params.id ?? "";
  const [topic, setTopic] = useState<Topic | null>(null);
  const [note, setNote] = useState<TopicNote | null>(null);
  const [persons, setPersons] = useState<Person[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [allDocuments, setAllDocuments] = useState<DocumentRecord[]>([]);
  const [linkDocId, setLinkDocId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState("已就绪");
  const savingRef = useRef(false);

  const load = useCallback(async () => {
    try {
      const [t, n, p, docs, allDocs] = await Promise.all([
        getTopic(topicId),
        getNote(topicId),
        listPersons({ pageSize: 100 }),
        listDocuments({ topicId, pageSize: 50 }),
        listDocuments({ pageSize: 100 }),
      ]);
      setTopic(t);
      setNote(n);
      setPersons(p.items);
      setDocuments(docs.items);
      setAllDocuments(allDocs.items);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, [topicId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!topic) {
    return (
      <main className="mx-auto w-full max-w-4xl px-6 py-10">
        <ErrorText message={error} />
        {!error && <p className="text-muted-foreground">加载中…</p>}
      </main>
    );
  }

  const handleSave = async (json: object, plainText: string) => {
    if (savingRef.current) {
      return;
    }
    savingRef.current = true;
    setSaveStatus("保存中…");
    try {
      const saved = await saveNote(topicId, {
        content_json: json,
        plain_text: plainText,
        expected_updated_at: note?.updated_at ?? null,
      });
      setNote(saved);
      setSaveStatus(`已保存 ${new Date().toLocaleTimeString("zh-CN")}`);
    } catch (e) {
      if (e instanceof Error && e.message.includes("409")) {
        setSaveStatus("保存冲突，已刷新，请重试");
      } else {
        setSaveStatus("保存失败");
      }
      void load();
    } finally {
      savingRef.current = false;
    }
  };

  const togglePerson = async (personId: string, checked: boolean) => {
    const current = new Set(topic.persons.map((p) => p.id));
    if (checked) {
      current.add(personId);
    } else {
      current.delete(personId);
    }
    try {
      await setTopicPersons(topicId, [...current]);
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "更新关联失败");
    }
  };

  const linkDocument = async (documentId: string) => {
    try {
      await setDocumentLinks(documentId, { topic_id: topicId });
      setLinkDocId("");
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "关联文件失败");
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`确认删除话题「${topic.name}」？`)) {
      return;
    }
    await deleteTopic(topicId);
    navigate("/topics");
  };

  return (
    <main className="mx-auto w-full max-w-4xl space-y-6 px-6 py-10">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{topic.name}</h1>
          <p className="text-muted-foreground">掌握度 {topic.mastery_level}/6</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(`/topics/${topic.id}/edit`)}>
            编辑
          </Button>
          <Button variant="destructive" onClick={() => void handleDelete()}>
            删除
          </Button>
          <Button variant="ghost" onClick={() => navigate("/topics")}>
            返回
          </Button>
        </div>
      </div>

      {topic.description && <p className="rounded-lg border bg-card p-4 text-sm">{topic.description}</p>}

      <section className="space-y-2">
        <h2 className="text-sm font-medium text-muted-foreground">关联人物</h2>
        <div className="flex flex-wrap gap-2">
          {persons.map((person) => {
            const checked = topic.persons.some((p) => p.id === person.id);
            return (
              <label key={person.id} className="flex cursor-pointer items-center gap-1.5 rounded border px-2.5 py-1 text-sm">
                <input type="checkbox" checked={checked} onChange={(e) => void togglePerson(person.id, e.target.checked)} />
                {person.name}
              </label>
            );
          })}
        </div>
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-medium text-muted-foreground">关联文件</h2>
        <div className="flex flex-wrap gap-2">
          {documents.map((document) => (
            <span key={document.id} className="rounded border px-2.5 py-1 text-sm">
              {document.filename}
            </span>
          ))}
          {documents.length === 0 && (
            <span className="text-sm text-muted-foreground">未关联文件</span>
          )}
        </div>
        <div className="flex gap-2">
          <Select className="w-56" value={linkDocId} onChange={(e) => setLinkDocId(e.target.value)}>
            <option value="">选择文件关联</option>
            {allDocuments
              .filter((document) => document.status === "completed")
              .map((document) => (
                <option key={document.id} value={document.id}>
                  {document.filename}
                </option>
              ))}
          </Select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (linkDocId) {
                void linkDocument(linkDocId);
              }
            }}
          >
            关联
          </Button>
        </div>
      </section>

      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium">笔记</h2>
          <span className="text-xs text-muted-foreground">{saveStatus}</span>
        </div>
        <NoteEditor initialJson={note?.content_json ?? null} onSave={(json, text) => void handleSave(json, text)} />
      </section>
      <ErrorText message={error} />
    </main>
  );
}
