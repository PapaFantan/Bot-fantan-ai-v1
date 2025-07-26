import streamlit as st
from collections import Counter
import joblib
import os
import json
import matplotlib.pyplot as plt

# Config
st.set_page_config(page_title="Fantan AI Demo", page_icon="🎲")

# Load AI model
MODEL_PATH = "fantan_model.pkl"
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

# Load demo session data
SESSION_FILE = "demo_sessions.json"
if os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "r") as f:
        demo_sessions = json.load(f)
else:
    demo_sessions = {}

# Telegram ID
telegram_id = st.text_input("📲 Nhập Telegram ID để bắt đầu:")

if not telegram_id:
    st.stop()

# Khởi tạo phiên nếu chưa có
if telegram_id not in demo_sessions:
    demo_sessions[telegram_id] = {"played": 0, "unlocked": False}

# Nếu vượt quá 40 ván và chưa có key
if demo_sessions[telegram_id]["played"] >= 40 and not demo_sessions[telegram_id]["unlocked"]:
    key = st.text_input("🔑 Nhập key để tiếp tục chơi:")
    if key == "papa-fantan-206":
        st.success("✅ Key đúng! Bạn có thể tiếp tục chơi.")
        demo_sessions[telegram_id]["unlocked"] = True
        with open(SESSION_FILE, "w") as f:
            json.dump(demo_sessions, f)
    else:
        st.error("❌ Key sai! Vui lòng liên hệ admin.")
        st.stop()

# Giao diện chính
st.title("🎲 BOT Fantan AI Unlock Key")
if "history" not in st.session_state:
    st.session_state.history = []

# Tăng lượt chơi (chỉ khi chọn số)
def click_number(n):
    st.session_state.history.append(n)
    demo_sessions[telegram_id]["played"] += 1
    with open(SESSION_FILE, "w") as f:
        json.dump(demo_sessions, f)
    st.rerun()

# Reset / Undo
def undo_last():
    if st.session_state.history:
        st.session_state.history.pop()
        demo_sessions[telegram_id]["played"] -= 1
        with open(SESSION_FILE, "w") as f:
            json.dump(demo_sessions, f)
        st.rerun()

def reset_all():
    st.session_state.history = []
    demo_sessions[telegram_id]["played"] = 0
    with open(SESSION_FILE, "w") as f:
        json.dump(demo_sessions, f)
    st.rerun()

# Hiển thị kết quả
st.markdown(f"**Số ván đã chơi:** {demo_sessions[telegram_id]['played']} / 40")
st.markdown("### 📜 Lịch sử kết quả")
if st.session_state.history:
    result_str = " | ".join(str(num) for num in st.session_state.history[-20:])
    st.markdown(f"<div style='font-size:24px'>{result_str}</div>", unsafe_allow_html=True)
else:
    st.markdown("*Chưa có kết quả.*")

# Các nút
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1: st.button("1️⃣", on_click=click_number, args=(1,))
with col2: st.button("2️⃣", on_click=click_number, args=(2,))
with col3: st.button("3️⃣", on_click=click_number, args=(3,))
with col4: st.button("4️⃣", on_click=click_number, args=(4,))
with col5: st.button("🔙 Undo", on_click=undo_last)
with col6: st.button("🧹 Reset", on_click=reset_all)

# Dự đoán nếu đủ dữ liệu
if len(st.session_state.history) >= 10:
    freq = Counter(st.session_state.history[-10:])
    top = freq.most_common()
    pred_1 = top[0][0]
    pred_2 = [x[0] for x in top[:2]]
    pred_3 = [x[0] for x in top[:3]]

    st.markdown("### 🔮 Dự đoán thống kê")
    st.markdown(f"- Khả năng cao nhất: **{pred_1}**")
    st.markdown(f"- Top 2: **{', '.join(map(str, pred_2))}**")
    st.markdown(f"- Top 3: **{', '.join(map(str, pred_3))}**")

    # Xác suất thống kê
    total = sum(freq.values())
    st.markdown("### 📊 Tỉ lệ thống kê")
    for i in range(1, 5):
        percent = round(freq.get(i, 0) / total * 100, 1)
        st.markdown(f"- Số {i}: {percent}%")

    # Dự đoán AI
    def predict_ai(history):
        if model and len(history) >= 3:
            return model.predict([history[-3:]])[0]
        return None

    ai_pred = predict_ai(st.session_state.history)
    if ai_pred:
        st.markdown("### 🤖 AI dự đoán")
        st.markdown(f"- AI chọn: **{ai_pred}**")

    # Biểu đồ
    fig, ax = plt.subplots()
    nums = [1, 2, 3, 4]
    counts = [freq.get(n, 0) for n in nums]
    ax.bar(nums, counts, color="skyblue")
    ax.set_xlabel("Số")
    ax.set_ylabel("Tần suất")
    st.pyplot(fig)