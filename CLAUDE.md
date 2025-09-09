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