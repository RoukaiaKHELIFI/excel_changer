# import streamlit as st
# import pandas as pd


# # Function to apply the code on the DataFrame
# def modify_dataframe(df):
#   df = df.dropna()
#   df = df[df['K3001:Failed SDCCH Seizures due to Busy SDCCH'] >= 10]
#   df['result'] = df['Cell Name'].apply(lambda x: df[df['Cell Name'] == x].shape[0])
#   return df

# # Streamlit app
# def main():
#   st.title("Excel Sheet Modifier")

#   # Upload Excel file
#   uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

#   if uploaded_file is not None:
#     try:
#       # Read the uploaded Excel file
#       df = pd.read_excel(uploaded_file)

#       # Apply the modification
#       modified_df = modify_dataframe(df)

#       # Display modified DataFrame
#       st.dataframe(modified_df)
#       # save the modified DataFrame as Excel file
#       modified_df.to_excel("modified.xlsx", index=False)
#     except Exception as e:
#       st.error(f"Error: {e}")

# if __name__ == "__main__":
#   main()


###################################


import streamlit as st
import pandas as pd
from io import BytesIO
# import openpyxl

def modify_dataframe(df):
    df = df.dropna()
    df = df[df['K3001:Failed SDCCH Seizures due to Busy SDCCH'] >= 10]
    df['Nomber de jour Failure > 10 sur 7'] = df['Cell Name'].apply(lambda x: df[df['Cell Name'] == x].shape[0])
    df['Integrity'] = '100%'
    return df

def main():
    st.title("Excel Sheet Support")
    st.write("""This app is a support of excel sheet modifications and information extraction, you have to upload an excel sheet that has these kind of columns : 'Cell Name',
              'K3001:Failed SDCCH Seizures due to Busy SDCCH', 'Date'
     just like the content of this excel sheet'
             """)
    st.image('example.png', width=700)
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df = df.to_csv('csvfile.csv', encoding='utf-8', index=False)
            df = pd.read_csv('csvfile.csv')

            modified_df = modify_dataframe(df)
            st.dataframe(modified_df)
            buffer = BytesIO()

            modified_df.to_excel(buffer, index=False, engine='openpyxl')
            #modified_df.to_excel('modified_excel.xlsx', sheet_name='Sheet1', index=False)
            buffer.seek(0)
            st.download_button(
                    label="Download Excel File",
                    data=buffer,
                    file_name="modified_excel.xlsx",
                    key="download_button"
                )

        except Exception as e:
            st.error(f"Error: {e}")
    st.link_button('Email Me!','https://mail.google.com/mail/u/0/#inbox?compose=DmwnWtMmVfqrkGHslNKWWgMvKPPDhXmSGxWNkCkCWsztBWXJNzvTNcsJJDpLncMXPkrHWGMnzRtV')
    
if __name__ == "__main__":
    main()
