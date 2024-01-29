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
import numpy as np

def modify_dataframe(df):
    df = df.dropna()
    df = df[df['K3001:Failed SDCCH Seizures due to Busy SDCCH'] >= 10]
    df['Nomber de jour Failure > 10 sur 7'] = df['Cell Name'].apply(lambda x: df[df['Cell Name'] == x].shape[0])
    df['Integrity'] = '100%'
    
    return df

def save_worst_cell(df):
    df = df[df['Nomber de jour Failure > 10 sur 7']>= 5 ].sort_values(by = 'K3001:Failed SDCCH Seizures due to Busy SDCCH', ascending=False).drop_duplicates('Cell Name')
    return df

def Target_cell_sdcch(df):
    conditions = [
    (df['Actual Cell SDCCH Channel Maximum'] < 30),
    (df['Actual Cell SDCCH Channel Maximum'] < 60),
    (df['Actual Cell SDCCH Channel Maximum'] < 80),
    (df['Actual Cell SDCCH Channel Maximum'] >= 80)
]
    choices = [30, 60, 80, 120]
    df['Target Cell SDCCH Channel Maximum'] = np.select(conditions, choices, default=0)
    return df

def script1(df):
    for i, j in df.iterrows():
        df.at[i,'Script 1'] = f"SET GCELLCHMGBASIC:IDTYPE=BYID,CELLID={j['Cell CI']},CELLMAXSD={j['Target Cell SDCCH Channel Maximum']};"
    return df

def script2(df):
    for i, j in df.iterrows():
        df.at[i,'Script 2'] = j['Script 1']+"{"+j["GBSC"]+"}"
    return df

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def main():
    st.title("Excel Sheet Support")
    st.write("""This app is a support of excel sheet modifications and information extraction, you have to upload an excel sheet that has these kind of columns : 'Cell Name',
              'K3001:Failed SDCCH Seizures due to Busy SDCCH', 'Date'
     just like the content of this excel sheet'
             """)
    st.image('example.png', width=700)
    st.sidebar.title("Steps and Choices")
    st.sidebar.write("""1- Upload the excel sheet that you want to modify""")
    st.sidebar.write("""2- Upload the configuration files""")
    st.sidebar.write("""3- Download the modified excel sheet""")
    
    uploaded_file = st.file_uploader("Upload KPI 2G BTS Query Result file", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df = df.to_csv('csvfile.csv', encoding='utf-8', index=False)
            df = pd.read_csv('csvfile.csv')
            modified_df = modify_dataframe(df)
            st.write('Failed Cells')
            st.dataframe(modified_df)
            buffer = BytesIO()
            worst_cell = save_worst_cell(modified_df)
            # save in a excel the first sheet has modified_df and the second has worst_cell with the name sheet1 and sheet2
            writer = pd.ExcelWriter(buffer, engine='openpyxl')
            modified_df.to_excel(writer, sheet_name='SDCCH Congestion', index=False)
            worst_cell.to_excel(writer, sheet_name='SDCCH Worst Cells', index=False)
            st.write('Worst Cells')
            st.dataframe(worst_cell)
            writer.close()

            buffer.seek(0)
            st.download_button(
                    label="Download Excel File",
                    data=buffer,
                    file_name="modified_excel.xlsx",
                    key="download_button"
                )
            if worst_cell is not None:
                try:
                    uploaded_file2 = st.file_uploader("Upload Configuration files", type=["xlsx", "xls"], accept_multiple_files=True)
                    if uploaded_file2 is not None:
                        uploaded_data_read = [pd.read_excel(file, sheet_name='GCELLCHMGBASIC', skiprows=[0]) for file in uploaded_file2]
                        raw_data = pd.concat(uploaded_data_read)
                        config_data = raw_data[['*Cell Name', 'Cell SDCCH Channel Maximum']]
                        config_data.to_csv('config_data.csv', index=False)
                    with st.spinner("Please Wait..."):
                        conf_df = pd.read_csv('config_data.csv')
                        st.write('Finding Actual Cell SDCCH Channel Maximum')
                        worst_cell["Actual Cell SDCCH Channel Maximum"] = worst_cell["Cell Name"].apply(lambda x: conf_df[conf_df["*Cell Name"] == x]["Cell SDCCH Channel Maximum"].values[0])
                        st.write('Getting Most Repeated Actual Cell SDCCH Channel Maximum')
                        repeated_critical_actual_cell = worst_cell[ worst_cell['Actual Cell SDCCH Channel Maximum'] >=  np.median(worst_cell['Actual Cell SDCCH Channel Maximum'].value_counts().unique())]
                        st.write('Calculating Target Cell SDCCH Channel Maximum')
                        target_cells = Target_cell_sdcch(repeated_critical_actual_cell)
                        st.write('Generating Scripts')
                        script_1 = script1(target_cells)
                        script_2 = script2(script_1)
                        script_2.to_excel('script.xlsx', index=False)
                except Exception as e:
                    st.write(f"Now you can provide the Configuration Data files that has the Cell SDCCH Channel Maximum")
            sc = pd.read_excel('script.xlsx')
            buffer2 = BytesIO()
            writer2 = pd.ExcelWriter(buffer2, engine='openpyxl')

            modified_df.to_excel(writer2, sheet_name='SDCCH Congestion', index=False)
            worst_cell.to_excel(writer2, sheet_name='SDCCH Worst Cells', index=False)
            sc.to_excel(writer2, sheet_name='Script', index=False)
            writer2.close()
            buffer2.seek(0)
            st.download_button(
                        label="Download Script File",
                        data=buffer2,
                        file_name="script.xlsx",
                        key="download_button2"
                    ) 
        except Exception as e:
            st.error(f"Error: {e}")

    
                
          
    st.link_button('Email Me!','https://mail.google.com/mail/u/0/#inbox?compose=DmwnWtMmVfqrkGHslNKWWgMvKPPDhXmSGxWNkCkCWsztBWXJNzvTNcsJJDpLncMXPkrHWGMnzRtV')
    
if __name__ == "__main__":
    main()