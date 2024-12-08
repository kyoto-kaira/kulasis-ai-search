## 開発方法

処理のフローは以下のようになっています。

1. preprocessing：テキストデータの前処理
2. embedding：テキストデータのベクトル化
3. search：候補シラバスの検索
4. reranking：候補シラバスの順位付け

上記のフローを踏まえ、各ステップは「モジュール化」されており、以下のポイントに留意することで効率的かつ柔軟な開発が可能です。

### モジュール構成

`src/` ディレクトリ以下は、以下のような役割別ディレクトリ構成になっています。

```
src/
├── preprocessing/   # 前処理ロジック（テキスト正規化、チャンキングなど）
├── embedding/       # 埋め込み生成（ベクトル化）ロジック
├── search/          # 検索エンジンや検索戦略（FAISS、ハイブリッド検索など）
├── reranking/       # リランキング手法（LLMベース、類似度ベースなど）
├── utils/           # 入出力、ログなどの補助的機能
├── pipeline.py      # パイプラインを統合的に実行するスクリプト
└── run_experiment.py # 実験（パイプライン実行）を管理するスクリプト
```

このようなモジュール構成により、新たな前処理手法や埋め込みモデル、リランキングアルゴリズムを容易に追加・比較できます。

### コンフィグ駆動型アプローチ

`configs/` ディレクトリ下にある YAML ファイル（例：`configs/base_config.yaml`）により、各ステップで使用する手法やパラメータを統一的に管理できます。

```yaml
# 例: configs/base_config.yaml
data:
  input_path: "data/processed/courses_processed.json"
  output_path: "results/default_experiment/reranked_results.json"

preprocessing:
  chunk_size: 512
  normalization: true

embedding:
  model: "text-embedding-ada-002"
  api_key: "your_openai_api_key"

search:
  metadata_filter:
    department: "工学部"
    semester: "前期"
  top_k: 10

reranking:
  method: "llm_reranker"
  model: "gpt-4"
  api_key: "your_openai_api_key"

query:
  example_query: "Pythonでデータサイエンスを学びたい"
```

- **method切り替え**：`reranking.method` を `"llm_reranker"` から `"sim_reranker"` に変更するだけで、LLMを用いたリランキングから類似度ベースのリランキングへ切り替え可能です。
- **パラメータ調整**：`chunk_size` や `top_k`、`metadata_filter`などのパラメータはコンフィグファイル側で容易に変更でき、コードを書き換えることなく異なる条件での実験を実施できます。

### 実験実行の流れ

1. **前処理 (preprocessing)**  
   `src/preprocessing`内の`BasePreprocessor`を継承したクラス（例`SimplePreprocessor`）を利用し、テキストデータを正規化・トークン分割・チャンク化します。  
   このステップでの出力は、後続の埋め込み生成で処理しやすい形に整えられたテキストチャンクのリストです。

2. **埋め込み (embedding)**  
   `src/embedding`内の`BaseEmbedder`を実装したクラス（例：`OpenAIEmbedder`）により、テキストチャンクをベクトルに変換します。  
   ベクトルはFAISSなどのインデックスに登録され、後続の検索で利用されます。

3. **検索 (search)**  
   `src/search`内の`BaseSearcher`を継承したクラス（例：`HybridSearcher`）を使用します。  
   クエリを埋め込みベクトルに変換し、FAISSインデックスとメタデータフィルタリングを組み合わせて、適合しそうなシラバス候補を取得します。

4. **リランキング (reranking)**  
   `src/reranking`内の`BaseReranker`を継承したクラス（`LLMReranker`や`SimReranker`など）を用いて、取得した候補を再評価・再ソートします。  
   - LLMベースのリランキング（`LLMReranker`）：LLMの評価能力を用いて関連度スコアを再計算し、結果を並べ替えます。  
   - 類似度ベースのリランキング（`SimReranker`）：コサイン類似度などのメトリクスを用いて、クエリと結果の関連度を計算・並べ替えます。

### 切り替え・新手法の追加

- **手法切り替え**：  
  `configs/*.yaml` の `reranking.method` を変更することで簡単にリランキング手法を切り替えられます。  
  他のステップ（例えば埋め込みモデル）の切り替えも同様にコンフィグファイル編集のみで対応可能です。

- **新手法の追加**：  
  新しい前処理クラス、埋め込み手法、検索アルゴリズム、リランキング手法を追加したい場合は、
  `src/` 以下の該当ディレクトリに `BaseClass` を継承した新しいクラスを作成し、`__init__.py`でエクスポートしてください。  
  その後、コンフィグファイルの対応するパラメータを更新することで、新規手法をすぐに実験へ組み込めます。

### 実験の実行例

```bash
# 基本的な実験実行
python src/run_experiment.py configs/base_config.yaml default_experiment
```

```bash
# sim_reranker を使用した実験実行
python src/run_experiment.py configs/sim_reranker_config.yaml sim_reranker_experiment
```

実験結果（リランキング後のJSONなど）は `results/<experiment_id>/` 以下に保存されます。  
`config_used.yaml` と `reranked_results.json` を併せて管理することで、後から条件別の結果比較が容易になります。



## ライブラリを追加する場合

1. `requirements.txt` に追加したいライブラリを追記する
2. 以下のコマンドを実行する

```bash
uv pip install -r requirements.txt --system
```
