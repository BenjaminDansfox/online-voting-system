# -*- coding: utf-8 -*-
"""Voting_app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QHj_Zmp83EJRmApBczbcCcpGBembl37a
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

credentials = {
    "type": st.secrets["gcp_service_account"]["type"],
    "project_id": st.secrets["gcp_service_account"]["project_id"],
    "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
    "private_key": st.secrets["gcp_service_account"]["private_key"],
    "client_email": st.secrets["gcp_service_account"]["client_email"],
    "client_id": st.secrets["gcp_service_account"]["client_id"],
    "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
    "token_uri": st.secrets["gcp_service_account"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
}

creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
client = gspread.authorize(creds)

# Open your voting Google Sheet
sheet = client.open("Online Voting System").worksheet("Votes")  # Adjust to your actual sheet name


# Load Sheets
sheet = client.open("Your Voting Sheet")
users_sheet = sheet.worksheet("Registered_Users")
votes_sheet = sheet.worksheet("Votes")

# Get registered users
users = users_sheet.get_all_records()

st.title("Online Voting System")

# Voting is allowed from 9AM to 12PM
now = datetime.now()
if not (9 <= now.hour < 12):
    st.warning("Voting is only allowed between 9:00 AM and 12:00 PM.")
    st.stop()

# Login form
st.subheader("Enter your details to vote")
name = st.text_input("Your Name")
phone = st.text_input("Phone Number")

if st.button("Verify"):
    user = next((u for u in users if u['Name'] == name and u['Phone Number'] == phone), None)

    if not user:
        st.error("You are not a registered voter.")
        st.stop()

    if user['Voted'].lower() == "yes":
        st.warning("You have already voted.")
        st.stop()

    st.success("Verified. Cast your vote below:")

    # Voting form
    positions = ["President", "Vice President", "Secretary", "Treasurer", "Organizer", "Welfare Officer", "Media Director"]
    votes = {}
    for pos in positions:
        votes[pos] = st.selectbox(f"Choose {pos}", ["Candidate A", "Candidate B", "Candidate C"], key=pos)

    if st.button("Submit Vote"):
        # Record vote
        vote_row = [name] + [votes[pos] for pos in positions]
        votes_sheet.append_row(vote_row)

        # Mark user as voted
        cell = users_sheet.find(name)
        users_sheet.update_cell(cell.row, 3, "Yes")

        st.success("Your vote has been successfully recorded!")

st.header("Live Results (Summary)")

if st.checkbox("Show Results"):
    vote_df = pd.DataFrame(votes_sheet.get_all_records())
    for position in positions:
        st.subheader(f"{position} Results")
        if position in vote_df.columns:
            st.bar_chart(vote_df[position].value_counts())
