## 環境構築方法

### 使用環境

|  | ツール | バージョン (括弧の場合は不問) |
| --- | --- | --- |
| 言語 | Python | 3.11.11 |
| コンテナ化ツール | Docker | (27.3.1) |
| パッケージ管理ツール | uv-pip | 0.5.5 |
| ビルドツール | make | (3.81) |
| ソースコード管理 | git | (2.39.5) |

### セットアップ

1. 下記を参考にしてgit, docker, makeを使えるようにする（すでに使える人は飛ばす）

  - 使えるようになっているか確認する方法
    - 以下のコマンドを実行して、バージョンが表示されればOK

      ```
      git --version
      docker --version
      make --version
      ```

  - **Windowsの人向け**
    - git: https://prog-8.com/docs/git-env-win
    - Docker: https://qiita.com/zembutsu/items/a98f6f25ef47c04893b3
      - 「hello-world コンテナの実行」の手前まででOK
    - make: https://redhologerbera.hatenablog.com/entry/2021/05/16/163305

  - **Macの人向け**
    - 以下のコマンドを実行するだけ。以上。

      ```
      brew install git
      brew install --cask docker
      brew install make
      ```

2. このリポジトリをクローンする

  ```
  git clone https://github.com/kyoto-kaira/kulasis-ai-search.git
  ```
  
3. 実験用ディレクトリに移動する

  ```
  cd kulasis-ai-search/experiments
  ```

4. makeコマンドを実行して、Dockerイメージをビルドする
  - (注) Docker Desktopを起動しておくこと。

  ```
  make build
  ```

5. Dockerコンテナを起動する

  ```
  make run
  ```

  - 以下のような表示が出ればOK

    ```
    root@<コンテナID>:/app#
    ```
  
6. 必要に応じて、APIキーを`.env`に設定する
  - 記述例は`.env.example`を参照（このファイルは編集しないでください）
  - 下記で`.env`ファイルの内容を読み込むことができます
  
    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```

### ライブラリを追加する場合

1. `requirements.txt` に追加したいライブラリを追記する
2. 以下のコマンドを実行する

  ```
  uv pip install -r requirements.txt --system
  ```

## 開発の進め方

- Notionページ「[【マニュアル】開発の進め方](https://www.notion.so/kyoto-kaira/156c86ea531e803c8ecde278392df13c?pvs=4)」を参照してください。


## 実験の実行例

### コマンド上で実行する場合

- 複数クエリに対して実験を行いたい場合
- wandbに実験を記録したい場合

```
python src/run_experiment.py configs/base_config.yaml default_experiment
```

### Streamlitで実行する場合

- アプリケーション上で実験を行いたい場合

```
streamlit run app.py
```


