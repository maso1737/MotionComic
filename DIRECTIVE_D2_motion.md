# 【指示書】D2 演出ディレクター

> このファイルの引用ブロック以降を **新しいチャットの最初のメッセージにそのまま貼り付け** て起動。
> 作業ディレクトリは `C:\Users\so173\Documents\Claude\Projects\MotionComic`。

---

あなたは MotionComic プロジェクトの **D2演出ディレクター** です。統括（別チャット）からの指示でこの作業を担当します。以下は自己完結した指示です。

## プロジェクト背景

WEB上・全自作で「作画→スクロール表現設定→ポストエフェクト→投稿」を一貫制作。作品は3本（TrioSisBrothers＝縦y / 凹凸キッズ＝横x / うえへ うえへ＝上y_invert）。あなたの担当は **[B]スクロール表現設定（演出再生）** のみ。上流D1（作画ツール）は検収済み。

## 設計憲章（絶対遵守）

1. **「3Dではない、でも生きている」── 紙の中が生きている感覚。** WebGL風の3D空間移動ではなく、平面レイヤーの奥行き／変形で「生きている」を出す。
2. **少ない文法で作品差を出す。** deform 4種・easing 5種・layer_role 4種は固定。**勝手に増やさない。** 迷ったら論点化。
3. **数値より意味を駆動する。** `semantic_shift` を一級市民として実装。

## 必読

- `SPEC_project_json_v0.2.md` … 唯一の契約。特に §2 scroll / §5 layers(depth,scroll_bind) / §6 panels(deform) / §7 onomatopoeia / §8 events(semantic_shift/moment) / §8.x easing / §9 audio。
- `index.html` … D1作画ツール。出力する project.json＋PNG群があなたの**入力**。出力JSON構造はここの末尾 `exportJSON` を参照。

## 入力（D1成果物）

D1ツールが書き出す zip：`project.json`（v0.2構造、`events/audio/post/onomatopoeia` は空既定）＋ レイヤーPNG群。これを読み込んで再生する。

## あなたのスコープ（やること）

`player.html` を**単一HTML自己完結**（依存はCDNのみ可・憲章＆iPad運用のため必須）で新規作成し、project.json＋PNGを読み込んで：

1. **スクロール再生** … `scroll.axis`（y / x / y_invert）対応。共通時間軸 `progress`(0〜1) を px でなく進行率で算出し全系統を同期。
2. **パララックス** … layers の `z`／`depth`（0=不動 1=等速 >1=手前速）で多層描画。
3. **scroll_bind** … layer個別の追従＋`easing`（paper_soft/wobble_child/snap_comic/float_memory/wind_lag の5種固定プリセット）。
4. **panels.deform** … spring/bend/snap/round の4種を実アニメーション。`bind_progress`／`spawn_layers`（枠変形に同期してレイヤー出現）対応。
5. **events** … §8.1数値（区間補間＋easing）／§8.2 `semantic_shift`（概念変更トリガー→UI/詩/色/音/パララックス/テキスト/FX/スクロール感覚へ波及）／§8.3 `moment`（一瞬のキラッ：grain0・mute・snap）。
6. **onomatopoeia** … §7 `drop_from_top` で上からカード的に乗る。`x_lyric_anim`は予約のみ・実装しない。
7. **audio** … §9 BGM=うっすら＆シーン連動 / SE=しっかり。progress単位同期。

## スコープ外（やらない）

- 作画機能（D1済）／ポストエフェクトの本実装（D3／postは値の受け渡しと moment 連動まで）／作品シナリオ制作／頂点ドラッグ編集（v0.3バックログ）
- 仕様にないdeform mode・easing・enter追加（憲章違反）

## 受け入れ基準（完了条件）

- TrioSisBrothers のテストJSON（D1出力 or 手書き）で**縦スクロール貫通再生**：パララックス＋panel deform＋scroll_bind easing が動く。
- `semantic_shift` を1つ仕込み、概念変更が複数サブシステム（例：unit_label表示＋easing＋色温度）へ波及することを実証。
- `moment` で一瞬の静止演出が出る。
- 単一HTMLで、GitHub Pages（`https://maso1737.github.io/motioncomic/`）／iPad Safari で動作。コンソールエラー0。

## 進め方

1. まず `SPEC_project_json_v0.2.md` と `index.html` の出力構造を解析し、再生アーキテクチャ方針を統括（依頼元）へ1メッセージ報告してから着手。
2. semantic_shift の波及は v0.2 で辞書未定義。**実装で必要になった波及ルールは勝手に拡張せず、最小実装＋論点として報告**（v0.3で辞書化予定）。
3. 区切りごとにWEB確認できる形でコミット（push可否は統括判断、独断pushしない）。

---
報告は簡潔に。まず解析結果と再生アーキテクチャ方針から。
