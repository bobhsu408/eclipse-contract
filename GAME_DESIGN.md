# 《蝕界契約》(Eclipse Contract) - Pygame 開發企劃書

**版本：** 3.0 (Pygame 專用版)  
**開發引擎：** Python 3.14 + Pygame-ce  
**核心類型：** 2D 橫向捲軸動作 x 商店經營 (Side-Scrolling Action x Shop Simulation)

---

## 1. 遊戲概述與目標 (Overview)

### 1.1 核心體驗 (The Hook)

> 「為了還債，我只好召喚死靈去打工。」

結合了 **《泰拉瑞亞》** 的橫向戰鬥與 **《Moonlighter》** 的經營循環。玩家在白天是黑心魔法店長，晚上是壓榨召喚物的死靈慣老闆。

### 1.2 視覺風格

- **美術：** 像素藝術 (Pixel Art)。建議使用 32x32 或 64x64 像素的單位。
- **視角：** 側面視角 (Side-View)，具備平台跳躍元素。
- **解析度：** 原生解析度建議 640x360 (16:9)，放大 2-3 倍顯示以呈現復古感。

---

## 2. 開發架構與技術規格 (Technical Architecture)

### 2.1 技術棧 (Tech Stack)

| 組件     | 技術                          |
| -------- | ----------------------------- |
| 核心語言 | Python 3.14+                  |
| 圖形庫   | pygame-ce (Community Edition) |
| 地圖編輯 | Tiled Map Editor (.tmx 格式)  |
| 地圖載入 | pytmx 庫                      |
| UI 系統  | 自訂 UI 類別                  |
| 數據存儲 | JSON (物品、敵人、存檔)       |

### 2.2 當前專案結構 (Current Project Structure)

```
商店經營/
├── main.py                # ✅ 遊戲主循環
├── settings.py            # ✅ 全局設定 (螢幕、世界、顏色)
├── physics.py             # ✅ 2.5D 物理引擎
├── camera.py              # ✅ 鏡頭跟隨系統
├── sprites.py             # ✅ Player & Unit 類別
├── ai.py                  # ✅ AI 行為系統
├── particles.py           # ✅ 粒子特效系統
│
├── assets/                # 資源文件
│   ├── player.png         # ✅ 玩家圖片
│   └── ghoul.png          # ✅ 食屍鬼圖片
│
├── data/                  # 數據文件
│   ├── units.json         # 🔜 單位數值表
│   ├── items.json         # 🔜 商店物品表
│   └── savegame.json      # 🔜 玩家進度
│
├── tools/                 # 開發工具
│   ├── character_editor.py  # ✅ 角色編輯器
│   └── sprite_exporter.py   # ✅ 精靈圖導出工具
│
└── venv/                  # Python 虛擬環境
```

### 2.3 建議新增的結構

```
商店經營/
└── src/                   # 🔜 模組化原始碼
    ├── __init__.py
    ├── game_state.py      # 🔜 狀態機 (Menu, Shop, Dungeon)
    ├── entities/          # 🔜 實體類
    │   └── enemy.py       # 🔜 敵人類別
    ├── systems/           # 🔜 系統
    │   ├── summoning.py   # 🔜 召喚邏輯
    │   ├── shop_system.py # 🔜 經營邏輯
    │   └── faction.py     # 🔜 陣營好感度
    └── ui/                # 🔜 介面繪製
        ├── hud.py
        └── shop_ui.py
```

---

## 3. 遊戲核心循環 (The Game Loop)

遊戲分為三個主要狀態：

### 3.1 狀態一：魔法小店 (State_Shop)

**視角：** 固定畫面 (類似 RPG 店舖內視圖)

**功能：**

- **櫃台 (Counter)：** 處理訂單，將素材賣給不同陣營（影響好感度）
- **工作台 (Workbench)：** 消耗「靈魂殘渣」強化召喚物數值 (寫入 `units.json`)
- **帳本 (Ledger)：** 查看當前債務倒數與現金流

**Pygame 實作重點：** 滑鼠點擊事件處理、數據更新

### 3.2 狀態二：地圖選擇 (State_MapSelect)

**功能：** 選擇今晚要去哪裡「進貨」

**顯示：** 三大關卡的目前狀態

- 例如：教會好感度低 → 迷霧森林顯示「危險：聖騎士巡邏中」

### 3.3 狀態三：地下城冒險 (State_Dungeon) ✅ 已實作基礎

**視角：** 橫向捲軸 (Side-scrolling)

