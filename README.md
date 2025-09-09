# Plurality本の概念マップ (Plurality Concept Map)

**🌐 [ライブデモを見る](https://nishio.github.io/plurality-concept-map/)**

AIを活用してPlurality本から概念と関係性を自動抽出し、インタラクティブな概念マップとして可視化するツールです。

## ✨ 主な機能

### 🌐 オンライン版
- **[GitHub Pages デモ](https://nishio.github.io/plurality-concept-map/)**: すぐに使えるライブ版
- **レスポンシブWebUI**: React + TypeScript + D3.jsで構築
- **インタラクティブ可視化**: ズーム、パン、ノード選択が可能

### 📊 高品質な概念抽出
- **多言語対応**: 日本語・英語テキストに対応（日本語原文なら日本語概念を生成）
- **自然言語関係**: 固定タイプではなく自由形式の関係表現
- **証拠付き**: 各概念・関係の根拠となる原文引用を保持

### 🎨 モダンWebUI
- **React 18 + TypeScript**: タイプセーフなモダン開発
- **D3.js v7**: 高性能なグラフ可視化
- **レスポンシブデザイン**: デスクトップ・モバイル対応
- **ハイライト機能**: 選択した概念の関連要素を強調表示
- **日本語最適化**: Noto Sans JPフォントで美しい表示

## 🚀 クイックスタート

### オンライン版（推奨）
[**https://nishio.github.io/plurality-concept-map/**](https://nishio.github.io/plurality-concept-map/) にアクセス

### ローカル開発版

#### 1. セットアップ
```bash
# リポジトリをクローン
git clone https://github.com/nishio/plurality-concept-map.git
cd plurality-concept-map

# Python環境セットアップ
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# WebUI開発環境セットアップ
cd webui
npm install
```

#### 2. 概念マップ生成（Python）
```bash
# 環境変数の設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定

# 基本的な実行
python pipeline.py --out ./output

# カスタム設定
python pipeline.py --input ./my_documents --out ./output --max-concepts 10 --model gpt-4o-mini
```

#### 3. WebUI開発サーバー起動
```bash
cd webui
npm run dev
# http://localhost:3000 でアクセス
```

## 🎯 WebUI機能

### インタラクティブ可視化
- **力学的レイアウト**: D3.jsによる自動配置
- **ズーム・パン**: マウスホイール・ドラッグ操作
- **ノード選択**: クリックで概念詳細を表示
- **エッジ選択**: 関係ラベルクリックで関係詳細を表示

### ハイライト機能
- **概念選択時**: 選択した概念をハイライト表示
- **関係選択時**: 関係するノードとエッジを強調表示
- **視認性向上**: 非関連要素をdimmed表示

### サイドバー詳細表示
- **概念情報**: 定義、エイリアス、証拠テキスト
- **関係情報**: 関係記述、関連概念、信頼度
- **ナビゲーション**: 関連概念へのクリック移動

## 📁 プロジェクト構造

```
plurality-concept-map/
├── 📁 webui/                    # Modern React WebUI
│   ├── 📁 src/
│   │   ├── 📁 components/       # React components
│   │   │   ├── App.tsx         # Main application
│   │   │   ├── D3Graph.tsx     # Interactive graph visualization
│   │   │   ├── ConceptDetails.tsx # Sidebar details panel
│   │   │   └── Toolbar.tsx     # Header and controls
│   │   ├── 📁 types/           # TypeScript definitions
│   │   ├── 📁 utils/           # Data loading utilities
│   ├── 📁 public/              # Static assets and data
│   ├── package.json            # Node.js dependencies
│   └── vite.config.ts          # Vite configuration
├── 📁 docs/                    # GitHub Pages deployment
├── pipeline.py                 # Main concept extraction pipeline
├── llm.py                      # LLM API client
├── prompts.py                  # Prompt templates
├── utils.py                    # Text processing utilities
├── requirements.txt            # Python dependencies
└── CLAUDE.md                   # Development guidelines
```

## 🛠️ 開発・デプロイメント

### WebUI開発
```bash
cd webui
npm run dev          # 開発サーバー（http://localhost:3000）
npm run build        # プロダクションビルド
npm run build:static # 静的HTML生成（全デプロイメント形式）
```

### GitHub Pages デプロイメント
```bash
# ビルドファイルをdocs/にコピー
npm run build
cp -r webui/dist/* docs/

# コミット・プッシュ
git add docs/
git commit -m "Update GitHub Pages deployment"
git push origin main
```

### データ更新
1. `pipeline.py`で新しい概念マップを生成
2. 生成された`graph.json`を`webui/public/`にコピー
3. WebUIを再ビルド・デプロイ

## 📖 概念抽出パイプライン

### 環境変数設定
`.env`ファイル：
```bash
OPENAI_API_KEY=your_api_key_here          # 必須
OPENAI_BASE_URL=https://api.openai.com/v1 # オプション
OPENAI_MODEL=gpt-4o-mini                  # オプション
```

### コマンドラインオプション
| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--input` | `contents/japanese` | 入力ディレクトリ |
| `--out` | 必須 | 出力ディレクトリ |
| `--segment-level` | `h2` | セクション分割レベル (h1/h2/h3) |
| `--max-concepts` | `10` | セクションあたりの最大概念数 |
| `--model` | `gpt-5-mini` | 使用するLLMモデル |

### モデル選択ガイド
| モデル | コスト | 品質 | 推奨用途 |
|--------|--------|------|----------|
| **GPT-5-mini** | 🔴 高 | ⭐⭐⭐⭐⭐ | 最終版・重要文書 |
| **GPT-4o-mini** | 🟡 中 | ⭐⭐⭐⭐ | 通常使用・開発 |
| **GPT-3.5-turbo** | 🟢 低 | ⭐⭐⭐ | テスト・軽量使用 |

## 📄 出力データ形式

### WebUI用データ
- **`graph.json`**: 完全なグラフデータ（WebUI用）
- **`graph_sec3-1.json`**: セクション別データ（サンプル）

### 従来形式
- **`nodes.csv`**: 概念一覧
- **`edges.csv`**: 関係性一覧  
- **`mermaid.md`**: Mermaid記法のダイアグラム

## 🔧 技術仕様

### フロントエンド
- **React 18** + **TypeScript**: 型安全なコンポーネント開発
- **Vite**: 高速開発サーバーとビルドツール
- **D3.js v7**: インタラクティブグラフ可視化
- **CSS Variables**: 一貫したテーマとスタイリング

### バックエンド
- **Python 3.8+**: 概念抽出パイプライン
- **OpenAI API**: GPTモデルによる概念・関係抽出
- **Structured Prompts**: 高精度な構造化データ抽出

### デプロイメント
- **GitHub Pages**: 静的サイトホスティング
- **自動ビルド**: Viteによるプロダクション最適化
- **CDN配信**: 高速グローバルアクセス

## 🤝 コントリビューション

1. **Fork** このリポジトリ
2. **Feature branch** を作成: `git checkout -b feature/amazing-feature`
3. **Commit** 変更: `git commit -m 'Add amazing feature'`
4. **Push** ブランチ: `git push origin feature/amazing-feature`  
5. **Pull Request** を作成

## 📄 ライセンス

MIT License - 商用・非商用問わず自由に使用可能

## 🔗 関連リンク

- **[ライブデモ](https://nishio.github.io/plurality-concept-map/)**
- **[GitHub リポジトリ](https://github.com/nishio/plurality-concept-map)**
- **[Issues・バグ報告](https://github.com/nishio/plurality-concept-map/issues)**

---

**📖 About Plurality**: このツールは[Plurality: The Future of Collaborative Technology and Democracy](https://www.plurality.net/)の概念理解を支援するために開発されました。

**🔥 注意**: GPT-5-miniは高コストです。本格運用前に必ずコスト確認を行ってください。