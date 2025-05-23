import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import subprocess

st.title("なんのうごき？🕺🕺")
video_data = st.file_uploader("", ['mp4','mov', 'avi'])

info_message_placeholder = st.empty()
analysis_message_placeholder = st.empty()
progress_bar_placeholder = st.empty()
success_message_placeholder = st.empty()

temp_file_to_save = './temp_file_1.mp4'
temp_file_result  = './temp_file_2.mp4'
temp_file_result_black  = './temp_file_black.mp4'

# func to save BytesIO on a drive
def write_bytesio_to_file(filename, bytesio):
    """
    Write the contents of the given BytesIO to a file.
    Creates the file or overwrites the file if it does
    not exist yet. 
    """
    with open(filename, "wb") as outfile:
        # Copy the BytesIO stream to the output file
        outfile.write(bytesio.getbuffer())

# mediapipe の初期化
@st.cache_resource
def get_pose_model():
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    return pose, mp_pose.POSE_CONNECTIONS, mp.solutions.drawing_utils

pose, POSE_CONNECTIONS, mp_drawing = get_pose_model()

if video_data:
    # save uploaded video to disc
    write_bytesio_to_file(temp_file_to_save, video_data)

    # read it with cv2.VideoCapture(), 
    # so now we can process it with OpenCV functions
    try:
        cap = cv2.VideoCapture(temp_file_to_save)
        info_message_placeholder.info("💁どうがありがとう")
        if not cap.isOpened():
            info_message_placeholder.empty() # メッセージをクリア
            analysis_message_placeholder.empty()
            progress_bar_placeholder.empty()
            st.error("💩どうががひらけません！ぱぱに言ってね🧔")
            st.stop()

        # grab some parameters of video to use them for writing a new, processed video
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_fps = cap.get(cv2.CAP_PROP_FPS)  ##<< No need for an int
        st.write(width, height, frame_fps)
        
        # specify a writer to write a processed video to a disk frame by frame
        fourcc_mp4 = cv2.VideoWriter_fourcc(*'mp4v')
        out_mp4 = cv2.VideoWriter(temp_file_result, fourcc_mp4, frame_fps, (width, height))
        out_black = cv2.VideoWriter(temp_file_result_black, fourcc_mp4, frame_fps, (width, height))

        # プログレスバー用
        analysis_message_placeholder.write("⌛️ちょっとまってね...☕")
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        progress_bar = progress_bar_placeholder.progress(0) # プレースホルダーにプログレスバーを表示

        while True:
            ret,frame = cap.read()
            if not ret: break

            frame_count += 1
            progress_bar.progress(min(int(frame_count / total_frames * 100), 100))

            # 黒背景フレームを作成
            black_background = frame.copy()*0

            # ポーズ推定の実行（オリジナル画像に対して行う）
            results = pose.process(frame)

            if results.pose_landmarks:
                # 元背景の画像にランドマークを描画
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=3, circle_radius=3),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=3)
                )
                
                # 黒背景の画像にランドマークを描画
                mp_drawing.draw_landmarks(
                    black_background,
                    results.pose_landmarks,
                    POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=3, circle_radius=3),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=3)
                )

            # # 各動画ファイルにフレームを書き込み
            out_mp4.write(frame)
            out_black.write(black_background)

            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) ##<< Generates a grayscale (thus only one 2d-array)
            # out_mp4.write(gray)
        
        ## Close video files
        out_mp4.release()
        out_black.release() 
        cap.release()

        # 解析完了後のメッセージとプログレスバーをクリア
        info_message_placeholder.empty()
        analysis_message_placeholder.empty()
        progress_bar_placeholder.empty() # プログレスバーをクリア
        success_message_placeholder.success("🦁おまたせ！")

        ## Reencodes video to H264 using ffmpeg
        ##  It calls ffmpeg back in a terminal so it fill fail without ffmpeg installed
        ##  ... and will probably fail in streamlit cloud
        convertedVideo = "./testh264.mp4"
        subprocess.call(args=f"ffmpeg -y -i {temp_file_result} -c:v libx264 {convertedVideo}".split(" "))
        convertedVideo_black = "./testh264_black.mp4"
        subprocess.call(args=f"ffmpeg -y -i {temp_file_result_black} -c:v libx264 {convertedVideo_black}".split(" "))
        
        ## Show results
        col1, col2 = st.columns(2)
        mov1, mov2 = st.columns(2)
        col1.write("なんだろう❓️🤔🤔🤔")
        mov1.video(convertedVideo_black)

        with col2:
            if st.button("💡せいかいをみる"):
                col2.write("こんなうごきでした✨️")
                mov2.video(convertedVideo)

    except Exception as e:
        info_message_placeholder.empty() # メッセージをクリア
        analysis_message_placeholder.empty()
        progress_bar_placeholder.empty()
        st.error(f"エラー！☹️ぱぱに言ってね: {e}")

else:
    info_message_placeholder.info("👧どうがをえらんでね🎦")
