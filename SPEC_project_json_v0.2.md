# MotionComic 共通プロジェクトJSON仕様 v0.2

全ツールの土台となるデータ契約。`[A]作画` が出力し、`[B]演出`・`[C]撮影`・`[D]プレイヤー` が読む唯一の共通フォーマット。

## 設計憲章（不変の原則）

> **「3Dではない、でも生きている」── 紙の中が生きている感覚をつくる。**

1. **少ない文法で作品差を出す。** 変形・イージング等は固定プリセットのみ。安易に増やさない（世界観が散る／演出が軽くなる／学習コスト増）。"少なさ"自体がブランド。
2. **数値より意味を駆動する。** 核は「意味が変質する瞬間」。`semantic_shift` を一級市民とする。
3. 拡張は `x_` 接頭辞で実験。後方互換は `version` で管理。

作品ごとの本質（実装判断の北極星）:
- 凹凸キッズ＝「友情」を構造力学で描く / TrioSis＝キャラ性をレンダリング構造で定義 / うえへ＝「意味の変質」をスクロールで体験

---

## 1. トップレベル構造

```jsonc
{
  "version": "0.2",
  "id": "triosis-scene01",
  "title": "TrioSisBrothers / Scene 01",
  "work": "TrioSisBrothers",
  "scroll": { ... },   // §2
  "stage": { ... },    // §3
  "assets": [ ... ],   // §4
  "layers": [ ... ],   // §5
  "panels": [ ... ],   // §6
  "onomatopoeia": [ ... ], // §7 擬音カード
  "events": [ ... ],   // §8
  "audio": { ... },    // §9
  "post": { ... }      // §10
}
```

共通時間軸は `progress`（0.0〜1.0）。px ではなく progress で全システム同期。

---

## 2. scroll

```jsonc
"scroll": { "axis": "y", "length": 8000, "unit_label": "m", "speed_reactive": true }
// axis: y=縦 | x=横 | y_invert=上スクロール
```

---

## 3. stage

```jsonc
"stage": { "width": 1080, "height": 1920, "background": "#f4efe6", "camera_depth": 1.0 }
```
原点左上、+y下。座標は基準解像度の論理px。

---

## 4. assets

```jsonc
"assets": [
  { "id": "a_kakashi", "type": "image", "src": "img/kakashi.png", "w": 600, "h": 1400 },
  { "id": "bgm_main",  "type": "audio", "src": "snd/suno_main.mp3", "loop": true },
  { "id": "se_don",    "type": "audio", "src": "snd/don.mp3" }
]
```
**画像は PNG（透過レイヤー）固定。** 作画ツールはレイヤー＝1PNGで書き出す（ベクター保持しない／v0.2確定）。

---

## 5. layers

```jsonc
{
  "id": "L_kakashi_body", "name": "カカシ兄_本体", "asset": "a_kakashi",
  "z": 20, "depth": 0.6,
  "transform": { "x": 300, "y": 900, "scale": 1.0, "rot": 0 },
  "scroll_bind": { "y": { "factor": 0.6 }, "easing": "wind_lag" },
  "tone": { "type": "dot", "density": 0.4, "angle": 45, "size": 6 },
  "texture": "watercolor_soft",
  "layer_role": "frame_inside"   // frame_inside=コマ内/土地依存 | traveler=コマ越え/手前 | bg | fx
}
```
`tone.type`: dot | line | gradient | noise。`depth`: 0=遠/不動 1=等速 >1=手前で速い。

---

## 6. panels — コマ枠（変形する舞台装置）

```jsonc
{
  "id": "P1",
  "shape": [[100,200],[980,200],[980,1200],[100,1200]],
  "stroke": { "color": "#222", "width": 6 },
  "deform": { "mode": "spring", "amount": 0.0, "bind_progress": true },
  "spawn_layers": ["L_kakashi_body"]
}
```

**deform.mode は次の4種のみ（v0.2 固定・拡張禁止）:**

| mode  | 感触 |
|-------|------|
| spring | ばね揺れ |
| bend   | たわみ |
| snap   | ピシッとキメ |
| round  | 角丸（雪・やわらかさ） |

---

## 7. onomatopoeia — 擬音カード

漫画のオノマトペを「上からカード的に乗る」表現。

