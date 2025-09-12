# CLAUDE.md

このファイルはClaude Code (claude.ai/code) がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

これは文書から概念と関係を抽出してインタラクティブな概念マップを生成するPythonベースのLLM概念マッピングツール（概念マッピングツール）です。日本語と英語のテキストに最適化され、特に日本語概念抽出に特化しています。

## コアアーキテクチャ

### 主要コンポーネント
- **`pipeline.py`**: 文書を概念抽出パイプライン全体で処理するメインオーケストレーションスクリプト
- **`llm.py`**: 設定可能なモデルでOpenAI互換API通信を行うChatCompletionsClient
- **`prompts.py`**: 概念と関係抽出のための構造化プロンプトを含む
- **`utils.py`**: 日本語対応IDスラグ化とJSON解析を含むテキスト処理ユーティリティ
- **`viewer.html`**: 概念マップ可視化用のインタラクティブHTMLビューア
- **`webui/`**: React+TypeScript+D3.jsベースのモダンWebUI
- **`create_graph_fix_prompt.py`**: 非連結グラフ修正用プロンプト生成ツール

### データモデル
コードベースは構造化データ用にPython dataclassesを使用：
- **Concept**: ID、ラベル、エイリアス、定義、証拠を持つ抽出概念を表す
- **Edge**: ソース/ターゲット、関係、関係記述、信頼度スコア、証拠を持つ概念間関係を表す
- **Section**: ID、章、タイトル、内容を持つ文書セクション
- **Evidence**: ソース文書からの支援テキスト断片

### 関係表現システム（2025-09-09更新）
従来の固定関係タイプから自由形式自然言語関係に変更：

**新しい関係フィールド構造:**
- **`relation`**: グラフ表示用の短いラベル（1-3語）例：「包含する」「示す」「対照的」
- **`relation_description`**: 完全な自然言語記述 例：「プルラリティ（多元性）は記述的多元性を含む」

**従来のRELATION_TYPESは削除済み** - より柔軟で自然な関係表現が可能

## 開発コマンド

### 環境セットアップ
```bash
# 仮想環境作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envを編集してOPENAI_API_KEYを追加
```

### パイプライン実行
```bash
# 基本実行（contents/japaneseから読み取り）
python pipeline.py --out ./output

# カスタム入力ディレクトリと設定
python pipeline.py --input ./my_documents --out ./output --max-concepts 10 --model gpt-4o-mini

# セクション間関係分析
python pipeline.py --out ./output --cross-section true
```

### 結果表示
```bash
# 出力ディレクトリでローカルサーバー開始
cd output
python -m http.server 8000

# ビューアーアクセス:
# 基本: http://localhost:8000/viewer.html

# WebUI開発サーバー（推奨）
cd webui
npm install
npm run dev  # http://localhost:3000
```

## 主要設定

### 環境変数 (.env)
```bash
OPENAI_API_KEY=your_api_key_here          # 必須
OPENAI_BASE_URL=https://api.openai.com/v1 # オプション、デフォルトはOpenAI
OPENAI_MODEL=gpt-4o-mini                  # オプション、モデル設定
```

### コマンドラインオプション
- `--input`: 入力ディレクトリパス（デフォルト: `contents/japanese`）
- `--out`: 出力ディレクトリパス（必須）
- `--segment-level`: セクション分割レベル（h1/h2/h3、デフォルト: h2）
- `--max-concepts`: セクションあたりの最大概念数（デフォルト: 15）
- `--cross-section`: セクション間関係分析を有効化（デフォルト: false）
- `--model`: 使用するLLMモデル（デフォルト: gpt-4o-mini）

## モデル選択戦略

### サポートモデル
- **GPT-5-mini**: 最高品質、最高コスト - 本番環境/最終版に使用
- **GPT-4o-mini**: バランス品質/コスト - 開発に推奨
- **GPT-3.5-turbo**: 最速、最低コスト - テスト用

### 日本語対応考慮
- GPT-5-mini: 優秀な日本語概念抽出、Unicode記号（⿻）保持
- GPT-4o-mini: 良好な日本語サポート、構造理解が安定
- GPT-3.5-turbo: 日本語プロンプトでも英語ラベル生成の可能性

