# AI議事録作成ツール

音声ファイルをアップロードするだけで、AIが自動で議事録を作成するWebアプリケーションです。

## 機能

- 音声ファイル（MP3、WAV、M4Aなど）から自動で議事録を生成
- 決定事項、宿題（ToDo）、議論の概要を整理
- 生成した議事録をMarkdown形式でダウンロード可能
- Google Gemini 2.0 Flashを使用した高精度な文字起こし

## デモ

（Streamlit Cloudにデプロイ後、URLを記載）

## ローカルでの実行方法

### 必要要件

- Python 3.10以上
- Google Gemini API キー

### セットアップ

1. リポジトリをクローン

```bash
git clone https://github.com/YOUR_USERNAME/AIsummary.git
cd AIsummary
```

2. 仮想環境を作成・有効化

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

4. 環境変数を設定

`.env`ファイルを作成し、Google Gemini APIキーを設定：

```
GOOGLE_API_KEY=your_api_key_here
```

5. アプリを起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## Streamlit Cloudでのデプロイ

1. GitHubにこのリポジトリをプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud)にアクセス
3. 「New app」をクリック
4. リポジトリ、ブランチ、メインファイル（`app.py`）を選択
5. 「Advanced settings」で環境変数 `GOOGLE_API_KEY` を設定
6. 「Deploy」をクリック

## 使い方

1. アプリを開く
2. 音声ファイルをアップロード
3. 「議事録を生成」ボタンをクリック
4. 生成された議事録を確認・ダウンロード

## 対応音声形式

- MP3
- WAV
- M4A
- OGG
- FLAC

## 技術スタック

- **フロントエンド**: Streamlit
- **AI**: Google Gemini 2.0 Flash
- **言語**: Python 3.12

## ライセンス

MIT License

## 作成者

wataru
