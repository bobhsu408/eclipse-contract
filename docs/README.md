# 🌑 Eclipse Contract (蝕界契約)

> **"為了還債，我只好召喚死靈去打工。"**

一款結合 **橫向捲軸動作** 與 **商店經營** 的 2D 像素遊戲。

![Version](https://img.shields.io/badge/version-Alpha%200.2-purple)
![Python](https://img.shields.io/badge/python-3.14-blue)
![Pygame](https://img.shields.io/badge/pygame--ce-2.5.6-green)

---

## 📖 遊戲簡介

你是 **艾莉絲·諾克斯**，一位負債累累的死靈術士。

因為教會禁令，你的魔法道具店被迫關閉。現在你欠暗影銀行 **13,310 金幣**，必須在 7 天內還清第一期款項，否則你的靈魂將成為抵押品。

**你的計劃：**

- 🌙 **晚上** - 潛入荒野，召喚死靈收集素材
- ☀️ **白天** - 回到店裡，將素材加工成商品賣出
- 💰 **還債** - 用賺來的錢還給銀行

但要小心：

- ⚔️ 教會巡邏隊會搜捕死靈術士
- 😈 惡魔商人想拉攏你加入黑市
- 🤝 冒險者公會對你的行為睜一隻眼閉一隻眼（只要你提供便宜貨）

---

## ✨ 核心特色

### 🎮 遊戲玩法

- **2.5D 橫向捲軸** - 探索迷霧森林、廢棄墓地、魔法廢墟
- **召喚系統** - 召喚不同類型的死靈幫你戰鬥和收集
- **AI 行為** - 6 種可配置的 AI（跟隨、守衛、巡邏、攻擊、逃跑、遊蕩）
- **經營循環** - 打怪 → 賺錢 → 強化 → 打更強的怪

### 🎨 視覺風格

- **像素藝術** - 復古的 2D 像素風格
- **死靈美學** - 紫色魔法、靈魂連線、粒子特效
- **動態相機** - 跟隨玩家的智能相機系統

### 🧙 召喚系統

- **食屍鬼** - 廉價勞工，死了不心疼
- **小惡魔** - 飛行單位，主動攻擊（開發中）
- **骷髏戰士** - 固定守衛，防禦力強（開發中）

---

## 🚀 快速開始

### 環境需求

- Python 3.10+
- Pygame-ce 2.5.6+

### 安裝步驟

1. **克隆倉庫**

```bash
git clone https://github.com/你的用戶名/eclipse-contract.git
cd eclipse-contract
```

2. **創建虛擬環境**

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

3. **安裝依賴**

```bash
pip install pygame-ce
```

4. **運行遊戲**

```bash
python main.py
```

---

## 🎯 開發進度

### ✅ 已完成

- [x] 2.5D 物理引擎（重力、摩擦力、碰撞）
- [x] 玩家控制（WASD 移動、Space 跳躍）
- [x] 智能相機系統（跟隨、邊界限制）
- [x] 召喚系統（按鍵召喚、魔法粒子效果）
- [x] AI 行為系統（6 種可配置行為）
- [x] 粒子特效系統
- [x] 靈魂連線視覺效果
- [x] 角色編輯器工具
- [x] 主選單 GUI

### 🔜 開發中

- [ ] 敵人系統
- [ ] 戰鬥系統（傷害計算、生命值）
- [ ] 商店經營系統
- [ ] 陣營好感度系統
- [ ] 關卡設計（Tiled 地圖）
- [ ] 音效與音樂

---

## 📁 專案結構

```
商店經營/
├── main.py              # 遊戲主循環
├── menu.py              # 主選單系統
├── settings.py          # 全局設定
├── physics.py           # 2.5D 物理引擎
├── camera.py            # 相機系統
├── sprites.py           # 玩家與單位類別
├── ai.py                # AI 行為系統
├── particles.py         # 粒子特效
│
├── assets/              # 遊戲資源
│   ├── player.png
│   └── ghoul.png
│
├── data/                # 遊戲數據
│   └── example_unit.json
│
├── tools/               # 開發工具
│   ├── character_editor.py
│   └── sprite_exporter.py
│
├── GAME_DESIGN.md       # 遊戲設計文件
└── STORY.md             # 故事設定
```

---

## 🛠️ 開發工具

### 角色編輯器

```bash
python tools/character_editor.py
```

功能：

- 選擇角色圖片
- 調整屬性（Scale、Speed、HP）
- 配置 AI 行為（支援搜尋和滾動）
- 導出 JSON 配置

---

## 🎮 操作說明

### 遊戲內

- `WASD` / `方向鍵` - 移動
- `Space` - 跳躍
- `1` - 召喚食屍鬼（消耗 10 靈魂）

### 開發模式

- `ESC` - 返回主選單（開發中）

---

## 📚 技術文檔

- [遊戲設計文件](GAME_DESIGN.md) - 完整的開發企劃
- [故事設定](STORY.md) - 角色與劇情背景

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

---

## 📝 授權

MIT License

---

## 👥 開發團隊

- **遊戲設計 & 程式** - 你的名字
- **故事設定** - 你的名字

---

## 🔗 相關連結

- [Pygame-ce 文檔](https://pyga.me/)
- [Tiled Map Editor](https://www.mapeditor.org/)

---

**最後更新：** 2025-11-23  
**當前版本：** Alpha 0.2  
**開發狀態：** 原型階段