## 出力ファイル構造

### データファイル
- `graph.json`: 証拠とメタデータを含む完全なグラフデータ
- `nodes.csv`: 概念リスト（ID、ラベル、定義、エイリアス、証拠）
- `edges.csv`: 関係リスト（source、target、relation、relation_description、confidence、evidence）
- `mermaid.md`: Mermaidダイアグラム記法
- `cross_chapter_links.json`: 章間の概念関連を記録（章間リンク機能用）

### グラフデータスキーマ (graph.json)

**トップレベル構造:**
```json
{
  "nodes": [...],           // 概念ノードの配列
  "edges": [...],           // 関係エッジの配列
  "metadata": {...},        // 生成メタデータ
  "sections": [...],        // セクション情報の配列
  "cross_chapter_links": {...}  // 章間リンク情報（オプション）
}
```

**Nodeオブジェクト:**
```json
{
  "id": "string",           // 一意識別子（例: "plurality_多元性"）
  "label": "string",        // 表示ラベル（例: "プルラリティ（多元性）"）
  "definition": "string",   // 概念の定義
  "aliases": ["string"],    // 別名のリスト
  "evidence": ["string"],   // ソーステキストからの証拠引用
  "section_id": "string"    // 所属セクションID（例: "0-0"）
}
```

**Edgeオブジェクト:**
```json
{
  "source": "string",              // ソースノードID
  "target": "string",              // ターゲットノードID
  "relation": "string",            // 短い関係ラベル（1-3語）
  "relation_description": "string", // 詳細な関係説明
  "confidence": 0.0-1.0,           // 信頼度スコア
  "evidence": ["string"]           // 関係を支持する証拠引用
}
```

**Metadataオブジェクト:**
```json
{
  "generated_at": "ISO 8601 timestamp",
  "model": "string",               // 使用したLLMモデル
  "max_concepts": number,          // セクションあたり最大概念数
  "cross_section": boolean,        // セクション間分析の有無
  "segment_level": "string"        // セクション分割レベル（h1/h2/h3）
}
```

**Sectionオブジェクト:**
```json
{
  "id": "string",          // セクションID（例: "0-0"）
  "chapter": number,       // 章番号
  "title": "string",       // セクションタイトル
  "content": "string"      // セクション本文（オプション）
}
```

**CrossChapterLinksオブジェクト:**
```json
{
  "概念名": {
    "chapters": [number],     // 概念が出現する章番号のリスト
    "node_ids": ["string"]    // 各章でのノードIDのリスト
  }
}
```

### ビューアーファイル
- `viewer.html`: シンプル可視化用基本ビューア
- `webui/`: React+D3.jsベースの高機能WebUI（推奨）

## 開発ノート

### テキスト処理
- `utils.py`の`slugify_id()`関数はUnicode正規表現で日本語文字を適切に処理
- `normalize_label()`は一貫した日本語テキスト処理にNFKC正規化を適用
- 証拠切り詰めは長い引用の開始/終了を保持

### APIエラー処理
- 429 (Rate Limit): より低いティアのモデルに切り替えまたは遅延追加
- 400 (Bad Request): モデル固有のパラメータ制約を確認
- insufficient_quota: OpenAIアカウントにクレジット追加

### カスタマイズポイント
1. **概念抽出**: `prompts.py`の`SECTION_CONCEPTS_PROMPT`を変更
2. **関係表現**: プロンプトルールで関係記述スタイルを調整
3. **UI/可視化**: WebUIコンポーネントまたはviewer.htmlのCSS/JavaScriptをカスタマイズ
4. **言語サポート**: 異なるソース言語用にプロンプトを調整

## 重要な実装詳細

### 最新の改善（2025-09-09）
1. **概念階層の動的化**: tierフィールドを削除し、max_conceptsによる重要度ベースフィルタリングに変更
2. **関係表現の二重化**: 
   - グラフ表示用の短い`relation`ラベル
   - 詳細な`relation_description`記述
3. **自然言語関係**: 固定タイプから自由形式自然言語記述へ移行

### システム特性
- 概念ラベルで元の言語を保持（日本語入力 → 日本語概念）
- 証拠はソーステキストからの逐語引用である必要がある
- 関係信頼度スコアは0.0から1.0の範囲
- セクション間分析は大きな文書では計算量が多い
- WebUIはCSS VariablesとFetch APIのモダンブラウザサポートが必要

