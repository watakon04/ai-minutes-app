import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（既存の環境変数を上書き）
load_dotenv(override=True)

# APIキーを環境変数から取得
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEYが設定されていません。.envファイルを確認してください。")

genai.configure(api_key=api_key)

def generate_minutes_with_gemini(audio_file_path, max_retries=3):
    print(f"処理開始: {audio_file_path}")

    # 1. 音声ファイルをGeminiのサーバーへアップロード
    print("ファイルをアップロード中...")
    myfile = genai.upload_file(audio_file_path)

    # ファイルの処理が完了するまで待機
    print(f"ファイルの状態: {myfile.state.name}")
    max_wait_time = 300  # 最大5分待機
    wait_time = 0
    while myfile.state.name == "PROCESSING":
        if wait_time >= max_wait_time:
            raise TimeoutError("ファイルの処理がタイムアウトしました")
        print("処理待ち...")
        time.sleep(5)
        wait_time += 5
        myfile = genai.get_file(myfile.name)
        print(f"ファイルの状態: {myfile.state.name}")

    if myfile.state.name == "FAILED":
        raise Exception(f"ファイルの処理に失敗しました: {myfile.state}")

    print(f"アップロード完了: {myfile.uri}")
    print(f"ファイルの最終状態: {myfile.state.name}")

    # 2. モデルの指定
    # 'gemini-2.5-flash' は高速で効率的なモデルです
    model = genai.GenerativeModel("gemini-2.5-flash")

    # 3. 議事録生成の指示
    prompt = """
    あなたはプロの書記です。アップロードされた音声は会議の録音です。
    この内容を聞き取り、以下のフォーマットで詳細な議事録を作成してください。

    # 会議議事録
    - **日時/参加者**: （音声から推測できる場合のみ記載）
    - **決定事項**:
    - **TodoList**: 誰が、いつまでに、何をやるか
    - **議論の概要**: 箇条書きで分かりやすく
    """

    # リトライ処理を追加
    for attempt in range(max_retries):
        try:
            print(f"議事録を生成中... (試行 {attempt + 1}/{max_retries})")
            result = model.generate_content([myfile, prompt])
            return result.text
        except Exception as e:
            print(f"エラー発生 (試行 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait = (attempt + 1) * 5
                print(f"{wait}秒待機してリトライします...")
                time.sleep(wait)
            else:
                raise Exception(f"最大リトライ回数に達しました: {e}")

# --- 実行部分 ---
if __name__ == "__main__":
    # 同じフォルダにある音声ファイル名を指定してください
    audio_path = "meeting.mp3" 
    
    try:
        minutes = generate_minutes_with_gemini(audio_path)
        print("\n" + "="*30)
        print(minutes)
        print("="*30)
    except Exception as e:
        print(f"エラーが発生しました: {e}")