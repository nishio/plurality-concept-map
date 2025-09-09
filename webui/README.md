# 概念マッピングツール (LLM Concept Mapping Tool)

AIを活用して文章から概念と関係性を自動抽出し、インタラクティブな概念マップを生成するツールです。

## ✨ 主な機能

### 📊 高品質な概念抽出
- **多言語対応**: 日本語・英語テキストに対応（日本語原文なら日本語概念を生成）
- **階層分類**: Core/Supplementary/Advanced概念の自動分類
- **証拠付き**: 各概念・関係の根拠となる原文引用を保持
- **エイリアス対応**: 別名・関連用語を自動識別

### 🔗 関係性の可視化
- **8種類の関係タイプ**: is_a, part_of, prerequisite_of, example_of, contrasts_with, parameter_of, returns, uses
- **信頼度付き**: 各関係に0.0-1.0の信頼度スコア
- **証拠ベース**: 関係性の根拠となる文章を保持

### 🎨 高機能ビューア
- **改良版ビューア**: 日本語最適化、詳細パネル、関係性ラベル表示
- **インタラクティブ操作**: ズーム、ドラッグ、フィルタリング
- **レスポンシブデザイン**: デスクトップ・モバイル対応

### 🤖 複数LLMモデル対応
- **GPT-5-mini**: 最高品質（高コスト）
- **GPT-4o-mini**: バランス重視（推奨）
- **GPT-3.5-turbo**: 軽量・高速

## 🚀 クイックスタート

### 1. セットアップ
```bash
# 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

### 2. 基本的な実行
```bash
# デフォルト設定（contents/japanese から読み込み）
python pipeline.py --out ./output

# カスタム入力ディレクトリ
python pipeline.py --input ./my_documents --out ./output

# 概念数とモデルを指定
python pipeline.py --out ./output --max-concepts 10 --model gpt-4o-mini
```

### 3. 結果の確認
```bash
# ローカルサーバー起動
cd output
python -m http.server 8000

# ブラウザで確認
# 改良版: http://localhost:8000/viewer_enhanced.html
# 従来版: http://localhost:8000/viewer.html
```

## 📖 詳細な使用方法

### 環境変数設定
`.env`ファイルに以下を設定：
```bash
# 必須
OPENAI_API_KEY=your_api_key_here

# オプション
OPENAI_BASE_URL=https://api.openai.com/v1  # デフォルト
OPENAI_MODEL=gpt-4o-mini                   # デフォルト
```

### コマンドラインオプション

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--input` | `contents/japanese` | 入力ディレクトリ |
| `--out` | 必須 | 出力ディレクトリ |
| `--segment-level` | `h2` | セクション分割レベル (h1/h2/h3) |
| `--max-concepts` | `15` | セクションあたりの最大概念数 |
| `--cross-section` | `false` | セクション間の関係分析 |
| `--model` | `gpt-4o-mini` | 使用するLLMモデル |

### 入力ファイル形式
- **形式**: Markdown (.md)
- **構造**: 階層的な見出し構造を推奨
- **エンコーディング**: UTF-8
- **言語**: 日本語・英語に対応

## 🎯 モデル選択ガイド

### 💰 コストと品質のバランス

| モデル | コスト | 品質 | 推奨用途 |
|--------|--------|------|----------|
| **GPT-5-mini** | 🔴 高 | ⭐⭐⭐⭐⭐ | 最終版・重要文書 |
| **GPT-4o-mini** | 🟡 中 | ⭐⭐⭐⭐ | 通常使用・開発 |
| **GPT-3.5-turbo** | 🟢 低 | ⭐⭐⭐ | テスト・軽量使用 |

### 📝 日本語対応の特徴

**GPT-5-mini**: 
- 日本語概念ラベルを正確に生成
- ⿻（ユニコード記号）などの細かい要素も抽出
- 複数の詳細な証拠引用
- 6つの関係性を高精度で抽出

**GPT-4o-mini**:
- 日本語ラベルで適切に応答
- 構造的な理解が良好
- 4つ程度の関係性を抽出

**GPT-3.5-turbo**:
- 日本語プロンプトでも英語ラベルを生成する場合がある
- より一般的な概念を抽出

### ⚠️ コスト管理
```bash
# 開発・テスト時は軽量モデル
python pipeline.py --model gpt-4o-mini --max-concepts 5

# 最終版のみ高品質モデル
python pipeline.py --model gpt-5-mini --max-concepts 15
```