## WebUI開発

### 技術スタック
- React 18 + TypeScript
- Vite（高速開発サーバー）
- D3.js v7（インタラクティブグラフ可視化）
- CSS Variables（一貫したテーマ）

### プロジェクト構造
```
webui/
├── src/
│   ├── components/           # React components
│   │   ├── ConceptDetails.tsx   # Sidebar concept information panel
│   │   ├── D3Graph.tsx         # Main graph visualization component
│   │   └── Toolbar.tsx         # Filter controls and legend
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts            # GraphData, Concept, Edge, TierFilter types
│   ├── utils/               # Utility functions
│   │   └── dataLoader.ts       # Graph data loading logic
│   ├── data/                # Sample/test data
│   │   └── sample.ts           # Sample concept map data
│   ├── App.tsx              # Main application component
│   ├── App.css              # Global styles
│   └── main.tsx             # React entry point
├── scripts/                 # Build and deployment scripts
│   └── generate-static.js      # Static HTML generation script
├── dist/                    # Build output directory
├── viewer.html              # Legacy HTML viewer (preserved)
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### 開発ワークフロー
```bash
cd webui
npm install
npm run dev          # 開発サーバー（HMR付き） http://localhost:3000
npm run build        # 本番ビルド（React SPA）
npm run build:static # 静的HTML生成（全デプロイメント形式）
```

### データ統合
- `webui/public/graph.json`に生成データを配置して開発
- 本番では`./graph.json`を自動読み込み
- サンプルデータへの自動フォールバック

### コンポーネントアーキテクチャ

**主要コンポーネント:**
- **App.tsx**: メインアプリケーションコンテナ、状態管理
- **D3Graph.tsx**: D3.js使用のコア可視化コンポーネント、力学的グラフレイアウト
- **ConceptDetails.tsx**: 選択概念の詳細情報表示パネル
- **Toolbar.tsx**: 概念tierフィルタリングと関係タイプ凡例

**パフォーマンス最適化:**
- `useMemo`でデータ処理の再計算防止
- `useCallback`で安定したイベントハンドラー
- 適切な依存配列で無限再レンダリング防止
- コンポーネントアンマウント時のD3クリーンアップ

### ビルド出力形式
1. **React SPA** (`dist/index.html`): モダンシングルページアプリケーション
2. **レガシービューア** (`dist/viewer_legacy.html`): オリジナルHTMLとD3.js
3. **静的ビューア** (`dist/viewer_static.html`): 埋め込みデータの自己完結型
4. **データファイル** (`dist/graph.json`): 外部利用用JSONデータ

### D3.js統合のベストプラクティス
- DOM要素参照に`useRef`使用
- useEffectクリーンアップでD3選択をクリーン
- ReactステートマネジメントでD3イベント処理
- D3レンダリングロジックをReactライフサイクルから分離

### トラブルシューティング
**一般的な問題:**
1. **無限再レンダリング**: useEffect依存関係チェック
2. **D3競合**: D3選択とイベントリスナーの適切なクリーンアップ確認
3. **データ読み込み**: `graph.json`形式とアクセシビリティ確認
4. **ビルドエラー**: TypeScript型とインポートパス確認

## Git ワークフローガイドライン

### コミットコマンド解釈
**ステージングとコミットの明確な区別:**

- **"add commitして"**: `git add .`の後`git commit`を実行（全変更をステージしてコミット）
- **"commitして"**: `git commit`のみ実行（ステージ済み変更のみコミット、追加ステージングなし）

これにより、シンプルなコマンドパターンを維持しながら、何がコミットされるかを正確に制御できます。

## グラフ修正ツール

### 非連結グラフ修正プロンプト生成
```bash
# 特定セクションの修正プロンプトを生成
python create_graph_fix_prompt.py --section-id 1-0 --output fix_prompt_1-0.txt

