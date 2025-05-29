import streamlit as st
import pandas as pd
from specklepy.api.client import SpeckleClient
from specklepy.transports.server import ServerTransport
from specklepy.api.credentials import get_default_account
from specklepy.api import operations

from fn__libs import *



# Setup Speckle client
account = get_default_account()
client = SpeckleClient(host=account.serverInfo.url)
client.authenticate_with_account(account)

# Project + model config
SPECKLE_PROJECT_ID = "dfdc0d2b01"
SPECKLE_MODEL_ID = "60d4b65b7b"







# Set full-width layout
st.set_page_config(layout="wide")
st.markdown("#### 🧩 Speckle Extractor — SpecklePy + Tekla Fields")



try:
    left_col, right_col = st.columns([2,3])  # 1/3 + 2/3 layout

    with left_col:
        embed_url = f"https://speckle.xyz/projects/{SPECKLE_PROJECT_ID}/models/{SPECKLE_MODEL_ID}?embed=%7B%22isEnabled%22%3Atrue%7D"
        st.markdown("##### 🌐 Speckle Viewer")
        st.components.v1.iframe(embed_url, height=700)

    with right_col:

        st.markdown("##### Speckle Object Parser")

        with st.spinner("🔍 Fetching all object IDs using SpecklePy..."):
            all_object_ids = get_objects_list(client, SPECKLE_PROJECT_ID, SPECKLE_MODEL_ID)
        st.success(f"✅ Total unique object IDs discovered: **{len(all_object_ids)}**")

        extracted_rows = []
        with st.spinner("📦 Extracting Tekla fields from all objects..."):
            for obj_id in all_object_ids:
                # st.write(obj_id)

                try:
                    row = extract_tekla_fields(client, SPECKLE_PROJECT_ID, obj_id)
                    extracted_rows.append(row)
                except Exception as e:
                    st.warning(f"Skipping {obj_id} due to error: {e}")

        if extracted_rows:
            df = pd.DataFrame(extracted_rows)

            mapping_dict = load_mapping_dict('mapping_dict.txt')
            df = add_mapping_column(df, 'Phase', mapping_dict, 'Phase_Ceccoli')

            print(df)



            st.subheader("📋 Extracted Tekla Fields Table")
            st.dataframe(df)

            st.subheader("📊 Summary")
            st.write(f"Total objects processed: **{len(df)}**")
            st.write(f"Unique Classes: {df['Class'].nunique()}")
            st.write(f"Unique Phases: {df['Phase'].nunique()}")

            st.download_button("💾 Download Extracted CSV", data=df.to_csv(index=False), file_name="tekla_extracted.csv")
            st.download_button("💾 Download Extracted JSON", data=df.to_json(orient="records", indent=2), file_name="tekla_extracted.json")
        else:
            st.warning("⚠ No Tekla data extracted.")

except Exception as e:
    st.error(f"❌ Error: {e}")
