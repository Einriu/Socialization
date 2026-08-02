import { useCallback, useEffect, useState } from "react";
import { deletePerson, listPersons } from "@/api/persons";
import { listTags } from "@/api/tags";
import type { Person, Tag } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, Select, TextInput } from "@/components/ui/field";
import { useRouter } from "@/lib/router";

const PAGE_SIZE = 20;

export function PersonsListPage() {
  const { navigate } = useRouter();
  const [persons, setPersons] = useState<Person[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [q, setQ] = useState("");
  const [tags, setTags] = useState<Tag[]>([]);
  const [tagId, setTagId] = useState("");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await listPersons({ page, pageSize: PAGE_SIZE, q: q || undefined, tagId: tagId || undefined });
      setPersons(data.items);
      setTotal(data.total);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, [page, q, tagId]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    void listTags()
      .then((data) => setTags(data.items))
      .catch(() => undefined);
  }, []);

  const handleSearch = () => {
    setPage(1);
    setQ(searchInput.trim());
  };

  const handleTagFilter = (value: string) => {
    setTagId(value);
    setPage(1);
  };

  const handleDelete = async (person: Person) => {
    if (!window.confirm(`确认删除「${person.name}」？（软删除，可在数据库中彻底删除）`)) {
      return;
    }
    try {
      await deletePerson(person.id);
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
          <h1 className="text-2xl font-semibold tracking-tight">人物</h1>
          <p className="text-muted-foreground">共 {total} 人</p>
        </div>
        <Button onClick={() => navigate("/persons/new")}>新建人物</Button>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div className="min-w-52 flex-1">
          <TextInput
            placeholder="搜索姓名 / 昵称 / 公司 / 职业"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleSearch();
              }
            }}
          />
        </div>
        <Button variant="outline" onClick={handleSearch}>
          搜索
        </Button>
        <Select
          className="w-44"
          value={tagId}
          onChange={(e) => handleTagFilter(e.target.value)}
          aria-label="按标签筛选"
        >
          <option value="">全部标签</option>
          {tags.map((tag) => (
            <option key={tag.id} value={tag.id}>
              {tag.name}
            </option>
          ))}
        </Select>
      </div>

      <ErrorText message={error} />

      {persons.length === 0 && !error ? (
        <p className="text-muted-foreground">还没有人物，点击“新建人物”开始记录。</p>
      ) : (
        <ul className="space-y-3">
          {persons.map((person) => (
            <li
              key={person.id}
              className="rounded-lg border bg-card p-4 text-card-foreground shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium">{person.name}</span>
                    {person.nickname ? (
                      <span className="text-sm text-muted-foreground">({person.nickname})</span>
                    ) : null}
                    {person.relationship_type ? (
                      <span className="rounded bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">
                        {person.relationship_type}
                      </span>
                    ) : null}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {person.tags.map((tag) => (
                      <span
                        key={tag.id}
                        className="rounded border px-2 py-0.5 text-xs"
                        style={tag.color ? { borderColor: tag.color, color: tag.color } : undefined}
                      >
                        {tag.name}
                      </span>
                    ))}
                  </div>
                  {(person.organization || person.occupation || person.location) && (
                    <p className="text-sm text-muted-foreground">
                      {[person.organization, person.occupation, person.location]
                        .filter(Boolean)
                        .join(" · ")}
                    </p>
                  )}
                </div>
                <div className="flex shrink-0 gap-2">
                  <Button variant="outline" size="sm" onClick={() => navigate(`/persons/${person.id}`)}>
                    详情
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => navigate(`/persons/${person.id}/edit`)}>
                    编辑
                  </Button>
                  <Button variant="destructive" size="sm" onClick={() => void handleDelete(person)}>
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
