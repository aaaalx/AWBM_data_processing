#==============================================================================
# Example script: Importing water daily SILO rainfall data and analysing to
#                 examine change in time periods between rainfall events.
#
#                 Uses daily rainfall from Blackbutt Post Office
#==============================================================================
# 0.0 ===== IMPORTING PACKAGES / MODULES ======================================
import pandas as pd        # Module used to import data
import numpy as np         # Pakage used for basic numerical functions
import csv                               # Imports csv module
import datetime                          # Imports module to convert dates
import time

# 1.0 ===== LOADING INPUT DATA ================================================
# infile_name = 'D:/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO_Gregors_1985-2020-pd.csv'
# outFileName1 = 'Output-RainfallEvents-SILO_Gregors_1985-2020.csv'
# outFileName2 = 'Output-DryEvents-SILO_Gregors_1985-2020.csv'

outFileName1 = 'Output-RainfallEvents-SILO_Full_1985-2020.csv'
outFileName2 = 'Output-DryEvents-SILO_Full_1985-2020.csv'
infile_name = 'D:/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO_Full_1985-2020-pd.csv'


tic_script = time.time()
df = pd.read_csv(infile_name)  # Read CSV file into Pandas data frame

data_Rain = pd.to_numeric(df['P[mm]'],errors="coerce") #Coverts to numeric
data_Date = pd.to_datetime(df['Date'], dayfirst=True)






# 2.0 ===== ANALYSING DATA ===================================================
# 2.1 ===== Basic analysis
RainDays = np.sum(data_Rain != 0) # Get total number of days with rain
DryDays = np.sum(data_Rain == 0)  # Get total number of days without rain

Thresh = 0 # Set a rainfall depth threshold
RainThresholdDays = np.sum(data_Rain > Thresh) # Get total days of rain above threshold

# 2.2 ===== Extracting Event Data
events_WetStart = []
events_WetEnd = []
events_WetDuration = []
events_WetMagnitude = []
events_DryStart = []
events_DryEnd = []
events_DryDuration = []
StartWet = data_Date[0]
StartDry = data_Date[0]
CummRain = 0

dims = np.size(data_Rain)-1
for i in range(1,dims):
    # Categorising wet events
    if data_Rain[i]>Thresh:
        if data_Rain[i-1] <= Thresh:
            StartWet = data_Date[i]
            CummRain = data_Rain[i]
        else:
            CummRain += data_Rain[i]
        if data_Rain[i+1] <= Thresh:
            EndWet = data_Date[i]
            DurationWet = EndWet - StartWet
            events_WetStart.append(StartWet)
            events_WetEnd.append(EndWet)
            events_WetDuration.append(DurationWet.days + 1)
            events_WetMagnitude.append(CummRain)
    # Categorising dry events
    if data_Rain[i] <= Thresh:
        if data_Rain[i-1] > Thresh:
            StartDry = data_Date[i]
        if data_Rain[i+1] > Thresh:
            EndDry = data_Date[i]
            DurationDry = EndDry - StartDry
            events_DryStart.append(StartDry)
            events_DryEnd.append(EndDry)
            events_DryDuration.append(DurationDry.days +1)


# 2.4 ===== Performing checks

            
# ===== 4.0 EXPORTING DATA ====================================================
print(' ')
print(' Exporting data to csv file ...')


header1 = ['Start Date', 'End Date','Duration','Magnitude']
header2 = ['[yyyy-mm-dd hh:mm:ss]', '[yyyy-mm-dd hh:mm:ss]', \
           '[days]','[mm]']
outData1 = zip(events_WetStart, events_WetEnd, events_WetDuration, \
              events_WetMagnitude)
with open(outFileName1,'w') as f:
    writer = csv.writer(f,lineterminator='\n')
    writer.writerow(header1)
    writer.writerow(header2)
    for row in outData1:
        writer.writerow(row)


header1 = ['Start Date', 'End Date','Duration']
header2 = ['[yyyy-mm-dd hh:mm:ss]', '[yyyy-mm-dd hh:mm:ss]','[days]']
outData2 = zip(events_DryStart, events_DryEnd, events_DryDuration)
with open(outFileName2,'w') as f:
    writer = csv.writer(f,lineterminator='\n')
    writer.writerow(header1)
    writer.writerow(header2)
    for row in outData2:
        writer.writerow(row)

print('      ... data exported to csv file.')
toc_script = time.time() - tic_script 
print(f'      ... script complete. t = {toc_script}')           
    
 
# =============================================================================
# ======== END OF SCRIPT ======== END OF SCRIPT ======== END OF SCRIPT ========
# =============================================================================