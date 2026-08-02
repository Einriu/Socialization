import type { ReactNode } from "react";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/lib/theme";
import { matchRoute, useRouter } from "@/lib/router";
import { DashboardPage } from "@/pages/dashboard";
import { InteractionsListPage } from "@/pages/interactions-list";
import { InteractionFormPage } from "@/pages/interaction-form";
import { PersonDetailPage } from "@/pages/person-detail";
import { PersonFormPage } from "@/pages/person-form";
import { PersonsListPage } from "@/pages/persons-list";

const NAV_ITEMS = [
  { path: "/", label: "首页" },
  { path: "/persons", label: "人物" },
  { path: "/interactions", label: "互动记录" },
];

export default function App() {
  const { theme, toggleTheme } = useTheme();
  const { path } = useRouter();

  let page: ReactNode;
  if (path === "/") {
    page = <DashboardPage />;
  } else if (path === "/persons") {
    page = <PersonsListPage />;
  } else if (matchRoute(path, "/persons/new") !== null) {
    page = <PersonFormPage />;
  } else if (matchRoute(path, "/persons/:id/edit") !== null) {
    page = <PersonFormPage />;
  } else if (matchRoute(path, "/persons/:id") !== null) {
    page = <PersonDetailPage />;
  } else if (path === "/interactions") {
    page = <InteractionsListPage />;
  } else if (matchRoute(path, "/interactions/new") !== null) {
    page = <InteractionFormPage />;
  } else if (matchRoute(path, "/interactions/:id/edit") !== null) {
    page = <InteractionFormPage />;
  } else {
    page = <DashboardPage />;
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b">
        <div className="mx-auto flex h-14 w-full max-w-4xl items-center justify-between px-6">
          <nav className="flex items-center gap-1">
            {NAV_ITEMS.map((item) => {
              const active = path === item.path || path.startsWith(`${item.path}/`);
              return (
                <a
                  key={item.path}
                  href={`#${item.path}`}
                  className={`rounded-md px-3 py-1.5 text-sm ${
                    active
                      ? "bg-secondary font-medium text-secondary-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {item.label}
                </a>
              );
            })}
          </nav>
          <span className="font-medium">Socialization</span>
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="切换主题">
            {theme === "dark" ? <Sun /> : <Moon />}
          </Button>
        </div>
      </header>
      {page}
    </div>
  );
}
