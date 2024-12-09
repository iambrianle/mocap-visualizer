import pandas as pd
import scipy.io as sio
import numpy as np

# extract marker names, numerical data, and time data from the sheet
def extract_clean_data_with_time(sheet_data):
    time_data = sheet_data.iloc[4:, 0].apply(pd.to_numeric, errors='coerce')
    marker_names = sheet_data.iloc[2, 1:].dropna().astype(str).apply(lambda x: x.strip())
    numerical_data = sheet_data.iloc[4:, 1:].apply(pd.to_numeric, errors='coerce')
    # print(time_data)
    # print(marker_names)
    # print(numerical_data)

    return marker_names, numerical_data.to_numpy(), time_data.to_numpy()


def main():
    # load the Excel file
    file_path = 'motiondata.xlsx'  
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    combined_data_struct= {}

    # creating the data structure with time
    for sheet_name in sheet_names:
        data = xls.parse(sheet_name, header=None)
        names, values, time_data = extract_clean_data_with_time(data)
        # create a dictionary for each marker
        marker_data = {name: values[:, idx] for idx, name in enumerate(names)}
        combined_data_struct[sheet_name] = {
            'marker_names': np.array(names),
            'marker_data': marker_data,
            'time': time_data
        }
        


    # save to a new .mat file
    output_path = 'motioncapture_with_time.mat'  
    sio.savemat(output_path, combined_data_struct)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()

