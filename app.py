import streamlit as st
import qrcode
from io import BytesIO
from streamlit_autorefresh import st_autorefresh

from database import create_tables, register_user, login_user

from queue_manager import (
    book_token,
    get_queue,
    get_patient_tokens,
    call_next_patient,
    get_waiting_count,
    get_token_details
)

from sms_service import send_sms


# PAGE CONFIGURATION
st.set_page_config(
    page_title="SmartQ 2.0",
    page_icon="🏥",
    layout="wide"
)

create_tables()

st.title("🏥 SmartQ 2.0")
st.subheader("Smart Hospital Queue Management System")


DOCTORS = {
    "General Medicine": ["Dr. Rahul", "Dr. Priya"],
    "Cardiology": ["Dr. Arjun", "Dr. Sneha"],
    "Orthopedics": ["Dr. Kiran", "Dr. Ananya"],
    "Neurology": ["Dr. Meera", "Dr. Vikram"],
    "Dermatology": ["Dr. Kavya", "Dr. Anil"]
}


if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None


# LOGIN PAGE
if st.session_state.username is None:

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:

        st.header("Patient / Admin Login")

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            role = login_user(username, password)

            if role:
                st.session_state.username = username
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid username or password")

    with register_tab:

        st.header("Create Patient Account")

        new_username = st.text_input("Create Username")
        new_password = st.text_input(
            "Create Password",
            type="password"
        )

        if st.button("Register"):

            if new_username and new_password:

                if register_user(new_username, new_password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists.")

            else:
                st.warning("Enter username and password.")


# PATIENT DASHBOARD
elif st.session_state.role == "patient":

    st_autorefresh(interval=5000, key="patient_refresh")

    st.sidebar.success(
        f"Welcome, {st.session_state.username}"
    )

    if st.sidebar.button("Logout"):
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

    book_tab, my_tokens_tab, queue_tab, qr_tab = st.tabs([
        "Book Token",
        "My Tokens",
        "Waiting List",
        "QR Scanner"
    ])

    # BOOK TOKEN
    with book_tab:

        st.header("Book Hospital Token")

        patient_name = st.text_input("Patient Name")
        phone = st.text_input("Mobile Number")

        department = st.selectbox(
            "Select Department",
            list(DOCTORS.keys())
        )

        doctor = st.selectbox(
            "Select Doctor",
            DOCTORS[department]
        )

        if st.button("Generate Token"):

            if patient_name and phone:

                token = book_token(
                    patient_name,
                    st.session_state.username,
                    phone,
                    department,
                    doctor
                )

                st.success("Token generated successfully!")

                st.subheader(f"🎫 Your Token: {token}")

                st.info("Counter Number: 1")

                st.info("Estimated waiting time: 15 minutes per patient.")

                qr_data = f"SmartQ Token: {token}"

                qr = qrcode.make(qr_data)

                image = BytesIO()
                qr.save(image, format="PNG")

                st.image(
                    image.getvalue(),
                    caption="Your Token QR Code",
                    width=200
                )

    # MY TOKENS
    with my_tokens_tab:

        st.header("My Appointments")

        tokens = get_patient_tokens(
            st.session_state.username
        )

        if tokens:

            for token_data in tokens:

                number, dept, doc, status, counter, appointment_time = token_data

                st.write(f"### 🎫 Token Number: {number}")
                st.write(f"Department: {dept}")
                st.write(f"Doctor: {doc}")
                st.write(f"Status: {status}")
                st.write(f"Counter Number: {counter}")

                if status == "Waiting":

                    waiting = get_waiting_count(
                        number, dept, doc
                    )

                    st.info(
                        f"Estimated waiting time: {waiting * 15} minutes"
                    )

                elif status == "Called":

                    st.success(
                        f"Your turn has arrived! Please go to Counter {counter}."
                    )

                st.divider()

        else:
            st.info("No appointments booked yet.")

    # WAITING LIST
    with queue_tab:

        st.header("Live Waiting List")

        if st.button("Refresh Queue"):
            st.rerun()

        queue = get_queue()

        if queue:

            for patient in queue:

                number, name, dept, doc, status, counter = patient

                st.write(
                    f"Token {number} | {dept} | "
                    f"{doc} | {status} | Counter {counter}"
                )

        else:
            st.info("No patients waiting.")

    # QR SCANNER
    with qr_tab:

        st.header("📷 QR Code Scanner")

        uploaded_qr = st.file_uploader(
            "Upload your Token QR Code",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded_qr:

            try:
                from PIL import Image
                from pyzbar.pyzbar import decode

                image = Image.open(uploaded_qr)

                results = decode(image)

                if results:

                    qr_data = results[0].data.decode("utf-8")

                    st.success("QR Code scanned successfully!")

                    if qr_data.startswith("SmartQ Token:"):

                        token_number = int(
                            qr_data.split(":")[1].strip()
                        )

                        details = get_token_details(token_number)

                        if details:

                            number, name, dept, doc, status, counter = details

                            st.subheader("🏥 Patient Details")

                            st.write(f"**Patient Name:** {name}")
                            st.write(f"**Token Number:** {number}")
                            st.write(f"**Department:** {dept}")
                            st.write(f"**Doctor:** {doc}")
                            st.write(f"**Status:** {status}")
                            st.write(f"**Counter Number:** {counter}")

                            if status == "Called":
                                st.success(
                                    f"Please proceed to Counter {counter}."
                                )

                            elif status == "Waiting":
                                st.warning("Please wait for your turn.")

                            elif status == "Served":
                                st.info("Your consultation is completed.")

                            # CURRENTLY RUNNING TOKEN
                            st.subheader("Currently Running Token")

                            queue = get_queue()

                            running = [
                                p for p in queue
                                if p[4] == "Called"
                                and p[2] == dept
                                and p[3] == doc
                            ]

                            if running:
                                for p in running:
                                    st.success(
                                        f"Now Calling Token: {p[0]}"
                                    )
                            else:
                                st.info("No token is currently being called.")

                        else:
                            st.error("Token details not found.")

                    else:
                        st.error("Invalid SmartQ QR Code.")

                else:
                    st.error("QR Code could not be scanned.")

            except Exception as error:
                st.error(f"QR Scanner Error: {error}")


# ADMIN DASHBOARD
elif st.session_state.role == "admin":

    st.sidebar.success("Admin Dashboard")

    if st.sidebar.button("Logout"):
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

    st.header("⚙️ Hospital Queue Management")

    st.subheader("Waiting Patients")

    queue = get_queue()

    if queue:

        for patient in queue:

            number, name, dept, doc, status, counter = patient

            st.write(
                f"Token: {number} | Patient: {name} | "
                f"Department: {dept} | Doctor: {doc} | Status: {status}"
            )

    else:
        st.info("No waiting patients.")

    if st.button("📢 Call Next Patient"):

        patient = call_next_patient()

        if patient:

            patient_id, token, name, phone = patient

            notification = send_sms(
                phone,
                token,
                1
            )

            st.success(f"Token {token} called successfully!")

            st.info(f"Patient: {name} | Counter: 1")

            st.subheader("📩 Simulated SMS Notification")

            st.write(f"To: {notification['phone']}")
            st.write(notification["message"])

            st.success(notification["status"])

        else:
            st.warning("No waiting patients available.")