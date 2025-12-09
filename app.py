import os
import time
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（既存の環境変数を上書き）
load_dotenv(override=True)

# ページ設定
st.set_page_config(
    page_title="AI議事録作成ツール",
    page_icon="📝",
    layout="wide"
)

# APIキーを環境変数またはStreamlit secretsから取得
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", None)

if not api_key:
    st.error("⚠️ GOOGLE_API_KEYが設定されていません。")
    st.info("Streamlit Cloudで公開する場合は、Settings > Secrets で `GOOGLE_API_KEY` を設定してください。")
    st.stop()

genai.configure(api_key=api_key)


def generate_minutes_with_gemini(audio_file, max_retries=3):
    """音声ファイルから議事録を生成する"""

    # プログレスバーとステータス表示
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # 1. 音声ファイルをGeminiのサーバーへアップロード
        status_text.text("📤 ファイルをアップロード中...")
        progress_bar.progress(20)

        # 一時ファイルとして保存
        temp_file_path = f"temp_{audio_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(audio_file.getbuffer())

        myfile = genai.upload_file(temp_file_path)

        # ファイルの処理が完了するまで待機
        status_text.text(f"⏳ ファイル処理中... (状態: {myfile.state.name})")
        progress_bar.progress(40)

        max_wait_time = 300  # 最大5分待機
        wait_time = 0
        while myfile.state.name == "PROCESSING":
            if wait_time >= max_wait_time:
                raise TimeoutError("ファイルの処理がタイムアウトしました")
            time.sleep(5)
            wait_time += 5
            myfile = genai.get_file(myfile.name)
            status_text.text(f"⏳ ファイル処理中... ({wait_time}秒経過)")

        if myfile.state.name == "FAILED":
            raise Exception(f"ファイルの処理に失敗しました: {myfile.state}")

        status_text.text("✅ ファイルアップロード完了")
        progress_bar.progress(60)

        # 2. モデルの指定
        # gemini-2.5-flash は高速で効率的なモデルです
        model = genai.GenerativeModel("gemini-2.5-flash")

        # 3. 議事録生成の指示
        prompt = """
        あなたはプロの書記です。アップロードされた音声は会議の録音です。
        この内容を聞き取り、以下のフォーマットで詳細な議事録を作成してください。

        # 会議議事録
        - **日時/参加者**: （音声から推測できる場合のみ記載）
        - **決定事項**:
        - **宿題（ToDo）**: 誰が、いつまでに、何をやるか
        - **議論の概要**: 箇条書きで分かりやすく
        """

        # リトライ処理を追加
        for attempt in range(max_retries):
            try:
                status_text.text(f"🤖 AI議事録を生成中... (試行 {attempt + 1}/{max_retries})")
                progress_bar.progress(80)

                result = model.generate_content([myfile, prompt])

                # 一時ファイルを削除
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

                status_text.text("✅ 議事録生成完了！")
                progress_bar.progress(100)

                return result.text

            except Exception as e:
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 5
                    status_text.text(f"⚠️ エラー発生。{wait}秒後にリトライします...")
                    time.sleep(wait)
                else:
                    raise Exception(f"最大リトライ回数に達しました: {e}")

    except Exception as e:
        # エラー時も一時ファイルを削除
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise e


# メインUI
st.title("📝 AI議事録作成ツール")
st.markdown("音声ファイルをアップロードすると、AIが自動で議事録を作成します。")

# サイドバー
with st.sidebar:
    st.header("使い方")
    st.markdown("""
    1. 会議の音声ファイル（MP3、WAVなど）をアップロード
    2. 「議事録を生成」ボタンをクリック
    3. AIが自動で議事録を作成します

    **対応形式**: MP3, WAV, M4A など

    **処理時間**: 音声の長さにより1〜5分程度
    """)

    st.divider()
    st.markdown("### 📊 モデル情報")
    st.info("Google Gemini 2.0 Flash")

# ファイルアップローダー
uploaded_file = st.file_uploader(
    "音声ファイルをアップロード",
    type=["mp3", "wav", "m4a", "ogg", "flac"],
    help="会議の録音ファイルをアップロードしてください"
)

if uploaded_file is not None:
    # ファイル情報を表示
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📁 ファイル名: {uploaded_file.name}")
    with col2:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📦 ファイルサイズ: {file_size_mb:.2f} MB")

    # 音声プレーヤー
    st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')

    # 生成ボタン
    if st.button("🚀 議事録を生成", type="primary", use_container_width=True):
        try:
            with st.spinner("処理中..."):
                minutes = generate_minutes_with_gemini(uploaded_file)

            # 成功メッセージ
            st.success("✅ 議事録の生成が完了しました！")

            # 議事録を表示
            st.markdown("---")
            st.markdown("## 📄 生成された議事録")
            st.markdown(minutes)

            # ダウンロードボタン
            st.download_button(
                label="📥 議事録をダウンロード",
                data=minutes,
                file_name=f"議事録_{uploaded_file.name.split('.')[0]}.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
            st.info("もう一度お試しいただくか、別の音声ファイルをアップロードしてください。")

else:
    st.info("👆 音声ファイルをアップロードして開始してください")

# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Powered by Google Gemini 2.0 Flash</p>
    </div>
    """,
    unsafe_allow_html=True
)