# パラメータ説明
# --section-id: セクションID（1-0, 0-2など）
# --output: 出力プロンプトファイル名（省略可、デフォルト: graph_fix_prompt.txt）
# --max-concepts: 元の最大概念数設定（省略可、デフォルト: 15）
```

**機能:**
- 非連結グラフの連結性を自動分析
- 元のMarkdownテキスト、抽出プロンプト、現在のグラフデータを含む包括的プロンプトを生成  
- LLMに概念統合ではなく「最小限の新概念追加」による修正を指示
- 孤立ノードと連結成分を特定し、橋渡し概念の追加を促す

**出力プロンプトの使用:**
1. 生成されたプロンプトをLLM（GPT-4o-miniまたはGPT-5-mini）に送信
2. LLMの提案に従って新しい概念とエッジを手動で追加
3. 修正後のグラフが連結されているか確認

**ファイル自動検索:**
ツールは以下の場所からファイルを自動検索：
- Markdownファイル: `./input/`
- グラフファイル: `./webui/public/`

### グラフ連結性修正のベストプラクティス（2025-09-12更新）

**推奨モデル: GPT-5 Thinking**
実験結果により、グラフの連結性修正には**GPT-5 Thinking**が最も効果的であることが判明：

**GPT-5 Thinking の優位性:**
- **戦略的思考**: グラフ全体の構造を理解し、最小限の追加で最大の効果を狙う
- **証拠ベース設計**: 原文に基づいた自然で正当性の高い概念・関係を提案
- **系統的アプローチ**: 孤立ノードを特定し、中心的概念を通じて効率的に連結
- **品質重視**: 意味のある関係のみを追加し、人工的な接続を避ける

**実証データ（extra-1, extra-2, extra-3での成功例）:**
- GPT-5 mini: 複数回の試行が必要、部分的な改善
- **GPT-5 Thinking: 一回で完全連結達成（10→1 連結成分、孤立ノード 0）**

**運用フロー:**
1. `create_graph_fix_prompt.py`でプロンプト生成
2. **GPT-5 Thinking**にプロンプト送信（推奨）
3. 提案された概念・エッジを手動でJSONに追加
4. 連結性確認（再度ツール実行）

**重要: 現在自動化不可**
グラフ連結性修正は現在のところ完全自動化できないため、プロンプト生成→人間判断→手動実装のワークフローが必要。

## ソースジャンプ機能（原文リンク）

### 概要
証拠項目から原文へ直接ジャンプできるインライン機能。テキストフラグメントAPIを使用して正確な引用箇所への遷移を実現。

### 実装アーキテクチャ

**コアファイル:**
- `webui/src/utils/sourceLinks.ts`: URL生成とテキストフラグメント作成
- `webui/src/components/ConceptDetails.tsx`: インラインアイコン表示
- `webui/src/types/index.ts`: Evidence型にsource_url、GraphData型にmetadata追加

**URL生成ロジック:**
```typescript
// デフォルト: Plurality.net chapters
const baseUrl = 'https://www.plurality.net/v/chapters';
const chapterUrl = `${baseUrl}/${sectionId}/jpn/`;

// テキストフラグメント付き
const url = `${chapterUrl}#:~:text=${encodedText}`;
```

### テキストフラグメント生成

**短いテキスト（～100文字）:**
```typescript
const escaped = text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
return encodeURIComponent(escaped);
```

**長いテキスト（100文字超）:**
```typescript
const startWords = words.slice(0, 5).join(' ');
const endWords = words.slice(-5).join(' ');
return `${encodeURIComponent(startWords)},${encodeURIComponent(endWords)}`;
```

### URL特別マッピング

**Plurality.netの構造対応:**
```typescript
// 1-0セクションは特別にURLパス「1」を使用
let urlPath = normalizedSection;
if (normalizedSection === '1-0') {
  urlPath = '1';
}
```

**理由:** `https://www.plurality.net/v/chapters/1-0/jpn/` は404、`/1/jpn/` が正解

### UI設計原則

**インライン表示:**
- 大きなボタンではなく小さなアイコンで場所を節約
- 文章の末尾に `margin-left: 6px` で自然に配置
- `vertical-align: baseline` でベースライン揃え

**視覚的配慮:**
- 初期透明度: `opacity: 0.7`（目立ちすぎないよう）
- ホバー時: `opacity: 1.0` + `translateY(-1px)`
- アイコンサイズ: 12x12px（テキストと調和）

