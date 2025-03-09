# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from password_utils import (
    generate_password,
    check_password_strength,
    detect_common_patterns,
    password_recommendations
)

# Configure Streamlit page
st.set_page_config(page_title="Advanced Password Tool", layout="wide")
st.title("Advanced Password Generator & Analyzer")
st.markdown("An interactive tool to generate secure passwords, evaluate their strength with detailed analysis, and visualize metrics.")

# Initialize session state for password history
if 'history' not in st.session_state:
    st.session_state.history = []

# Define tabs
tabs = st.tabs(["Generate Password", "Strength Checker", "Analysis & Visualization", "History & Recommendations"])

# -------------------
# Tab 1: Password Generator
# -------------------
with tabs[0]:
    st.header("Generate a Secure Password")
    st.markdown("Customize your password parameters below:")
    
    col1, col2 = st.columns(2)
    with col1:
        length = st.slider("Select Password Length", min_value=8, max_value=32, value=12, step=1)
        use_lower = st.checkbox("Include Lowercase Letters", value=True)
        use_upper = st.checkbox("Include Uppercase Letters", value=True)
        use_digits = st.checkbox("Include Digits", value=True)
        use_symbols = st.checkbox("Include Symbols", value=True)
        avoid_ambiguous = st.checkbox("Avoid Ambiguous Characters (e.g., Il1O0)", value=False)
    with col2:
        generate_multiple = st.checkbox("Generate Multiple Passwords")
        num_passwords = 5
        if generate_multiple:
            num_passwords = st.number_input("How many passwords?", min_value=1, max_value=20, value=5, step=1)
    
    if st.button("Generate Password"):
        if generate_multiple:
            passwords = []
            for _ in range(num_passwords):
                pwd = generate_password(length, use_lower, use_upper, use_digits, use_symbols, avoid_ambiguous)
                breakdown = check_password_strength(pwd)
                warnings = detect_common_patterns(pwd)
                passwords.append({
                    "Password": pwd,
                    "Strength": breakdown['total'],
                    "Warnings": "; ".join(warnings) if warnings else "None"
                })
                # Add to session history
                st.session_state.history.append({"Password": pwd, "Strength": breakdown['total']})
            df = pd.DataFrame(passwords)
            st.dataframe(df)
            st.download_button("Download as CSV",
                               df.to_csv(index=False).encode('utf-8'),
                               file_name='passwords.csv',
                               mime='text/csv')
            # Scatter plot for multiple passwords
            if not df.empty:
                fig_scatter = px.scatter(df, x="Password", y="Strength", title="Strength Distribution for Generated Passwords",
                                         labels={"Strength": "Strength Score"})
                st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            pwd = generate_password(length, use_lower, use_upper, use_digits, use_symbols, avoid_ambiguous)
            st.code(pwd, language="python")
            breakdown = check_password_strength(pwd)
            warnings = detect_common_patterns(pwd)
            st.write(f"Password Strength: **{breakdown['total']} / 100**")
            st.progress(breakdown['total'] / 100)
            if warnings:
                st.warning("Common issues: " + ", ".join(warnings))
            # Add to history
            st.session_state.history.append({"Password": pwd, "Strength": breakdown['total']})

# -------------------
# Tab 2: Password Strength Checker
# -------------------
with tabs[1]:
    st.header("Password Strength Checker")
    password_input = st.text_input("Enter a Password", type="password")
    
    if password_input:
        breakdown = check_password_strength(password_input)
        warnings = detect_common_patterns(password_input)
        st.write(f"Overall Strength: **{breakdown['total']} / 100**")
        st.progress(breakdown['total'] / 100)
        
        st.subheader("Score Breakdown:")
        st.write(f"**Length Score:** {breakdown['length']} / 40")
        st.write(f"**Lowercase Score:** {breakdown['lowercase']} / 10")
        st.write(f"**Uppercase Score:** {breakdown['uppercase']} / 10")
        st.write(f"**Digits Score:** {breakdown['digits']} / 20")
        st.write(f"**Symbols Score:** {breakdown['symbols']} / 20")
        
        if warnings:
            st.warning("Detected issues: " + ", ".join(warnings))
        
        recs = password_recommendations(breakdown, warnings)
        if recs:
            st.info("Recommendations to improve your password:")
            for rec in recs:
                st.write(f"- {rec}")
        else:
            st.success("Your password is robust!")

# -------------------
# Tab 3: Analysis & Visualization
# -------------------
with tabs[2]:
    st.header("Detailed Analysis & Visualization")
    st.markdown("Enter a password to see an in-depth visual breakdown of its strength metrics.")
    analysis_password = st.text_input("Enter Password for Analysis", key="analysis_input")
    
    if analysis_password:
        breakdown = check_password_strength(analysis_password)
        warnings = detect_common_patterns(analysis_password)
        data = {
            "Criteria": ["Length", "Lowercase", "Uppercase", "Digits", "Symbols"],
            "Score": [breakdown['length'], breakdown['lowercase'], breakdown['uppercase'], breakdown['digits'], breakdown['symbols']],
            "Maximum": [40, 10, 10, 20, 20]
        }
        df_analysis = pd.DataFrame(data)
        df_analysis["Percentage"] = df_analysis["Score"] / df_analysis["Maximum"] * 100
        
        fig_bar = px.bar(df_analysis, x="Criteria", y="Percentage", 
                         title="Password Strength Breakdown (%)", 
                         labels={"Percentage": "Score (%)"},
                         range_y=[0, 110],
                         text="Score")
        fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.subheader("Radar Chart Overview")
        fig_radar = px.line_polar(df_analysis, r="Percentage", theta="Criteria", line_close=True,
                                  title="Password Strength Radar Chart")
        st.plotly_chart(fig_radar, use_container_width=True)
        
        if warnings:
            st.warning("Issues detected: " + ", ".join(warnings))

# -------------------
# Tab 4: History & Recommendations
# -------------------
with tabs[3]:
    st.header("Password History & Recommendations")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        st.subheader("Generated Passwords History")
        st.dataframe(df_history)
        
        st.subheader("General Recommendations")
        # For overall recommendations, calculate average strength
        avg_strength = df_history["Strength"].mean()
        st.write(f"Average Strength Score: **{avg_strength:.2f} / 100**")
        if avg_strength < 50:
            st.info("Consider revising your generation parameters to improve overall strength.")
        else:
            st.success("Your generated passwords are generally strong!")
    else:
        st.info("No passwords generated yet. Use the Generate tab to create passwords.")
