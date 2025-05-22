import streamlit as st
import cv2
import subprocess

video_data = st.file_uploader("Upload file", ['mp4','mov', 'avi'])

temp_file_to_save = './temp_file_1.mp4'
temp_file_result  = './temp_file_2.mp4'

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

if video_data:
    # save uploaded video to disc
    write_bytesio_to_file(temp_file_to_save, video_data)

    # read it with cv2.VideoCapture(), 
    # so now we can process it with OpenCV functions
    cap = cv2.VideoCapture(temp_file_to_save)

    # grab some parameters of video to use them for writing a new, processed video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_fps = cap.get(cv2.CAP_PROP_FPS)  ##<< No need for an int
    st.write(width, height, frame_fps)
    
    # specify a writer to write a processed video to a disk frame by frame
    fourcc_mp4 = cv2.VideoWriter_fourcc(*'mp4v')
    out_mp4 = cv2.VideoWriter(temp_file_result, fourcc_mp4, frame_fps, (width, height),isColor = False)
   
    while True:
        ret,frame = cap.read()
        if not ret: break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) ##<< Generates a grayscale (thus only one 2d-array)
        out_mp4.write(gray)
    
    ## Close video files
    out_mp4.release()
    cap.release()

    ## Reencodes video to H264 using ffmpeg
    ##  It calls ffmpeg back in a terminal so it fill fail without ffmpeg installed
    ##  ... and will probably fail in streamlit cloud
    convertedVideo = "./testh264.mp4"
    subprocess.call(args=f"ffmpeg -y -i {temp_file_result} -c:v libx264 {convertedVideo}".split(" "))
    
    ## Show results
    col1,col2 = st.columns(2)
    col1.header("Original Video")
    col1.video(temp_file_to_save)
    col2.header("Output from OpenCV (MPEG-4)")
    col2.video(temp_file_result)
    col2.header("After conversion to H264")
    col2.video(convertedVideo)

# import streamlit as st
# import cv2
# import mediapipe as mp
# import numpy as np
# import tempfile
# import os
# import shutil

# # MediaPipe Pose Landmarker の初期化
# @st.cache_resource
# def get_pose_model():
#     mp_pose = mp.solutions.pose
#     pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
#     return pose, mp_pose.POSE_CONNECTIONS, mp.solutions.drawing_utils

# pose, POSE_CONNECTIONS, mp_drawing = get_pose_model()

# st.title("なんのうごき？")

# # 動画の保存パスをセッションステートで管理
# if 'output_video_path_black' not in st.session_state: # 黒背景用
#     st.session_state.output_video_path_black = ""
# if 'output_video_path_original' not in st.session_state: # 元背景用
#     st.session_state.output_video_path_original = ""
# if 'uploaded_file_path' not in st.session_state:
#     st.session_state.uploaded_file_path = ""

# # --- メッセージとプログレスバーのプレースホルダーを定義 ---
# # これらを動画表示カラムよりも上に配置
# info_message_placeholder = st.empty()
# analysis_message_placeholder = st.empty()
# progress_bar_placeholder = st.empty()
# success_message_placeholder = st.empty()

# # --- 動画表示用のカラムを作成 (メッセージなどの後に配置) ---
# # st.subheader("解析結果動画")
# col1_video, col2_video = st.columns(2)

# # 動画1の表示エリア
# with col1_video:
#     # ここには初期状態では何も表示されない
#     # 解析完了後に動画がレンダリングされる
#     video_placeholder1 = st.empty()

# # 動画2の表示エリア
# with col2_video:
#     # ここには初期状態では何も表示されない
#     # ボタン押下後に動画がレンダリングされる
#     video_placeholder2 = st.empty()


# uploaded_file = st.file_uploader(" ", type=["mp4", "mov", "avi"])


# if uploaded_file is not None:
#     # 新しいファイルがアップロードされた場合、以前の一時ファイルを削除
#     if st.session_state.uploaded_file_path and os.path.exists(st.session_state.uploaded_file_path):
#         os.unlink(st.session_state.uploaded_file_path)
#     if st.session_state.output_video_path_black and os.path.exists(st.session_state.output_video_path_black):
#         os.unlink(st.session_state.output_video_path_black)
#     if st.session_state.output_video_path_original and os.path.exists(st.session_state.output_video_path_original):
#         os.unlink(st.session_state.output_video_path_original)
    
#     # メッセージやプログレスバーをリセット
#     info_message_placeholder.empty()
#     analysis_message_placeholder.empty()
#     progress_bar_placeholder.empty()
#     success_message_placeholder.empty()
#     video_placeholder1.empty() # 古い動画表示をクリア
#     video_placeholder2.empty() # 古い動画表示をクリア

#     info_message_placeholder.info("どうがありがとう")

