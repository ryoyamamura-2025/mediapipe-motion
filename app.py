import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os

# --- MediaPipe Pose Landmarker の初期化 ---
@st.cache_resource
def get_pose_model():
    """MediaPipe Pose Landmarker モデルを初期化し、キャッシュします。"""
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    return pose, mp_pose.POSE_CONNECTIONS, mp.solutions.drawing_utils

pose, POSE_CONNECTIONS, mp_drawing = get_pose_model()

# --- 定数とパスの管理 ---
TEMP_DIR = tempfile.gettempdir() # 一時ファイルの保存ディレクトリ

# --- ユーティリティ関数 ---
def process_video_with_pose(video_path):
    """
    指定された動画ファイルに対してMediaPipe Pose Landmarkerでポーズ推定を行い、
    黒背景と元背景の2種類の動画を生成します。
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("どうががひらけません")
        return None, None

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # MP4Vコーデックを使用

    # 一時ファイル名を生成
    output_video_path_black = os.path.join(TEMP_DIR, f"output_black_{os.urandom(8).hex()}.mp4")
    output_video_path_original = os.path.join(TEMP_DIR, f"output_original_{os.urandom(8).hex()}.mp4")

    out_black = cv2.VideoWriter(output_video_path_black, fourcc, fps, (width, height))
    out_original = cv2.VideoWriter(output_video_path_original, fourcc, fps, (width, height))

    analysis_message_placeholder.write("ちょっとまってね...")
    progress_bar = progress_bar_placeholder.progress(0)

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        progress_bar.progress(min(int(frame_count / total_frames * 100), 100))

        image_original_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_original_rgb.flags.writeable = False

        black_background = np.zeros((height, width, 3), dtype=np.uint8)
        image_black_rgb = black_background.copy()
        image_black_rgb.flags.writeable = False

        results = pose.process(image_original_rgb)

        image_original_rgb.flags.writeable = True
        image_black_rgb.flags.writeable = True

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image_original_rgb,
                results.pose_landmarks,
                POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=3, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=3)
            )
            mp_drawing.draw_landmarks(
                image_black_rgb,
                results.pose_landmarks,
                POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=3, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=3)
            )

        out_original.write(cv2.cvtColor(image_original_rgb, cv2.COLOR_RGB2BGR))
        out_black.write(cv2.cvtColor(image_black_rgb, cv2.COLOR_RGB2BGR))

    cap.release()
    out_original.release()
    out_black.release()

    return output_video_path_black, output_video_path_original

def clear_temp_files():
    """セッションステートに保存されている一時動画ファイルを削除します。"""
    for key in ['uploaded_file_path', 'output_video_path_black', 'output_video_path_original']:
        if st.session_state.get(key) and os.path.exists(st.session_state[key]):
            os.unlink(st.session_state[key])
            st.session_state[key] = ""

# --- Streamlit UI ---
st.title("なんのうごき？")

# セッションステートの初期化
if 'output_video_path_black' not in st.session_state:
    st.session_state.output_video_path_black = ""
if 'output_video_path_original' not in st.session_state:
    st.session_state.output_video_path_original = ""
if 'uploaded_file_path' not in st.session_state:
    st.session_state.uploaded_file_path = ""

# --- メッセージとプログレスバーのプレースホルダー ---
info_message_placeholder = st.empty()
analysis_message_placeholder = st.empty()
progress_bar_placeholder = st.empty()
success_message_placeholder = st.empty()

# --- 動画表示用のカラム ---
col1_video, col2_video = st.columns(2)
with col1_video:
    video_placeholder1 = st.empty()
with col2_video:
    video_placeholder2 = st.empty()

# --- ファイルアップローダー ---
uploaded_file = st.file_uploader(" ", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    clear_temp_files() # 新しいファイルがアップロードされたら既存の一時ファイルをクリア

    # メッセージやプログレスバーをリセット
    info_message_placeholder.empty()
    analysis_message_placeholder.empty()
    progress_bar_placeholder.empty()
    success_message_placeholder.empty()
    video_placeholder1.empty()
    video_placeholder2.empty()

    info_message_placeholder.info("どうがありがとう")

    # 一時ファイルに動画を保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
        tfile.write(uploaded_file.read())
        video_path = tfile.name
    st.session_state.uploaded_file_path = video_path

    try:
        output_black, output_original = process_video_with_pose(video_path)

        if output_black and output_original:
            st.session_state.output_video_path_black = output_black
            st.session_state.output_video_path_original = output_original

            info_message_placeholder.empty()
            analysis_message_placeholder.empty()
            progress_bar_placeholder.empty()
            success_message_placeholder.success("おまたせ！")

            video_placeholder1.video(st.session_state.output_video_path_black, format="video/mp4", start_time=0)
        else:
            st.error("動画の処理に失敗しました。")

    except Exception as e:
        info_message_placeholder.empty()
        analysis_message_placeholder.empty()
        progress_bar_placeholder.empty()
        st.error(f"動画処理中にエラーが発生しました: {e}")
    finally:
        # アップロードされた一時動画ファイルを削除
        if os.path.exists(video_path):
            os.unlink(video_path)
            st.session_state.uploaded_file_path = ""

else:
    info_message_placeholder.info("どうがをえらんでね")

# 解析済みの動画が存在する場合に「せいかいは？」ボタンを表示
if st.session_state.output_video_path_black or st.session_state.output_video_path_original:
    col_buttons_above_videos = st.columns(2)
    with col_buttons_above_videos[1]:
        if st.button("せいかいは？"):
            if st.session_state.output_video_path_original and os.path.exists(st.session_state.output_video_path_original):
                video_placeholder2.video(st.session_state.output_video_path_original, format="video/mp4", start_time=0)
            else:
                st.warning("元背景の動画が利用できません。再度ファイルをアップロードしてください。")
