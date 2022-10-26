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
    # top,left,bottom,right
    # area=[50,0,90,100],
    relative_area=True,
    # lattice=True,
    stream=True,
    # columns=,
    # format='CSV',
    # format='TSV',
    # format='JSON',
)

df = df[0]
print(type(df))
print(df)
print(df.to_csv())