```jsonc
"onomatopoeia": [
  {
    "id": "O_don", "text": "ドーン！", "asset": null,   // 文字 or 画像どちらでも
    "at": [0.30, 0.34],
    "enter": "drop_from_top",      // 上からカードが乗る（既定）
    "z": 90,                       // 最前面寄り
    "transform": { "x": 540, "y": 600, "scale": 1.0, "rot": -4 },
    "style": { "font": "comic", "color": "#111", "stroke": "#fff", "stroke_w": 8 },
    "x_lyric_anim": null           // 将来: Vtuber MV的リリックアニメ（v0.3候補・今は予約のみ）
  }
]
```
v0.2 では `enter: drop_from_top` のみ正式サポート。リリック文字アニメは `x_lyric_anim` で予約だけ確保（実装は v0.3 判断）。

---

## 8. events — スクロール連動イベント

2系統を持つ。**意味駆動を一級市民とする。**

### 8.1 数値イベント（補間あり）
```jsonc
{ "at": [0.10, 0.25], "target": "P1", "set": { "deform.amount": 0.8, "deform.mode": "bend" }, "easing": "snap_comic" }
```

### 8.2 semantic_shift（概念変更トリガー／物理シミュではない）
```jsonc
{
  "at": [0.55, 0.70],
  "type": "semantic_shift",
  "target": "world.gravity",      // 例: world.gravity / scroll.unit_label / world.space
  "value": "memory"               // 概念名 or 文字列配列（順に置換）
}
```
波及先（プレイヤーが解釈）: UI / 詩テキスト / 色温度 / 音 / パララックス / テキスト挙動 / FX / スクロール感覚。
例: `unit_label` 1200m → 「祈り」、`gravity` 9.8 → "memory"（漂う easing・音遅延・UI浮遊・色温度変化へ波及）。

### 8.3 moment（一瞬のキラッ）
```jsonc
{ "at": [0.40, 0.42], "type": "moment", "set": { "post.grain": 0, "audio.mute": true, "scroll.snap": true } }
```

---

## 8.x easing — 感情語イージング（プリセット固定）

数値イベント・scroll_bind で使う `easing` 値。これ以外は使わない。

| name | 感触 |
|------|------|
| paper_soft   | 紙っぽく遅れる |
| wobble_child | 子供っぽい |
| snap_comic   | 漫画的キメ |
| float_memory | 記憶っぽい |
| wind_lag     | 布遅延 |

---

## 9. audio — 音声同期

```jsonc
"audio": {
  "bgm":  { "asset": "bgm_main", "level": 0.25, "scene_reactive": true },  // SUNO BGM。うっすら、シーンに合わせる
  "se":   [ { "asset": "se_don", "at": 0.31, "level": 0.9 } ]              // 効果音はしっかり
}
```
方針: **BGM＝うっすら＆シーン連動 / 効果音＝しっかり。** 同期粒度は progress 単位（v0.2）。

---

## 10. post — ポストエフェクト（撮影処理）

```jsonc
"post": { "grain": 0.15, "vignette": 0.2, "bloom": 0.3,
          "color_shift": { "r": 1.02, "g": 1.0, "b": 0.98 }, "chromatic": 0.0, "lut": null }
```
全値 events / semantic_shift から上書き可能。

---

## 11. 作品別の使い分け（同一仕様で吸収）

| 要素 | 凹凸キッズ | TrioSisBrothers | うえへ うえへ |
|---|---|---|---|
| scroll.axis | x | y | y_invert |
| 主役 | キャラ移動・結合 | panels.deform＋layer_role | layers.depth多層＋semantic_shift |
| 物理法則 | 凹凸結合/追従/役割交代/外れ崩壊 | コマ＝空間/感情で歪む/越境 | 上昇で概念崩壊/単位が詩に |
| texture | watercolor / crayon | paper | paper_cut |
| 特徴 | 仲間追従events | moment“キラッ”/風崩壊 | semantic_shift連発/テキスト浮遊 |

---

## 12. v0.3 へ送る論点

- `x_lyric_anim`（Vtuber MV的リリック文字アニメ）を正式化するか
- semantic_shift の波及ルール定義（どの概念がどのサブシステムをどう変えるか辞書化）
- 凹凸キッズの「結合・追従」物理（layer間リンク構造）の表現方法
- onomatopoeia の enter バリエーション追加可否（憲章原則1に照らし慎重に）

---

**確定事項:** PNG固定 / deform 4種固定 / 感情語イージング5種 / BGMうっすら＋SEしっかり / semantic_shift採用 / オノマトペは上乗せカード。
**次:** この v0.2 を契約として D1作画・D2演出 を別チャットで起動。各Dirへ「§Xを実装」の指示書を発行。