## 📁 出力ファイル

### データファイル
- **`graph.json`**: 完全なグラフデータ（証拠付き）
- **`nodes.csv`**: 概念一覧（ID, ラベル, 階層, 定義, エイリアス, 証拠）
- **`edges.csv`**: 関係性一覧（ソース, ターゲット, タイプ, 信頼度, 証拠）
- **`mermaid.md`**: Mermaid記法のダイアグラム

### ビューアファイル
- **`viewer_enhanced.html`**: 🌟 改良版ビューア（推奨）
  - 日本語最適化UI
  - 詳細パネル
  - 証拠データ表示
  - 関係性ラベル表示
- **`viewer.html`**: 従来版ビューア

## 🎨 改良版ビューアの特徴

### 📱 ユーザーインターフェース
- **Noto Sans JPフォント**: 美しい日本語表示
- **レスポンシブデザイン**: PC・タブレット・スマートフォン対応
- **モダンデザイン**: CSS Variables使用の洗練されたUI

### 📊 データ表示
- **詳細パネル**: 概念クリックで左サイドバーに詳細表示
- **証拠引用**: 概念・関係の根拠となる原文を表示
- **エイリアス表示**: 別名・関連用語をタグ形式で表示
- **階層表示**: Core/Supplementary/Advancedを色分け

### 🎛️ 操作機能
- **ズーム操作**: +/-/⌂ボタンによる拡大縮小
- **ドラッグ&ドロップ**: ノードの自由配置
- **フィルタリング**: 階層別の表示切替
- **関係性表示**: エッジ上に関係タイプを表示

## 🛠️ 開発・カスタマイズ

### プロジェクト構造
```
conceptmap/
├── pipeline.py          # メインパイプライン
├── llm.py              # LLM API クライアント
├── prompts.py          # プロンプトテンプレート
├── utils.py            # ユーティリティ関数
├── viewer.html         # 従来版ビューア
├── viewer_enhanced.html # 改良版ビューア
├── requirements.txt    # Python依存関係
└── README.md          # このファイル
```

### カスタマイズポイント

#### 1. 概念抽出のカスタマイズ
`prompts.py`の`SECTION_CONCEPTS_PROMPT`を編集：
```python
# 概念の定義基準を調整
# 証拠の要求レベルを変更
# 階層分類の基準を修正
```

#### 2. 関係性タイプの追加
`pipeline.py`の`RELATION_TYPES`を編集：
```python
RELATION_TYPES = [
    "is_a", "part_of", "prerequisite_of", "example_of",
    "contrasts_with", "parameter_of", "returns", "uses",
    "your_custom_relation"  # 追加
]
```

#### 3. ビューアのカスタマイズ
`viewer_enhanced.html`のCSS・JavaScript部分を編集：
- 色・フォント・レイアウトの調整
- 新しいインタラクション機能の追加
- データ表示形式の変更

### デバッグ機能
現在のバージョンには以下のデバッグ出力が含まれています：
```python
print(f"Relations response for {sec.title}: {rtxt[:500]}...")
```

### APIエラー対応
- **429 Too Many Requests**: レート制限 → モデル変更やリクエスト間隔調整
- **400 Bad Request**: パラメータエラー → モデル固有の制約確認
- **insufficient_quota**: 残高不足 → OpenAIダッシュボードで残高追加

## 🔧 トラブルシューティング

### よくある問題

#### 1. 関係性が生成されない
```bash
# 原因: 日本語ラベルのID化問題
# 解決: utils.pyのslugify_id関数でUnicode対応済み
```

#### 2. 日本語文字が文字化け
```bash
# 原因: フォント・エンコーディング問題  
# 解決: 改良版ビューアではNoto Sans JP使用
```

#### 3. API呼び出しエラー
```bash
# 環境変数確認
echo $OPENAI_API_KEY

# 残高確認（OpenAI Dashboard）
# モデル名確認（最新のモデル名を使用）
```

## 📄 ライセンス

MIT License - 商用・非商用問わず自由に使用可能

## 🛠️ 開発環境セットアップ

```bash
git clone [repository-url]
cd conceptmap
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

**🔥 重要**: GPT-5-miniは高コストです。本格運用前に必ずコスト確認を行ってください。