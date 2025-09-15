import streamlit as st
import pandas as pd
import requests
import datetime

# Airtable configuration
AIRTABLE_BASE_ID = st.secrets.get("AIRTABLE_BASE_ID", "your_base_id")
AIRTABLE_TABLE_NAME = st.secrets.get("AIRTABLE_TABLE_NAME", "Patient_Records")
AIRTABLE_API_KEY = st.secrets.get("AIRTABLE_API_KEY", "your_api_key")

AIRTABLE_ENDPOINT = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

# Airtable API functions
def add_record_to_airtable(record_data):
    """Add record to Airtable"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "records": [
            {
                "fields": record_data
            }
        ]
    }
    
    try:
        response = requests.post(AIRTABLE_ENDPOINT, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["records"][0]["id"]
        else:
            st.error(f"Airtable API error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def get_records_from_airtable():
    """Get all records from Airtable"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }
    
    try:
        response = requests.get(AIRTABLE_ENDPOINT, headers=headers)
        if response.status_code == 200:
            records = response.json()["records"]
            # Flatten the structure
            flattened_records = []
            for record in records:
                flat_record = record["fields"]
                flat_record["airtable_id"] = record["id"]
                flattened_records.append(flat_record)
            return flattened_records
        else:
            st.error(f"Airtable API error: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

def update_airtable_record(record_id, updates):
    """Update record in Airtable"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "records": [
            {
                "id": record_id,
                "fields": updates
            }
        ]
    }
    
    try:
        response = requests.patch(AIRTABLE_ENDPOINT, json=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def delete_airtable_record(record_id):
    """Delete record from Airtable"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }
    
    try:
        response = requests.delete(f"{AIRTABLE_ENDPOINT}/{record_id}", headers=headers)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# Streamlit UI
st.title("🗃️ Airtable Database Integration")
st.markdown("### Simple spreadsheet-like database with powerful API")

# Setup instructions
with st.expander("🚀 Super Easy Airtable Setup (5 minutes!)"):
    st.markdown("""
    ### Step-by-Step Setup:
    
    #### 1. Create Airtable Base (2 minutes)
    - Go to [airtable.com](https://airtable.com) → Sign up (free)
    - Create new base → "Start from scratch"
    - Name it: "Antimicrobial Resistance Study"
    
    #### 2. Set Up Table Structure (2 minutes)
    Replace default fields with these **exact field names**:
    
    **Demographics:**
    - `Age` (Number)
    - `Gender` (Single select: Male, Female)
    
    **Microbiology:**  
    - `Species` (Single select: E. coli, Klebsiella spp., Proteus spp., Pseudomonas spp., Acinetobacter spp.)
    - `Rectal_CPE_Pos` (Single select: 0, 1)
    
    **Clinical:**
    - `Setting` (Single select: ICU, Internal Medicine)  
    - `Acquisition` (Single select: Community, Hospital)
    - `BSI_Source` (Single select: Primary, Lung, Abdomen, UTI)
    
    **Comorbidities:**
    - `CHF` (Single select: 0, 1)
    - `CKD` (Single select: 0, 1) 
    - `Tumor` (Single select: 0, 1)
    - `Diabetes` (Single select: 0, 1)
    - `Immunosuppressed` (Single select: 0, 1)
    
    **Resistance:**
    - `CR` (Single select: 0, 1)
    - `BLBLI_R` (Single select: 0, 1)
    - `FQR` (Single select: 0, 1)  
    - `GC3_R` (Single select: 0, 1)
    - `Notes` (Long text)
    - `Created_At` (Date)
    
    #### 3. Get API Credentials (1 minute)
    - Click your profile → Account
    - Generate API key
    - Copy Base ID from base URL: `https://airtable.com/app**BASEID**/tbl...`
    
    #### 4. Add to Streamlit Secrets
    ```toml
    AIRTABLE_BASE_ID = "appXXXXXXXXXXXXXX"
    AIRTABLE_TABLE_NAME = "Patient_Records"  
    AIRTABLE_API_KEY = "keyXXXXXXXXXXXXXX"
    ```
    
    **That's it!** 🎉 Your database is ready!
    """)

# Test connection
if st.button("🔍 Test Airtable Connection"):
    records = get_records_from_airtable()
    if records is not None:
        st.success(f"✅ Connected! Found {len(records)} records")
        if records:
            st.dataframe(pd.DataFrame(records))
    else:
        st.error("❌ Connection failed. Check your credentials.")

# Main app interface
tab1, tab2 = st.tabs(["➕ Add Record", "📊 View Data"])

with tab1:
    st.header("Add New Patient Record")
    
    with st.form("airtable_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=18, max_value=90, value=65)
            gender = st.selectbox("Gender", ["Male", "Female"])
            species = st.selectbox("Species", [
                "E. coli", "Klebsiella spp.", "Proteus spp.", 
                "Pseudomonas spp.", "Acinetobacter spp."
            ])
            rectal_cpe = st.selectbox("Rectal CPE Positive", ["0", "1"])
            setting = st.selectbox("Setting", ["ICU", "Internal Medicine"])
            acquisition = st.selectbox("Acquisition", ["Community", "Hospital"])
        
        with col2:
            bsi_source = st.selectbox("BSI Source", ["Primary", "Lung", "Abdomen", "UTI"])
            chf = st.selectbox("CHF", ["0", "1"])
            ckd = st.selectbox("CKD", ["0", "1"])
            tumor = st.selectbox("Tumor", ["0", "1"])
            diabetes = st.selectbox("Diabetes", ["0", "1"])
            immunosuppressed = st.selectbox("Immunosuppressed", ["0", "1"])
        
        # Resistance outcomes
        st.subheader("🧪 Resistance Results")
        col3, col4 = st.columns(2)
        
        with col3:
            cr = st.selectbox("CR (Carbapenem Resistance)", ["0", "1"])
            blbli_r = st.selectbox("BLBLI_R", ["0", "1"])
        
        with col4:
            fqr = st.selectbox("FQR", ["0", "1"]) 
            gc3_r = st.selectbox("3GC_R", ["0", "1"])
        
        notes = st.text_area("Notes (optional)")
        
        if st.form_submit_button("💾 Save to Airtable"):
            record_data = {
                "Age": int(age),
                "Gender": gender,
                "Species": species,
                "Rectal_CPE_Pos": rectal_cpe,
                "Setting": setting,
                "Acquisition": acquisition,
                "BSI_Source": bsi_source,
                "CHF": chf,
                "CKD": ckd,
                "Tumor": tumor,
                "Diabetes": diabetes,
                "Immunosuppressed": immunosuppressed,
                "CR": cr,
                "BLBLI_R": blbli_r,
                "FQR": fqr,
                "GC3_R": gc3_r,
                "Notes": notes,
                "Created_At": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            
            record_id = add_record_to_airtable(record_data)
            if record_id:
                st.success(f"✅ Record saved successfully! ID: {record_id}")
                st.balloons()
            else:
                st.error("❌ Failed to save record")

with tab2:
    st.header("📊 View All Records")
    
    records = get_records_from_airtable()
    
    if records:
        df = pd.DataFrame(records)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            if 'Gender' in df.columns:
                male_count = len(df[df['Gender'] == 'Male'])
                st.metric("Male Patients", male_count)
        with col3:
            if 'Gender' in df.columns:
                female_count = len(df[df['Gender'] == 'Female'])
                st.metric("Female Patients", female_count)
        
        # Data table
        st.subheader("All Patient Records")
        st.dataframe(df, use_container_width=True)
        
        # Export functionality
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV File",
                data=csv,
                file_name=f"patient_data_{datetime.date.today()}.csv",
                mime="text/csv"
            )
        
        # Quick analytics
        st.subheader("📈 Quick Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Species' in df.columns:
                species_counts = df['Species'].value_counts()
                st.write("**Species Distribution:**")
                st.bar_chart(species_counts)
        
        with col2:
            # Resistance summary
            resistance_cols = ['CR', 'BLBLI_R', 'FQR', 'GC3_R']
            available_cols = [col for col in resistance_cols if col in df.columns]
            
            if available_cols:
                resistance_data = {}
                for col in available_cols:
                    resistance_data[col] = (df[col] == '1').sum()
                
                st.write("**Resistance Patterns:**")
                st.bar_chart(pd.Series(resistance_data))
    
    else:
        st.info("No records found. Add some data in the 'Add Record' tab!")

# Requirements file content
st.markdown("---")
st.code("""
# requirements.txt
streamlit
pandas
requests
""")

# Deployment checklist
with st.expander("🚀 Deployment Checklist"):
    st.markdown("""
    ### Ready to Deploy? ✅
    
    **Prerequisites:**
    - [ ] Airtable base created with correct field names
    - [ ] API key generated
    - [ ] Base ID copied
    - [ ] Secrets configured
    
    **Deployment Options:**
    
    **1. Streamlit Cloud (Easiest):**
    ```bash
    # Push to GitHub
    git add .
    git commit -m "Airtable integration"
    git push origin main
    
    # Deploy at share.streamlit.io
    # Add secrets in dashboard
    ```
    
    **2. Heroku:**
    ```bash
    # Create Procfile
    echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile
    
    # Deploy
    heroku create your-app-name
    git push heroku main
    ```
    
    **3. Railway:**
    ```bash
    # One command deployment
    railway deploy
    ```
    
    **Benefits of Airtable:**
    - ✅ Visual interface for data review
    - ✅ Built-in data validation  
    - ✅ Easy sharing with team
    - ✅ Automatic backups
    - ✅ Mobile app available
    - ✅ Export to Excel/CSV anytime
    """)
