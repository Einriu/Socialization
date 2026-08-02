export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export class ApiError extends Error {
  code: number | string;
  status: number;

  constructor(message: string, code: number | string, status: number) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (response.status === 204) {
    return undefined as T;
  }
  let body: ApiResponse<T>;
  try {
    body = (await response.json()) as ApiResponse<T>;
  } catch {
    throw new ApiError(`请求失败：HTTP ${response.status}`, String(response.status), response.status);
  }
  if (!response.ok || body.code !== 0) {
    throw new ApiError(body.message || `请求失败：HTTP ${response.status}`, body.code, response.status);
  }
  return body.data;
}
