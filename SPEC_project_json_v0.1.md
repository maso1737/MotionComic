# MotionComic 共通プロジェクトJSON仕様 v0.1（叩き台）

全ツールの土台となるデータ契約。`[A]作画` が出力し、`[B]演出`・`[C]撮影`・`[D]プレイヤー` が読む唯一の共通フォーマット。
**設計方針:** シンプル / 拡張可能（`x_` 接頭辞で実験フィールド追加可）/ 後方互換は `version` で管理。

---

## 1. トップレベル構造

```jsonc
{
  "version": "0.1",
  "id": "triosis-scene01",
  "title": "TrioSisBrothers / Scene 01",
  "work": "TrioSisBrothers",          // 凹凸キッズ | TrioSisBrothers | うえへ うえへ
  "scroll": { ... },                  // §2 スクロール定義
  "stage": { ... },                   // §3 ステージ（画面・座標系）
  "assets": [ ... ],                  // §4 画像/音などの実体
  "layers": [ ... ],                  // §5 レイヤー（描画＋奥行き＋連動）
  "panels": [ ... ],                  // §6 コマ枠（変形する舞台装置）
  "events": [ ... ],                  // §7 スクロール連動イベント
  "post": { ... }                     // §8 ポストエフェクト（撮影処理）
}
```

---

## 2. scroll — スクロール定義

```jsonc
"scroll": {
  "axis": "y",            // y=縦 | x=横 | y_invert=上スクロール（うえへ うえへ）
  "length": 8000,         // スクロール全長(px相当の論理単位)
  "unit_label": "m",      // 高度/距離表示用（途中で壊す演出は events で上書き）
  "speed_reactive": true  // スクロール速度を風圧等に流すか
}
```

`progress`（0.0〜1.0）を全システム共通の時間軸とする。px ではなく progress で同期する。

---

## 3. stage — 画面と座標系

```jsonc
"stage": {
  "width": 1080, "height": 1920,   // 基準解像度（レスポンシブは比率維持）
  "background": "#f4efe6",
  "camera_depth": 1.0              // パララックス基準（depth=1.0が等速）
}
```

座標は基準解像度の論理ピクセル。原点は左上、+y は下。

---

## 4. assets — 実体

```jsonc
"assets": [
  { "id": "a_kakashi", "type": "image", "src": "img/kakashi.png", "w": 600, "h": 1400 },
  { "id": "snd_wind",  "type": "audio", "src": "snd/wind.mp3", "loop": true }
]
```

`src` はリポジトリ相対パス。作画ツールは PNG（透過レイヤー）で書き出す。

---

## 5. layers — レイヤー（最重要）

作画の1レイヤー＝1エントリ。奥行きと連動をここに集約。

```jsonc
"layers": [
  {
    "id": "L_kakashi_body",
    "name": "カカシ兄_本体",
    "asset": "a_kakashi",
    "z": 20,                      // 描画順（大きいほど手前）
    "depth": 0.6,                 // パララックス係数(0=遠/動かない 1=等速 >1=手前で速い)
    "transform": { "x": 300, "y": 900, "scale": 1.0, "rot": 0 },
    "scroll_bind": {              // スクロールに対する動き（任意）
      "y": { "factor": 0.6 },     // depthと別に個別補正したい時
      "wind_lag": 0.0             // 布の遅れ等（0〜1, 大きいほど遅延）
    },
    "tone": null,                 // §5.1 スクリーントーン
    "texture": "watercolor_soft", // 水彩テクスチャ名 or null
    "layer_role": "frame_inside"  // frame_inside=コマ内/土地依存, traveler=コマ越え/手前
  }
]
```

### 5.1 tone（スクリーントーン）

```jsonc
"tone": { "type": "dot", "density": 0.4, "angle": 45, "size": 6 }
// type: dot | line | gradient | noise
```

### layer_role の意味（TrioSis構造を一般化）

- `frame_inside`: コマの内側・場所に依存（兄弟側）
- `traveler`: コマ枠を越えられる手前レイヤー（姉妹側）
- `bg` / `fx`: 背景・効果

---

## 6. panels — コマ枠（変形する舞台装置）

クリスタ風コマ枠。天気/風/温度で「にゅん・たわむ・ピシッ」と変形。

```jsonc
"panels": [
  {
    "id": "P1",
    "shape": [[100,200],[980,200],[980,1200],[100,1200]], // 多角形頂点
    "stroke": { "color": "#222", "width": 6 },
    "deform": {
      "mode": "spring",           // spring=ばね揺れ | bend=たわみ | snap=ピシッ | round=角丸
      "amount": 0.0,              // 0=静止。events で driveする
      "bind_progress": true       // スクロール進行/速度で量を変える
    },
    "spawn_layers": ["L_kakashi_body"]  // 「枠がキャラを生やす」: 枠変形に同期して出現
  }
]
```

---

## 7. events — スクロール連動イベント

`progress` 区間に対する変化。演出ツールが主に編集。

```jsonc
"events": [
  {
    "at": [0.10, 0.25],          // progress 区間
    "target": "P1",
    "set": { "deform.amount": 0.8, "deform.mode": "bend" }
  },
  {
    "at": [0.40, 0.42],          // 一瞬の“キラッ”
    "type": "moment",
    "set": { "post.grain": 0.0, "audio.mute": true, "scroll.snap": true }
  },
  {
    "at": [0.55, 1.0],
    "target": "scroll.unit_label",
    "set": { "value": ["記憶","祈り","ひかり"] }  // 高度表示が壊れる（うえへ うえへ）
  }
]
```

区間外は線形補間 or 直前値保持（`hold` フラグで指定、既定は補間）。

---

## 8. post — ポストエフェクト（撮影処理）

```jsonc
"post": {
  "grain": 0.15,        // フィルムグレイン
  "vignette": 0.2,
  "bloom": 0.3,         // 光のにじみ
  "color_shift": { "r": 1.02, "g": 1.0, "b": 0.98 }, // 色被り
  "chromatic": 0.0,
  "lut": null           // 将来: ルックテーブル名
}
```

全値 events から上書き可能（撮影もスクロール連動できる）。

---

## 9. 作品別の使い分け（同一仕様で吸収）

| 要素 | 凹凸キッズ | TrioSisBrothers | うえへ うえへ |
|---|---|---|---|
| `scroll.axis` | `x` | `y` | `y_invert` |
| 主役 | キャラ移動 | `panels.deform`＋`layer_role` | `layers.depth`多層パララックス |
| `texture` | watercolor/crayon | paper | paper_cut |
| 特徴events | 仲間追従 | moment“キラッ”/風崩壊 | unit_label崩壊/テキスト浮遊 |

---

## 10. 未確定・次回論点（v0.2 へ）

- 作画ツールの実書き出し単位（レイヤー＝PNG固定か、ベクター保持か）
- `events` のイージング指定方法（現状linearのみ）
- 音声同期の粒度
- テキスト（詩）の扱い: layer内テキストノード化するか別 `texts[]` を立てるか

---

**承認後の動き:** この仕様を契約として D1作画 / D2演出 を別チャットで起動。各Dirへは「この仕様の §X を実装」の形で指示書を発行する。
