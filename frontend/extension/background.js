// Socialization 网页收藏扩展（MV3）
// 点击扩展图标：抓取当前标签页标题与正文文本，POST 到本地应用。
// 使用方式：Chrome/Edge 扩展管理 → 开发者模式 → 加载已解压的扩展程序 → 选择本目录。
// 注意：后端需运行在 127.0.0.1:8000，且 CORS 允许本地来源（默认仅 3000，需在 .env
// 的 CORS_ORIGINS 中加入 chrome-extension://<你的扩展ID> 或临时允许）。

const API_BASE = "http://127.0.0.1:8000";

async function getPageContent(tabId) {
  const result = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      const text = document.body ? document.body.innerText : "";
      return { title: document.title, text: text.slice(0, 200000) };
    },
  });
  return result && result[0] ? result[0].result : { title: "", text: "" };
}

async function clipPage(tab) {
  try {
    const { title, text } = await getPageContent(tab.id);
    if (!text || !text.trim()) {
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icons/icon.png",
        title: "Socialization",
        message: "当前页面没有可收藏的文字",
      });
      return;
    }
    const response = await fetch(`${API_BASE}/api/web-clips`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: tab.url, title: title || tab.title }),
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon.png",
      title: "Socialization",
      message: `已收藏：${title || tab.url}`,
    });
  } catch (error) {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon.png",
      title: "Socialization",
      message: `收藏失败：${error.message}（请确认本地应用已启动）`,
    });
  }
}

chrome.action.onClicked.addListener((tab) => {
  void clipPage(tab);
});
