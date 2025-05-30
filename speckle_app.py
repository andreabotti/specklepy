import os
import streamlit as st
import pandas as pd
from specklepy.api.client import SpeckleClient

from fn__libs import get_objects_list, extract_tekla_fields

# ---------- Helper function ----------
def get_required_secret(key):
    val = st.secrets.get(key) or os.environ.get(key)
    if not val:
        st.error(f"❌ Missing required secret or environment variable: {key}")
        st.stop()
    return val

# ---------- Load configuration ----------
SPECKLE_URL = get_required_secret("SPECKLE_URL")
SPECKLE_API_TOKEN = get_required_secret("SPECKLE_TOKEN")
SPECKLE_PROJECT_ID = get_required_secret("SPECKLE_PROJECT_ID")
SPECKLE_MODEL_ID = get_required_secret("SPECKLE_MODEL_ID")

# ---------- Initialize Speckle client ----------
client = SpeckleClient(host=SPECKLE_URL)
client.authenticate_with_token(SPECKLE_API_TOKEN)

# ---------- Streamlit layout ----------
st.set_page_config(layout="wide")
st.markdown("### Speckle Extractor — SpecklePy + custom Tekla Fields")

try:
    left_col, right_col = st.columns([3,5], gap="small")  # 1/3 + 2/3 layout

    with left_col:
        embed_url = f"https://speckle.xyz/projects/{SPECKLE_PROJECT_ID}/models/{SPECKLE_MODEL_ID}?embed=%7B%22isEnabled%22%3Atrue%7D"
        st.markdown("##### 🌐 Speckle Viewer")
        st.components.v1.iframe(embed_url, height=700)

    with right_col:
        st.markdown("##### 🧩 Speckle parameter extraction")

        st.write(f"Project ID: `{SPECKLE_PROJECT_ID}`")
        st.write(f"Model ID: `{SPECKLE_MODEL_ID}`")

        with st.spinner("🔍 Fetching all object IDs using SpecklePy..."):
            all_object_ids = get_objects_list(client, SPECKLE_PROJECT_ID, SPECKLE_MODEL_ID)
        st.success(f"✅ Total unique object IDs discovered: **{len(all_object_ids)}**")

        extracted_rows = []
        with st.spinner("📦 Extracting Tekla fields from all objects..."):
            for obj_id in all_object_ids:
                try:
                    row = extract_tekla_fields(client, SPECKLE_PROJECT_ID, obj_id)
                    extracted_rows.append(row)
                except Exception as e:
                    st.warning(f"Skipping {obj_id} due to error: {e}")

        if extracted_rows:
            df = pd.DataFrame(extracted_rows)
            df = df.astype(str)                     # Ensure all columns are string-typed for Arrow compatibility

            st.markdown("##### 📋 Extracted Table with Tekla Fields")
            st.dataframe(df)

            st.markdown("##### 📊 Summary")
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 2], gap="small")
            col1.metric("Total Objects", len(df))
            col2.metric("Unique Classes", df['Class'].nunique())
            col3.metric("Unique Phases", df['Phase'].nunique())
            # col1.write(f"Total objects processed: **{len(df)}**")
            # col2.write(f"Unique Classes: {df['Class'].nunique()}")
            # col3.write(f"Unique Phases: {df['Phase'].nunique()}")
            col4.markdown(""); col5.markdown("")
            col4.download_button("💾 Download Extracted CSV", data=df.to_csv(index=False), file_name="tekla_extracted.csv")
            col5.download_button("💾 Download Extracted JSON", data=df.to_json(orient="records", indent=2), file_name="tekla_extracted.json")
        else:
            st.warning("⚠ No Tekla data extracted.")

except Exception as e:
    st.error(f"❌ Error: {e}")
