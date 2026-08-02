import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export interface MatchResult {
  params: Record<string, string>;
}

export interface RouterContextValue {
  path: string;
  navigate: (to: string) => void;
}

const RouterContext = createContext<RouterContextValue | null>(null);

function getHashPath(): string {
  const hash = window.location.hash;
  if (!hash || hash === "#") {
    return "/";
  }
  return hash.startsWith("#/") ? hash.slice(1) : "/";
}

export function RouterProvider({ children }: { children: ReactNode }) {
  const [path, setPath] = useState<string>(getHashPath);

  useEffect(() => {
    const onHashChange = () => setPath(getHashPath());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const navigate = useCallback((to: string) => {
    window.location.hash = to;
  }, []);

  return (
    <RouterContext.Provider value={{ path, navigate }}>{children}</RouterContext.Provider>
  );
}

export function useRouter(): RouterContextValue {
  const context = useContext(RouterContext);
  if (!context) {
    throw new Error("useRouter 必须在 RouterProvider 内使用");
  }
  return context;
}

export function matchRoute(path: string, pattern: string): MatchResult | null {
  const pathSegments = path.split("/").filter(Boolean);
  const patternSegments = pattern.split("/").filter(Boolean);
  if (pathSegments.length !== patternSegments.length) {
    return null;
  }
  const params: Record<string, string> = {};
  for (let i = 0; i < patternSegments.length; i++) {
    const segment = patternSegments[i] ?? "";
    if (segment.startsWith(":")) {
      params[segment.slice(1)] = decodeURIComponent(pathSegments[i] ?? "");
    } else if (segment !== pathSegments[i]) {
      return null;
    }
  }
  return { params };
}
