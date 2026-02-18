import streamlit as st
from deepface import DeepFace
import os
import json
from PIL import Image
import uuid

# ---------------------------
# Config
# ---------------------------
st.set_page_config(page_title="Face Access System", layout="wide")

DATABASE_PATH = "database/users.json"
FACES_PATH = "stored_faces"

os.makedirs("database", exist_ok=True)
os.makedirs(FACES_PATH, exist_ok=True)

# ---------------------------
# Advanced CSS Styling
# ---------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}
.main {
    background: transparent;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(15px);}
    to {opacity: 1; transform: translateY(0);}
}
.title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    color: white;
}
.button>button {
    border-radius: 18px;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border: none;
    padding: 0.6em 1.5em;
}
img {
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Utility Functions
# ---------------------------
def load_users():
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, "r") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(DATABASE_PATH, "w") as f:
        json.dump(users, f, indent=4)

def verify_face(uploaded_path):
    users = load_users()
    for user in users:
        try:
            result = DeepFace.verify(
                img1_path=uploaded_path,
                img2_path=user["image_path"],
                model_name="Facenet",
                enforce_detection=True
            )
            if result["verified"]:
                return user["name"]
        except:
            continue
    return None

# ---------------------------
# Navigation
# ---------------------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Register User (Admin)", "View Registered Users", "About"]
)

st.markdown('<div class="title">🔐 Face Access Control System</div>', unsafe_allow_html=True)
st.write("")

users = load_users()

# ---------------------------
# HOME PAGE
# ---------------------------
if menu == "Home":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Upload Photo to Access")

    uploaded_file = st.file_uploader("Upload Image", type=["jpg","jpeg","png"])

    if uploaded_file:
        temp_path = f"temp_{uuid.uuid4().hex}.jpg"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        if len(users) == 0:
            st.success("No users found. You are registered as Admin.")
            admin_name = st.text_input("Enter Admin Name")

            if st.button("Register Admin"):
                permanent_path = os.path.join(FACES_PATH, f"{admin_name}.jpg")
                os.rename(temp_path, permanent_path)

                users.append({
                    "name": admin_name,
                    "role": "Admin",
                    "image_path": permanent_path
                })
                save_users(users)
                st.success("Admin Registered Successfully")

        else:
            verified_user = verify_face(temp_path)
            os.remove(temp_path)

            if verified_user:
                st.success(f"Access Granted. Welcome {verified_user}")
            else:
                st.error("Access Denied! Ask admin or registered members to give you access.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# REGISTER PAGE
# ---------------------------
elif menu == "Register User (Admin)":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Admin Only - Add New User")

    admin_name = st.text_input("Enter Admin Name to Verify")
    new_user_name = st.text_input("New User Name")
    uploaded_file = st.file_uploader("Upload New User Image", type=["jpg","jpeg","png"])

    if st.button("Register User"):
        admin_exists = any(u["name"] == admin_name and u["role"] == "Admin" for u in users)

        if not admin_exists:
            st.error("Only Admin can add users.")
        elif uploaded_file and new_user_name:
            user_path = os.path.join(FACES_PATH, f"{new_user_name}.jpg")
            with open(user_path, "wb") as f:
                f.write(uploaded_file.read())

            users.append({
                "name": new_user_name,
                "role": "User",
                "image_path": user_path
            })
            save_users(users)
            st.success("User Registered Successfully")
        else:
            st.warning("Fill all fields.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# VIEW USERS PAGE
# ---------------------------
elif menu == "View Registered Users":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Registered Users")

    if len(users) == 0:
        st.warning("No users registered.")
    else:
        cols = st.columns(3)
        for i, user in enumerate(users):
            with cols[i % 3]:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.image(user["image_path"])
                st.markdown(f"**{user['name']}**")
                st.write(f"Role: {user['role']}")
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# ---------------------------
# ABOUT PAGE
# ---------------------------
elif menu == "About":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.subheader("🔎 Project Overview")

    st.markdown("""
    The **Face Access Control System** is a biometric authentication platform 
    designed to provide secure, intelligent, and role-based access using facial recognition technology.

    Unlike traditional password systems that rely on memory and manual input, 
    this system leverages **Deep Learning-based facial verification** to identify 
    and authenticate users through their unique facial features.

    The system operates in a structured workflow:

    1. **Initial Admin Registration**
       - When the system runs for the first time and no users exist,
         the first verified individual is automatically registered as the **Admin**.
       - This Admin gains authority to manage user access.

    2. **User Authentication**
       - When a user uploads their photo, the system compares it 
         against stored facial data using the **FaceNet model**.
       - If a match is verified within the threshold confidence level,
         access is granted.
       - If no match is found, access is denied.

    3. **Role-Based Access Control**
       - Admin users can register new members.
       - Registered users can be authenticated securely.
       - Unauthorized individuals are blocked with a controlled access denial message.

    4. **Secure Storage Mechanism**
       - Facial images are stored securely in the system.
       - Metadata including name and role is maintained in a structured JSON database.
       - Face verification is performed dynamically using DeepFace.

    This project demonstrates the practical implementation of:
    - Computer Vision
    - Deep Learning
    - Biometric Security Systems
    - Role-Based Access Control
    - Modern Web Interface Design (Glassmorphism UI)

    The objective of this system is to simulate a real-world biometric access platform 
    that could be extended to institutions, workplaces, or secure environments.
    """)

    st.subheader("⚙️ Technologies Used")

    st.markdown("""
    - **Streamlit** – Frontend web framework  
    - **DeepFace** – Deep Learning-based facial verification  
    - **TensorFlow & FaceNet** – Neural network model for feature embeddings  
    - **Python** – Core application logic  
    - **JSON Database** – Lightweight structured data storage  
    - **Glassmorphism UI Design** – Modern user interface styling  
    """)

    st.subheader("🎯 Key Features")

    st.markdown("""
    ✔ Automated Admin Initialization  
    ✔ Facial Verification using Deep Learning  
    ✔ Role-Based Access Control  
    ✔ Secure User Registration  
    ✔ Real-Time Face Matching  
    ✔ Modern Responsive Interface  
    ✔ Extendable Architecture for Live Systems  
    """)

    st.subheader("👨‍💻 Creators")

    creators = [
        {"name": "Ayush Bhagwat", "role": "Lead Developer & System Architect", "image": "assets/Ayushpic.jpeg"},
        {"name": "Adarsh Patil", "role": "Backend Developer", "image": "assets/Aadarsh.jpeg"},
        {"name": "Rihanshu Ashtikar", "role": "Frontend & UI Developer", "image": "assets/Rihanshu.jpeg"},
        {"name": "Aman Shaikh", "role": "System Integration & Testing", "image": "assets/Aaman Shaikh.jpeg"},
    ]

    cols = st.columns(2)

    for i, creator in enumerate(creators):
        with cols[i % 2]:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.image(creator["image"])
            st.markdown(f"### {creator['name']}")
            st.write(creator["role"])
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