**核心玩法：**

- ✅ **玩家輸入：** WASD 移動，Space 跳躍，1 召喚
- ✅ **AI 運算：** 召喚物自動跟隨/巡邏/攻擊（已有 6 種 AI）
- ✅ **物理碰撞：** 使用 `pygame.Rect` 處理
- ✅ **鏡頭：** Camera 類別計算 offset
- ✅ **粒子特效：** 召喚時的魔法粒子

---

## 4. 數值與經營系統設計 (Simulation Design)

### 4.1 召喚物數據 (JSON 結構範例)

**檔案：** `data/units.json`

```json
{
  "ghoul": {
    "name": "食屍鬼",
    "type": "ground",
    "cost": 15,
    "hp": 30,
    "speed": 1.5,
    "attack_range": 20,
    "ai_type": "follow",
    "ai_params": {
      "follow_distance": 80,
      "stop_distance": 50
    },
    "description": "廉價勞工，死了不心疼。"
  },
  "imp": {
    "name": "小惡魔",
    "type": "flying",
    "cost": 25,
    "hp": 20,
    "speed": 2.5,
    "attack_range": 40,
    "ai_type": "aggressive",
    "ai_params": {
      "attack_range": 150,
      "chase_range": 300
    },
    "description": "飛行單位，主動攻擊。"
  }
}
```

### 4.2 陣營好感度 (Faction Logic)

**檔案：** `src/systems/faction.py`

```python
factions = {
    "church": 0,   # 範圍 -100 到 100
    "demon": 0,
    "guild": 0
}
```

**邏輯：**

- 當 `factions["church"] < -50`：生成敵人列表加入 Inquisitor (異端審判官)
- 當 `factions["demon"] > 50`：召喚物 Imp 的 Cost 降低 20%

### 4.3 經濟系統 (Economy)

- **貨幣：** 金幣 (Gold)
- **債務機制：** 每經過一天 (Day += 1)，債務利息增加 10%
- **Game Over 條件：** 若第 7 天未還清第 1 期款項

---

## 5. 戰鬥與 AI 邏輯 (Combat System)

### 5.1 召喚機制 (The Summoning) ✅ 已實作

- ✅ **隊列處理：** 玩家按下 1 → 檢查資源 → 實例化 Unit → 加入 sprite_group
- ✅ **連線效果 (Soul Link)：** 使用 `pygame.draw.line` 繪製玩家與單位之間的連線，帶有呼吸效果

### 5.2 單位 AI (State Machine) ✅ 已實作

**已實作的 AI 類型：**

| AI 類型      | 行為         | 狀態 |
| ------------ | ------------ | ---- |
| `follow`     | 跟隨玩家     | ✅   |
| `guard`      | 守衛固定位置 | ✅   |
| `patrol`     | 來回巡邏     | ✅   |
| `aggressive` | 主動攻擊敵人 | ✅   |
| `flee`       | 遇敵逃跑     | ✅   |
| `wander`     | 隨機遊蕩     | ✅   |

**狀態機邏輯：**

- **IDLE:** 檢查視野範圍內有無目標
- **MOVE:** 向目標移動
- **ATTACK:** 播放攻擊動畫，扣除目標 HP

---

## 6. 開發里程碑 (Roadmap)

### ✅ 第一階段：引擎原型 (已完成)

- [x] 建立 Pygame 視窗與 Game Loop
- [x] 實作 Player 移動與跳躍 (2.5D 物理)
- [x] 實作捲軸鏡頭 (Camera)
- [x] **產出：** 可以操控死靈法師在世界上跑跳

### ✅ 第二階段：召喚與戰鬥 (已完成基礎)

- [x] 實作 Unit 基礎類別
- [x] 實作召喚功能 (按下按鍵生成單位)
- [x] 實作 6 種基礎 AI
- [x] 實作 Soul Link 視覺連線
- [x] 實作粒子特效系統
- [x] **產出：** 可以召喚食屍鬼並看到魔法效果

### ✅ 第三階段：敵人與戰鬥系統 (已完成 90%)

- [x] 實作 Enemy 基礎類別 (`enemy.py`)
- [x] 實作敵人 AI (巡邏、追擊、跳躍攻擊)
- [x] 實作戰鬥判定 (碰撞檢測、Z 軸高度、傷害計算)
- [x] 實作生命值系統 (HP 條、HUD 顯示)
- [x] 實作掉落物品系統 (金幣、靈魂)
- [x] 實作威脅值系統 (敵人優先攻擊召喚物)
- [x] 實作怪物重生系統 (5 秒重生)
- [x] 實作關卡目標 (收集 100 金幣到出口)
- [ ] 實作死亡動畫 (目前只有粒子效果)
- [ ] **產出：** 完整的戰鬥循環 ✅

