import streamlit as st
import requests
import json

API_URL = "http://localhost:8000/generate-plan"

st.set_page_config(page_title="AI Learning Path Recommender", layout="wide")

st.title("🎓 AI-Powered Personalized Learning Path Recommender")
st.markdown("Generate a curated week-by-week learning plan based on real ML scoring, not just LLM opinions.")

with st.sidebar:
    st.header("Your Constraints")
    topic = st.selectbox("Topic", ["Machine Learning", "Data Science", "System Design"])
    goal = st.text_area("Your Specific Goal", "I want to learn the basics of machine learning without complex math.")
    skill_level = st.selectbox("Current Skill Level", ["Beginner", "Intermediate", "Advanced"])
    available_hours = st.slider("Hours available per week", 1.0, 40.0, 5.0)
    num_weeks = st.slider("Timeline (Weeks)", 1, 12, 4)
    
    generate_btn = st.button("Generate Plan", type="primary")

if generate_btn:
    with st.spinner("Analyzing resources and constructing plan..."):
        try:
            payload = {
                "topic": topic,
                "goal": goal,
                "available_hours_per_week": available_hours,
                "num_weeks": num_weeks,
                "skill_level": skill_level
            }
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    st.error(data["error"])
                else:
                    st.success("Plan generated successfully!")
                    
                    st.markdown("### 📋 Your Plan Breakdown")
                    st.markdown(data['explanation'])
                    
                    with st.expander("View Raw JSON Plan Data"):
                        st.json(data['plan_data'])
            else:
                st.error(f"Error from backend: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
            st.info("Make sure the FastAPI backend is running on port 8000.")