#     # 一時ファイルに動画を保存
#     tfile = tempfile.NamedTemporaryFile(delete=False)
#     tfile.write(uploaded_file.read())
#     video_path = tfile.name
#     tfile.close()
#     st.session_state.uploaded_file_path = video_path

#     output_video_path_black = ""
#     output_video_path_original = ""

#     try:
#         cap = cv2.VideoCapture(video_path)

#         if not cap.isOpened():
#             info_message_placeholder.empty() # メッセージをクリア
#             analysis_message_placeholder.empty()
#             progress_bar_placeholder.empty()
#             st.error("どうががひらけません")
#             os.unlink(video_path)
#             st.session_state.uploaded_file_path = ""
#             st.stop()
            
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         fps = int(cap.get(cv2.CAP_PROP_FPS))
        
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#         # 黒背景の出力動画ファイルを設定
#         output_video_path_black = tempfile.NamedTemporaryFile(suffix="_black.mp4", delete=False).name
#         out_black = cv2.VideoWriter(output_video_path_black, fourcc, fps, (width, height))

#         # 元背景の出力動画ファイルを設定
#         output_video_path_original = tempfile.NamedTemporaryFile(suffix="_original.mp4", delete=False).name
#         out_original = cv2.VideoWriter(output_video_path_original, fourcc, fps, (width, height))


#         analysis_message_placeholder.write("ちょっとまってね...")
#         progress_bar = progress_bar_placeholder.progress(0) # プレースホルダーにプログレスバーを表示
#         frame_count = 0
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             frame_count += 1
#             progress_bar.progress(min(int(frame_count / total_frames * 100), 100))

#             # オリジナルフレームをRGBに変換
#             image_original_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             image_original_rgb.flags.writeable = False

#             # 黒背景フレームを作成
#             black_background = np.zeros((height, width, 3), dtype=np.uint8)
#             image_black_rgb = black_background.copy()
#             image_black_rgb.flags.writeable = False


#             # ポーズ推定の実行（オリジナル画像に対して行う）
#             results = pose.process(image_original_rgb)

#             # 描画のために書き込み可能に戻す
#             image_original_rgb.flags.writeable = True
#             image_black_rgb.flags.writeable = True


#             if results.pose_landmarks:
#                 # 元背景の画像にランドマークを描画
#                 mp_drawing.draw_landmarks(
#                     image_original_rgb,
#                     results.pose_landmarks,
#                     POSE_CONNECTIONS,
#                     mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=3, circle_radius=3),
#                     mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=3)
#                 )
                
#                 # 黒背景の画像にランドマークを描画
#                 mp_drawing.draw_landmarks(
#                     image_black_rgb,
#                     results.pose_landmarks,
#                     POSE_CONNECTIONS,
#                     mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=3, circle_radius=3),
#                     mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=3)
#                 )

#             # 各動画ファイルにフレームを書き込み
#             out_original.write(cv2.cvtColor(image_original_rgb, cv2.COLOR_RGB2BGR))
#             out_black.write(cv2.cvtColor(image_black_rgb, cv2.COLOR_RGB2BGR))


#         cap.release()
#         out_original.release()
#         out_black.release()
        
#         # 解析完了後のメッセージとプログレスバーをクリア
#         info_message_placeholder.empty()
#         analysis_message_placeholder.empty()
#         progress_bar_placeholder.empty() # プログレスバーをクリア
#         success_message_placeholder.success("おまたせ！")
        
#         st.session_state.output_video_path_black = output_video_path_black
#         st.session_state.output_video_path_original = output_video_path_original

#         # 解析完了後、動画1（黒背景）を即時再生
#         video_placeholder1.video(st.session_state.output_video_path_black, format="video/mp4", start_time=0)


#     except Exception as e:
#         info_message_placeholder.empty() # メッセージをクリア
#         analysis_message_placeholder.empty()
#         progress_bar_placeholder.empty()
#         st.error(f"動画処理中にエラーが発生しました: {e}")
#     finally:
#         if os.path.exists(video_path):
#             os.unlink(video_path)
#             st.session_state.uploaded_file_path = ""

# else:
#     info_message_placeholder.info("どうがをえらんでね")

# if (st.session_state.output_video_path_black and os.path.exists(st.session_state.output_video_path_black)) or \
#    (st.session_state.output_video_path_original and os.path.exists(st.session_state.output_video_path_original)):
    
#     # ボタンは動画カラムの上に配置
#     col_buttons_above_videos = st.columns(2) # ボタン用のカラムを新しく定義

#     with col_buttons_above_videos[1]: # 動画2のボタンは右側に配置
#         if st.button("せいかいは？"):
#             # ボタンを押したときに動画2を再生
#             video_placeholder2.video(st.session_state.output_video_path_original, format="video/mp4", start_time=0)
            
