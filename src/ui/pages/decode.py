"""VIN Decoder page for pyVIN application"""

import streamlit as st
from src.api.client import decode_vin_values_extended
from src.formatting.response import filter_non_null
from src.ui.components.results_table import display_results_table
from src.exceptions import VINDecoderError

st.set_page_config(page_title="VIN Decoder - pyVIN", layout="wide")

st.title("🚗 VIN Decoder")
st.markdown("Enter a 17-character Vehicle Identification Number to decode vehicle information from the NHTSA database.")

# VIN Input
vin_input = st.text_input(
    "Vehicle Identification Number",
    max_chars=17,
    placeholder="Enter 17-character VIN...",
    help="Example: 5UXWX7C50BA123456"
)

# Decode button
if st.button("Decode VIN", type="primary", use_container_width=False):
    if vin_input:
        if len(vin_input) != 17:
            st.error("VIN must be exactly 17 characters")
        else:
            try:
                with st.spinner("Decoding VIN..."):
                    result = decode_vin_values_extended(vin_input)
                    filtered = filter_non_null(result)

                st.success(f"✅ Successfully decoded VIN: {result.vin}")

                # Display results using the custom table component
                display_results_table(filtered)

            except VINDecoderError as e:
                st.error(f"❌ Decoding Error: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected Error: {e}")
    else:
        st.warning("⚠️ Please enter a VIN")

# Footer with helpful info
st.divider()
st.caption("Data provided by the NHTSA vPIC API")
