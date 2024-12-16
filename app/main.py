import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")

st.title("📧 Cold Mail Generator")
url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-44515?from=job%20search%20funnel")

# Initialize session state for response handling
if "response_generated" not in st.session_state:
    st.session_state.response_generated = False
    st.session_state.emails = []

submit_button = st.button("Submit")

def create_streamlit_app(llm, portfolio, clean_text):
    if submit_button and not st.session_state.response_generated:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            emails = []
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                emails.append(email)

            # Store the responses in session state
            st.session_state.emails = emails
            st.session_state.response_generated = True
        except Exception as e:
            st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)

    # Display the generated emails if available
    if st.session_state.response_generated:
        st.subheader("Generated Emails:")
        for email in st.session_state.emails:
            st.code(email, language="markdown")