### 🔜 第四階段：經營循環 (Week 5-6)

- [ ] 建立 Shop 場景與 UI
- [ ] 串接 JSON 數據 (物品賣出增加金幣)
- [ ] 實作日夜切換循環
- [ ] 實作陣營好感度系統
- [ ] **產出：** 完整的遊戲循環 (打怪 → 賺錢 → 買強化 → 打更強的怪)

### 🔜 第五階段：美術與打磨 (Week 7+)

- [x] 替換玩家與 Ghoul 為 Pixel Art 素材
- [ ] 替換其他單位為 Pixel Art
- [ ] 加入音效與背景音樂
- [ ] 優化粒子特效
- [ ] 加入陣營好感度事件
- [ ] 打包與發布

---

## 7. 當前技術亮點 (Current Features)

### ✅ 已實作的系統

1. **2.5D 物理引擎** (`physics.py`)

   - X/Y 地面移動 + Z 軸高度
   - 重力、摩擦力
   - 世界邊界碰撞

2. **智能相機系統** (`camera.py`)

   - 跟隨玩家
   - 世界邊界限制
   - 平滑移動

3. **AI 行為系統** (`ai.py`)

   - 6 種可配置的 AI 行為
   - CommandableAI (可切換模式)
   - 基於狀態機的設計
   - 支援參數調整

4. **粒子特效系統** (`particles.py`)

   - 召喚魔法效果
   - 可擴展的粒子系統

5. **敵人系統** (`enemy.py`)

   - Skeleton 和 Goblin 兩種敵人
   - 巡邏、追擊、跳躍攻擊 AI
   - 威脅值目標選擇
   - HP 條顯示

6. **召喚物系統** (`sprites.py`)

   - Ghoul (近戰) 和 Wisp (遠程)
   - CommandableAI 控制
   - 威脅值系統
   - 自動攻擊

7. **UI 系統** (`ui.py`)

   - 召喚欄位
   - 單位頭像面板（圓形頭像 + 血量圓弧）
   - 右鍵選單（模式切換）
   - 可擴展架構（預留屬性/技能）

8. **戰鬥系統**

   - 玩家魔法彈攻擊
   - 召喚物自動戰鬥
   - 掉落物系統（金幣、靈魂）
   - 怪物重生機制
   - 關卡目標與出口

9. **角色編輯器** (`tools/character_editor.py`)
   - 圖片選擇（系統對話框）
   - 參數調整（Scale, Speed, HP）
   - AI 類型選擇（搜尋 + 滾動）
   - JSON 導出

---

## 8. 下一步建議 (Next Steps)

### ✅ 優先級 1：敵人系統 - 已完成

1. ✅ 創建 `Enemy` 類別
2. ✅ 實作基礎敵人 AI（巡邏、追擊）
3. ✅ 實作戰鬥判定

### ✅ 優先級 2：戰鬥系統 - 已完成

1. ✅ 生命值顯示
2. ✅ 傷害計算
3. ⚠️ 死亡動畫（部分完成，有粒子效果但無專門動畫）

### 🔜 優先級 3：關卡設計 - 建議跳過，直接進入經營循環

1. ❌ 使用 Tiled 創建地圖（目前程式生成已足夠）
2. ❌ 整合 pytmx
3. ⚠️ 設計敵人波次（有重生系統但無波次腳本）

### ⭐ 新建議：優先級 4：經營循環（推薦下一步）

1. 創建商店場景 UI
2. 實作日夜循環系統
3. 實作債務與經濟系統
4. 實作陣營好感度
5. 串接戰鬥與經營的完整循環

---

## 9. 技術債務與優化 (Technical Debt)

### 需要重構的部分

- [ ] 將 `sprites.py` 拆分為多個檔案
- [ ] 實作狀態機管理器
- [ ] 統一事件處理系統

### 效能優化

- [ ] 使用 Sprite Groups 的 dirty rect 更新
- [ ] 實作物件池 (Object Pooling)
- [ ] 優化粒子系統

---

**最後更新：** 2025-11-20  
**當前版本：** Alpha 0.2  
**開發狀態：** 原型階段 → 準備進入內容開發
