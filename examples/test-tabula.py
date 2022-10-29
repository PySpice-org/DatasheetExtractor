####################################################################################################

from pathlib import Path

import tabula

####################################################################################################

pdf_path = Path('.', 'devices', 'Infineon-1EDCxxI12AH-DataSheet-v02_00-EN.pdf')

df = tabula.read_pdf(
    pdf_path,
    output_format='dataframe',
    # output_format='json',
    pages=1,
    guess=True,
    # guess=False,
    # top,left,bottom,right
    # area=[54,4,71,96],
    relative_area=True,
    # lattice=True,
    stream=True,
    # columns=,
    # format='CSV',
    # format='TSV',
    # format='JSON',
)

df = df[0]

print(df.to_csv())

print(type(df))
print(df)
print('shape', df.shape)
print('number of rows', len(df))
print('index', df.index)
print('columns', df.columns)

for j in range(df.shape[1]):   # iterate over columns
    column_length = 0
    for i in range(df.shape[0]):   # iterate over rows
        value = df.iloc[i, j]   # get cell value
        column_length = max(len(str(value)), column_length)
    print(f'column length {column_length}')
