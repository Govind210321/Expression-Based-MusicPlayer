import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2 
import numpy as np 
import mediapipe as mp 
from keras.models import load_model
import webbrowser

model  = load_model(r"F:\Downloads\Moodify-main\Moodify-main\model.h5")
label = np.load(r"F:\Downloads\Moodify-main\Moodify-main\labels.npy")
holistic = mp.solutions.holistic
hands = mp.solutions.hands
holis = holistic.Holistic()
drawing = mp.solutions.drawing_utils

st.header("Expression Based Music Player")
st.header("final year project")
print("hi")

if "run" not in st.session_state:
	st.session_state["run"] = "true"

if "step2" not in st.session_state:
	st.session_state["step2"] = "false"
try:
	emotion = np.load("emotion.npy")[0]
except:
	emotion=""


if not(emotion):
	st.session_state["run"] = "true"
else:
	st.session_state["run"] = "false"

import time
def progress():
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.05)
        my_bar.progress(percent_complete + 1, text=progress_text)
	

class EmotionProcessor:
	def recv(self, frame):
		frm = frame.to_ndarray(format="bgr24")

		##############################
		frm = cv2.flip(frm, 1)

		res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

		lst = []

		if res.face_landmarks:
			for i in res.face_landmarks.landmark:
				lst.append(i.x - res.face_landmarks.landmark[1].x)
				lst.append(i.y - res.face_landmarks.landmark[1].y)

			if res.left_hand_landmarks:
				for i in res.left_hand_landmarks.landmark:
					lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
					lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
			else:
				for i in range(42):
					lst.append(0.0)

			if res.right_hand_landmarks:
				for i in res.right_hand_landmarks.landmark:
					lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
					lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
			else:
				for i in range(42):
					lst.append(0.0)

			lst = np.array(lst).reshape(1,-1)

			pred = label[np.argmax(model.predict(lst))]

			print(pred)
			cv2.putText(frm, pred, (50,50),cv2.FONT_ITALIC, 1, (255,0,0),2)

			np.save("emotion.npy", np.array([pred]))

			
		#drawing.draw_landmarks(frm, res.face_landmarks, holistic.FACEMESH_TESSELATION,
		#						landmark_drawing_spec=drawing.DrawingSpec(color=(0,0,255), thickness=-1, circle_radius=1)) #,
								#connection_drawing_spec=drawing.DrawingSpec(thickness=1))
		#drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
		#drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)


		##############################

		return av.VideoFrame.from_ndarray(frm, format="bgr24")

btn1 = st.button("capture the image to detect expression")

if btn1 and st.session_state["run"] == "false":

    progress()
    st.session_state["step2"] = "true"

print(btn1, st.session_state["run"])
if st.session_state["step2"] == "true":

    webrtc_streamer(key="key", 
	    desired_playing_state=True, 
	    video_processor_factory=EmotionProcessor)

    lang = st.text_input("Language")

    btn1 = st.button("Recommend me video")

    from streamlit_player import st_player
    if btn1:
        #webbrowser.open(f"https://www.youtube.com/results?search_query={lang}+{emotion}+song")
        st_player("https://youtu.be/CmSKVW1v0xM")
        np.save("emotion.npy", np.array([""]))
        st.session_state["run"] = "false"

    btn2 = st.button("Recommend me music")

    if btn2:
        #webbrowser.open(f"https://open.spotify.com/search/{lang}%20{emotion}")
        st_player("https://soundcloud.com/imaginedragons/demons")
        np.save("emotion.npy", np.array([""]))
        st.session_state["run"] = "false"