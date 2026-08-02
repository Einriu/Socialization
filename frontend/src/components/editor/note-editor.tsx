import { useCallback, useEffect, useRef } from "react";
import Placeholder from "@tiptap/extension-placeholder";
import Highlight from "@tiptap/extension-highlight";
import Image from "@tiptap/extension-image";
import { Table } from "@tiptap/extension-table";
import TableCell from "@tiptap/extension-table-cell";
import TableHeader from "@tiptap/extension-table-header";
import TableRow from "@tiptap/extension-table-row";
import TaskItem from "@tiptap/extension-task-item";
import TaskList from "@tiptap/extension-task-list";
import { EditorContent, useEditor, type Editor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { Button } from "@/components/ui/button";

interface NoteEditorProps {
  initialJson: object | null;
  onSave: (json: object, plainText: string) => void;
  saveStatus: string;
}

const AUTOSAVE_DELAY_MS = 1500;

export function NoteEditor({ initialJson, onSave, saveStatus }: NoteEditorProps) {
  const onSaveRef = useRef(onSave);
  onSaveRef.current = onSave;
  const saveTimer = useRef<number | null>(null);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
      }),
      Placeholder.configure({
        placeholder: "开始写笔记…支持 Markdown 快捷输入（# 标题、- 列表、> 引用、` 代码）",
      }),
      Highlight,
      Image.configure({ allowBase64: true }),
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      TaskList,
      TaskItem.configure({ nested: true }),
    ],
    content: initialJson ?? { type: "doc", content: [] },
  });

  const flushNow = useCallback(
    (target: Editor | null = editor) => {
      if (target) {
        if (saveTimer.current !== null) {
          window.clearTimeout(saveTimer.current);
          saveTimer.current = null;
        }
        onSaveRef.current(target.getJSON(), target.getText());
      }
    },
    [editor],
  );

  useEffect(() => {
    if (!editor) {
      return;
    }
    const handleUpdate = () => {
      if (saveTimer.current !== null) {
        window.clearTimeout(saveTimer.current);
      }
      saveTimer.current = window.setTimeout(() => {
        onSaveRef.current(editor.getJSON(), editor.getText());
      }, AUTOSAVE_DELAY_MS);
    };
    const handleKeydown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        flushNow(editor);
      }
    };
    editor.on("update", handleUpdate);
    editor.view.dom.addEventListener("keydown", handleKeydown);
    return () => {
      editor.off("update", handleUpdate);
      editor.view.dom.removeEventListener("keydown", handleKeydown);
      if (saveTimer.current !== null) {
        window.clearTimeout(saveTimer.current);
      }
    };
  }, [editor, flushNow]);

  useEffect(() => {
    const onBeforeUnload = () => {
      if (saveTimer.current !== null && editor) {
        window.clearTimeout(saveTimer.current);
        saveTimer.current = null;
        onSaveRef.current(editor.getJSON(), editor.getText());
      }
    };
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [editor]);

  if (!editor) {
    return <p className="text-muted-foreground">编辑器加载中…</p>;
  }

  const insertLocalImage = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") {
        editor.chain().focus().setImage({ src: reader.result }).run();
      }
    };
    reader.readAsDataURL(file);
  };

  const toggle = (fn: (chain: ReturnType<Editor["chain"]>) => void) => {
    fn(editor.chain().focus());
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-1 rounded-lg border bg-card p-2">
        <ToolButton active={editor.isActive("heading", { level: 1 })} onClick={() => toggle((c) => c.toggleHeading({ level: 1 }))}>
          H1
        </ToolButton>
        <ToolButton active={editor.isActive("heading", { level: 2 })} onClick={() => toggle((c) => c.toggleHeading({ level: 2 }))}>
          H2
        </ToolButton>
        <ToolButton active={editor.isActive("heading", { level: 3 })} onClick={() => toggle((c) => c.toggleHeading({ level: 3 }))}>
          H3
        </ToolButton>
        <Separator />
        <ToolButton active={editor.isActive("bold")} onClick={() => toggle((c) => c.toggleBold())}>
          加粗
        </ToolButton>
        <ToolButton active={editor.isActive("italic")} onClick={() => toggle((c) => c.toggleItalic())}>
          斜体
        </ToolButton>
        <ToolButton active={editor.isActive("highlight")} onClick={() => toggle((c) => c.toggleHighlight())}>
          高亮
        </ToolButton>
        <ToolButton active={editor.isActive("code")} onClick={() => toggle((c) => c.toggleCode())}>
          行内代码
        </ToolButton>
        <Separator />
        <ToolButton active={editor.isActive("bulletList")} onClick={() => toggle((c) => c.toggleBulletList())}>
          列表
        </ToolButton>
        <ToolButton active={editor.isActive("orderedList")} onClick={() => toggle((c) => c.toggleOrderedList())}>
          编号
        </ToolButton>
        <ToolButton active={editor.isActive("taskList")} onClick={() => toggle((c) => c.toggleTaskList())}>
          待办
        </ToolButton>
        <ToolButton active={editor.isActive("blockquote")} onClick={() => toggle((c) => c.toggleBlockquote())}>
          引用
        </ToolButton>
        <ToolButton active={editor.isActive("codeBlock")} onClick={() => toggle((c) => c.toggleCodeBlock())}>
          代码块
        </ToolButton>
        <Separator />
        <ToolButton
          onClick={() => {
            toggle((c) => c.insertTable({ rows: 3, cols: 3, withHeaderRow: true }));
          }}
        >
          表格
        </ToolButton>
        <label className="cursor-pointer rounded px-2 py-1 text-sm text-muted-foreground hover:text-foreground">
          图片
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                insertLocalImage(file);
              }
              e.target.value = "";
            }}
          />
        </label>
        <Separator />
        <Button variant="ghost" size="sm" onClick={() => toggle((c) => c.undo())}>
          撤销
        </Button>
        <Button variant="ghost" size="sm" onClick={() => toggle((c) => c.redo())}>
          重做
        </Button>
        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-muted-foreground">
            {editor.getText().length} 字
          </span>
          <span className="text-xs text-muted-foreground">{saveStatus}</span>
          <Button size="sm" onClick={() => flushNow()}>
            保存
          </Button>
        </div>
      </div>
      <div className="min-h-96 rounded-lg border bg-card p-5 focus-within:ring-2 focus-within:ring-ring">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
}

function ToolButton({
  active,
  onClick,
  children,
}: {
  active?: boolean;
  onClick: () => void;
  children: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded px-2 py-1 text-sm ${
        active ? "bg-secondary font-medium text-secondary-foreground" : "text-muted-foreground hover:text-foreground"
      }`}
    >
      {children}
    </button>
  );
}

function Separator() {
  return <span className="mx-1 h-5 w-px bg-border" aria-hidden />;
}
