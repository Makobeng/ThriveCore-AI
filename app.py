import os
import streamlit as st
import requests

st.set_page_config(page_title='ThriveCore AI', page_icon='🌱', layout='centered')
st.markdown('''<style>.block-container{max-width:850px;padding-top:2rem}h1{color:#183e53}.stButton button{background:#174c61;color:white;border-radius:10px}</style>''', unsafe_allow_html=True)
st.title('ThriveCore AI')
st.caption('Your Business. Smarter Every Day. | Prototype v1.1')
st.info('Prototype: AI features require a configured, reachable Llama-compatible inference endpoint. Outputs must be reviewed before use.')

# oUse a trusted server-side secret store when deployed; never ask end users for the key.
def setting(key, default=''):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

url = setting('LLAMA_API_URL')
key = setting('LLAMA_API_KEY')
model = setting('LLAMA_MODEL', 'meta-llama/Llama-3.3-70B-Instruct')

with st.sidebar:
    st.header('Business profile')
    business = st.text_input('Business name', 'My South African Business')
    sector = st.text_input('Industry', 'Retail and services')
    facts = st.text_area('Verified business facts (hours, prices, policies)', 'Only use information I provide here.')
    language = st.selectbox('Preferred language', ['English', 'Sepedi', 'isiZulu'])
    st.caption('Sepedi and isiZulu output quality must be independently checked.')
    st.divider()
    st.write('AI connection:', 'Configured' if url and key else 'Not configured')
    if st.button('Test AI connection'):
        if not (url and key):
            st.error('Set LLAMA_API_URL and LLAMA_API_KEY in your deployment secrets.')
        else:
            try:
                r = requests.post(url, headers={'Authorization':f'Bearer {key}', 'Content-Type':'application/json'}, json={'model':model,'messages':[{'role':'user','content':'Reply with exactly: Connected'}], 'max_tokens':20}, timeout=35)
                r.raise_for_status()
                answer = r.json()['choices'][0]['message']['content']
                st.success('Model returned: '+str(answer)[:120])
            except requests.RequestException as exc:
                st.error(f"Connection failed: HTTP {exc.response.status_code}" if exc.response is not None else f"Connection failed: {type(exc).__name__}")

def ask_llama(system, prompt):
    if not (url and key):
        st.warning('AI is not connected. Add the Llama endpoint and API key to activate this feature.')
        return None
    try:
        response = requests.post(url, headers={'Authorization':f'Bearer {key}', 'Content-Type':'application/json'}, json={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':prompt}], 'temperature':0.3, 'max_tokens':700}, timeout=65)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        st.error('AI request unsuccessful. Check provider configuration and logs. ('+type(exc).__name__+')')
        return None

profile = f'Business: {business}\nIndustry: {sector}\nVerified facts: {facts}\nRequested language: {language}.'
tabs = st.tabs(['💬 Customer replies','📝 Business writer','🛡️ Scam awareness'])
with tabs[0]:
    st.subheader('Customer reply assistant')
    enquiry = st.text_area('Paste a customer enquiry', placeholder='Hi, what time do you close?')
    if st.button('Draft customer reply', disabled=not enquiry.strip()):
        result = ask_llama('Draft a polite concise reply. Do not invent opening hours, prices, availability, or policies. Ask for missing facts. Never promise actions were taken. '+profile, enquiry)
        if result: st.text_area('Review and copy your draft',result,height=210)
with tabs[1]:
    st.subheader('Business document writer')
    doc_type = st.selectbox('Document type',['Professional email','Quotation draft','Short proposal'])
    request = st.text_area('What should the document say?', placeholder='Write a follow-up to a potential customer...')
    if st.button('Generate document', disabled=not request.strip()):
        result = ask_llama('Write a '+doc_type+'. Do not fabricate costs, contact information, company registration or commitments. For missing information insert [TO CONFIRM]. This is a draft, not an issued invoice. '+profile, request)
        if result: st.text_area('Review and copy your draft',result,height=260)
with tabs[2]:
    st.subheader('Suspicious message review')
    st.caption('Do not paste passwords, OTPs, identity numbers or other sensitive data. This is educational guidance, not a definitive security verdict.')
    suspicious = st.text_area('Paste a message with personal information removed', placeholder='Urgent! Click this link to verify your account...')
    if st.button('Review warning signs', disabled=not suspicious.strip()):
        result = ask_llama('Explain potential phishing or scam indicators, uncertainty, and safe next steps. Never state that a message is definitely safe. Do not open links or perform external actions. Respond in '+language+'.', suspicious)
        if result: st.text_area('Educational analysis',result,height=260)
st.divider()
st.caption('ThriveCore AI | Johannesburg, South Africa | Founder: Makobeng Annah Mampana | Prototype — not publicly launched')
