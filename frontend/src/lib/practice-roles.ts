export interface DetectedRole {
  name: string;
  role?: string;
}

const NAME_STOPWORDS = new Set([
  "对方", "朋友", "同事", "同学", "家人", "客户", "领导", "上级", "陌生人",
  "长辈", "晚辈", "新人", "自己", "彼此", "大家", "我们", "你们", "他们",
  "场景", "背景", "气氛", "氛围", "状态", "情绪", "话题", "冲突", "机会",
  "现场", "关系", "印象", "开场", "破冰", "我", "你", "他", "她",
  "现在", "时候", "事情", "问题", "感受", "心情", "故事", "反应",
  "角色", "背景故事",
]);

function isValidName(name: string): boolean {
  if (NAME_STOPWORDS.has(name)) {
    return false;
  }
  const han = (name.match(/[\u4e00-\u9fa5]/g) ?? []).length;
  const latin = (name.match(/[A-Za-z]/g) ?? []).length;
  const total = han + latin;
  return total >= 2 && total <= 8;
}

/**
 * 从场景背景文字与对话内容中自动识别角色名（含括号内的角色说明）。
 * 按出现次数排序，次数相同按首次出现顺序。
 */
export function extractRoleNames(text: string): DetectedRole[] {
  const found = new Map<string, DetectedRole & { count: number }>();
  const add = (raw: string, role?: string) => {
    const name = raw.trim().replace(/^[和与跟及同但而]/u, "");
    if (!isValidName(name)) {
      return;
    }
    const existing = found.get(name);
    if (existing) {
      existing.count += 1;
      if (!existing.role && role) {
        existing.role = role.trim() || undefined;
      }
      return;
    }
    found.set(name, { name, role: role?.trim() || undefined, count: 1 });
  };
  const patterns = [
    /【([^】]{1,8})】/g,
    /([\u4e00-\u9fa5]{2,4})（([^）]{1,20})）/g,
    /([A-Za-z][A-Za-z ]{1,10})（([^）]{1,20})）/g,
    /“([\u4e00-\u9fa5]{2,4})”/g,
    /"([\u4e00-\u9fa5]{2,4})"/g,
    /「([\u4e00-\u9fa5]{2,4})」/g,
    /([\u4e00-\u9fa5]{2,4})说(?:道)?[：:]/g,
    /([A-Za-z][A-Za-z ]{1,10})说(?:道)?[：:]/g,
  ];
  for (const pattern of patterns) {
    for (const match of text.matchAll(pattern)) {
      add(match[1] ?? "", match[2]);
    }
  }
  // 结构化背景中的【角色】小节：- 角色名：描述
  const rolesSection = text.match(/【角色】([\s\S]*?)(?=【|$)/)?.[1] ?? "";
  const bulletPattern = /(?:^|\n)[ \t]*[-•·][ \t]*([^：:（【】]{1,10})[：:]/g;
  for (const match of rolesSection.matchAll(bulletPattern)) {
    add(match[1] ?? "", undefined);
  }
  return [...found.values()]
    .sort((a, b) => b.count - a.count)
    .map(({ name, role }) => ({ name, role }));
}