### 拡張性対応

**カスタムベースURL:**
```typescript
// graph.jsonのmetadataでカスタムURL指定可能
{
  "nodes": [...],
  "edges": [...],
  "metadata": {
    "source_base_url": "https://custom-domain.com/chapters"
  }
}
```

**Evidence型の拡張:**
```typescript
interface Evidence {
  text: string;
  section?: string;
  source_url?: string;  // 個別URL指定可能
}
```

### 技術的ノウハウ

**テキストフラグメント最適化:**
- 日本語テキストの正確なURLエンコーディング
- 長い引用文の開始/終了抽出で検索精度向上
- 正規表現特殊文字のエスケープ処理

**React統合:**
- コンポーネント間でのsection情報伝播
- props drilling回避（currentSection をConceptDetailsに直接渡す）
- TypeScript型安全性の維持

**デバッグ手法:**
```bash
# URL存在確認
curl -I "https://www.plurality.net/v/chapters/1-0/jpn/" # 404
curl -I "https://www.plurality.net/v/chapters/1/jpn/"   # 200
```

### 運用上の注意点

1. **Text Fragments API対応**: Chrome 80+、Firefox未対応（フォールバック: ページトップに遷移）
2. **外部リンク**: `target="_blank"` + `rel="noopener noreferrer"` でセキュリティ対策
3. **エラー処理**: URLが存在しない場合は静かに非表示（ユーザビリティ重視）

## 追加データの処理

### 新しいデータセットの追加方法

**1. 個別ファイル処理（複数のMarkdownファイルを別々の章として処理）:**
```bash
# 各ファイル用の個別ディレクトリ作成
mkdir -p extra-input-1 extra-input-2 extra-input-3

# 各ファイルをそれぞれのディレクトリにコピー
cp source/1.md extra-input-1/
cp source/2.md extra-input-2/
cp source/3.md extra-input-3/

# 個別にパイプライン実行
python pipeline.py --input ./extra-input-1 --out ./output-extra-1
python pipeline.py --input ./extra-input-2 --out ./output-extra-2
python pipeline.py --input ./extra-input-3 --out ./output-extra-3
```

**2. WebUIでの表示設定:**
```bash
# 生成されたgraph.jsonをセクション固有のファイル名でコピー
cp output-extra-1/graph.json webui/public/graph_extra-1.json
cp output-extra-2/graph.json webui/public/graph_extra-2.json
cp output-extra-3/graph.json webui/public/graph_extra-3.json
```

**3. Toolbarコンポーネントへの追加:**
```typescript
// webui/src/components/Toolbar.tsx
const sections = [
  { value: 'extra-1', label: 'Extra-1: タイトル1' },
  { value: 'extra-2', label: 'Extra-2: タイトル2' },
  { value: 'extra-3', label: 'Extra-3: タイトル3' },
  // 既存のセクション...
];
```

### WebUIファイル命名規則

- **セクション固有ファイル**: `graph_${sectionId}.json`
  - 例: `graph_sec1-0.json`, `graph_extra-1.json`
- **dataLoaderの動作**: セクションIDに基づいて自動的にファイルを探索
- **フォールバック**: ファイルが見つからない場合は`graph_sec1-0.json`または内蔵データを使用

### 重要な変更履歴

**viewer.html削除（2025-09-11）:**
- 理由: WebUIへの完全移行により不要に
- 対応: pipeline.pyからviewer生成コードを削除
- 影響: 静的HTMLビューアは生成されなくなり、WebUIのみ使用

**複数ファイル処理の修正（2025-09-11）:**
- 問題: pipeline.pyが複数ファイルを1つの統合グラフとして処理
- 解決: 各ファイルを個別ディレクトリに配置して個別処理
- 利点: 各章の概念が独立して管理され、章ごとの特徴が保持される

### デバッグTips

**WebUI開発サーバーのポート確認:**
```bash
# バックグラウンドプロセスの出力確認
BashOutput tool使用、bash_idを指定

# ポートが既に使用中の場合、Viteは自動的に次のポートを選択
# デフォルト: 3000 → 3001 → 3002...
```

**不要なサーバーの停止:**
```bash
# 特定ポートのプロセスを終了
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
```