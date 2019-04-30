#-------------------------------------------------------------------------------
# Name:        concreteCalcs.py
# Purpose:
#
# Author:      tulery
#
# Created:     5/07/2013
# Copyright:   (c) HDR inc. 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, sys, os, math, datetime, textwrap
from arcpy import env
from multiprocessing.pool import TERMINATE
from decimal import ROUND_UP
from arcpy.sa.Functions import RoundUp

env.overwriteOutput = True

#Parameters
cceNo = arcpy.GetParameterAsText(0)
if cceNo == '#' or not cceNo:
    cceNo = "11-RS-810" # provide a default value if unspecified
userInit = arcpy.GetParameterAsText(1)
if userInit == '#' or not userInit:
    userInit = "TEST" # provide a default value if unspecified
reviewedBy = arcpy.GetParameterAsText(2)
if reviewedBy == '#' or not reviewedBy:
    reviewedBy = "Kristen Hahn" # provide a default value if unspecified
reviewByDate = arcpy.GetParameterAsText(3)
if reviewByDate == '#' or not reviewByDate:
    reviewByDate = "2/21/14" # provide a default value if unspecified
scratch_folder = arcpy.GetParameterAsText(4)
if scratch_folder == '#' or not scratch_folder:
    scratch_folder = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\working\Templates" # provide a default value if unspecified
SDE = arcpy.GetParameterAsText(5)
if SDE == '#' or not SDE:
    SDE = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\Lex_CDOT_Survey.sde\Lex_CDOT_Menu.DBO.Ops" # provide a default value if unspecified
target = arcpy.GetParameterAsText(6)
if target == '#' or not target:
    target = r"E:\gis\projects\IL\Chicago\CDOT_Menu_Pro\Spatial\gdb\Lex_CDOT_MapOutput.sde\Lex_CDOT_MapOutput.DBO.Calcs\Lex_CDOT_MapOutput.DBO.Blocks_FinalCalcs" # provide a default value if unspecified
arcpy.AddMessage("Assigning parameters for project " + cceNo)

projectType = cceNo.split('-')[1]

#Find corresponding combo number
if "-RS-" in cceNo:
    cceNo = cceNo.replace("-RS-", "-ASlRS-")
if "-RA-" in cceNo:
    cceNo = cceNo.replace("-RA-", "-AAlRA-")

scratch_folder = scratch_folder.replace('Templates', 'scratch')

today = datetime.datetime.now()
ts = today.strftime('%y%m%d_%H%M%S')
#Create Scratch GDB
scratchGDB = "CC_" + cceNo + "_" + userInit + "_" + ts + ".gdb"
arcpy.CreateFileGDB_management(scratch_folder, scratchGDB)
scratch = scratch_folder + "\\" + scratchGDB

descSDE = arcpy.Describe(SDE)
sdeName = descSDE.baseName[:-3]
print sdeName

sdePath = os.path.dirname(os.path.dirname(target))

descTarget = arcpy.Describe(target)
targetName = descTarget.name[:-17]
print targetName



# Establish Variable for SDE Street Calcs *If the direct connection to Feature class will be different
swRampRemove = SDE + "\\" + sdeName + "SidewalkRampRemove"
swRamp = SDE + "\\" + sdeName + "SidewalkRamp"
swOmit = SDE + "\\" + sdeName + "SidewalkOmit"
sw = SDE + "\\" + sdeName + "Sidewalk"
rOmit = SDE + "\\" + sdeName + "SidewalkRampOmit"
c_Paveave = SDE + "\\" + sdeName + "ConcretePavement"
cBusPad = SDE + "\\" + sdeName + "ConcreteBusPad"
aPave = SDE + "\\" + sdeName + "AlleyPavement"
aDrive = SDE + "\\" + sdeName + "AlleyDriveway"
aDriveRemove = SDE + "\\" + sdeName + "DrivewayRemove"
cGutter = SDE + "\\" + sdeName + "CurbGutter"
BikeRack = SDE + "\\" + sdeName + "BikeRack"
# Block and Project already queried
##blockCL = preGDB + "\\" + "BlockCenterline"
blockCL = SDE + "\\" + sdeName + "BlockCenterline"
##projectCL = preGDB + "\\" + "ProjectCenterline"
projectCL = SDE + "\\" + sdeName + "ProjectCenterline"
# Reference of IHC AR CC CO CS Calc Sheet Pavement Markings # Run already for query from street calcs
PaveMarks = SDE + "\\" + sdeName + "PavementMarking"
#tblMenu
tblMenu = sdePath + "\\" + targetName + "tblMenu"

# Final Calcs
FinalCalcs = target
desc = arcpy.Describe(FinalCalcs)
print desc.file

# Create Table View for Selections
print "Creating Table Views..."
swRampRemoveView = arcpy.MakeTableView_management(swRampRemove, "swRampRemoveView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')"); print "..."
swRampView = arcpy.MakeTableView_management(swRamp, "swRampView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
swOmitView = arcpy.MakeTableView_management(swOmit, "swOmitView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
swView = arcpy.MakeTableView_management(sw, "swView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
rOmitView = arcpy.MakeTableView_management(rOmit, "rOmitView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
c_PaveaveView = arcpy.MakeTableView_management(c_Paveave, "c_PaveaveView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
cBusPadView = arcpy.MakeTableView_management(cBusPad, "cBusPadView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
aPaveView = arcpy.MakeTableView_management(aPave, "aPaveView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
aDriveView = arcpy.MakeTableView_management(aDrive, "aDriveView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
aDriveRemoveView = arcpy.MakeTableView_management(aDriveRemove, "aDriveRemoveView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
cGutterView = arcpy.MakeTableView_management(cGutter, "cGutterView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
paveMarksView = arcpy.MakeTableView_management(PaveMarks, "paveMarksView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
bikeRackView = arcpy.MakeTableView_management(BikeRack, "bikeRackView", "strCCEProjectNumber = '" + cceNo + "' AND(OmitYN IS NULL OR OmitYN = 'No')")
blockView = arcpy.MakeTableView_management(blockCL, "blockView", "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
projectView = arcpy.MakeTableView_management(projectCL, "projectView", "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")


print "Creating Table copies..."
# Create Copy rows from queried table views
swRampRemoveCopy = arcpy.CopyRows_management(swRampRemoveView, scratch + "\\" + "swRampRemoveCopy")
swRampCopy = arcpy.CopyRows_management(swRampView, scratch + "\\" + "swRampCopy")
swOmitCopy = arcpy.CopyRows_management(swOmitView, scratch + "\\" + "swOmitCopy")
swCopy = arcpy.CopyRows_management(swView, scratch + "\\" + "swCopy")
rOmitCopy = arcpy.CopyRows_management(rOmitView, scratch + "\\" + "rOmitCopy")
c_PaveaveCopy = arcpy.CopyRows_management(c_PaveaveView, scratch + "\\" + "c_PaveaveCopy")
cBusPadCopy = arcpy.CopyRows_management(cBusPadView, scratch + "\\" + "cBusPadCopy")
aPaveCopy = arcpy.CopyRows_management(aPaveView, scratch + "\\" + "aPaveCopy")
aDriveCopy = arcpy.CopyRows_management(aDriveView, scratch + "\\" + "aDriveCopy")
aDriveRemoveCopy = arcpy.CopyRows_management(aDriveRemoveView, scratch + "\\" + "aDriveRemoveCopy")
cgCopy = arcpy.CopyRows_management(cGutterView, scratch + "\\" + "cgutterCopy")
paveMarksCopy = arcpy.CopyRows_management(paveMarksView, scratch + "\\" + "paveMarksCopy")
bikeRackCopy = arcpy.CopyRows_management(bikeRackView, scratch + "\\" + "bikeRackCopy")
blockCopy = arcpy.CopyRows_management(blockView, scratch + "\\" + "blockCopy")
projectCopy = arcpy.CopyRows_management(projectView, scratch + "\\" + "projectCopy")

#AutoComments Dictionary Population Function
def updateAutoCommentsDict(pref, fieldName, includeFieldYN):

    if includeFieldYN:
        fieldValue = row.getValue(fieldName)
        if fieldValue == None:
            fieldValue = ""

        if len(AutoComments_Dict[pageNo]) == 0:
            AutoComments_Dict.update({pageNo : pref +": " + fieldValue})
        else:
            AutoComments_Dict.update({pageNo : AutoComments_Dict[pageNo] + "; " + pref + ": " + fieldValue})
    else:
        if len(AutoComments_Dict[pageNo]) == 0:
            AutoComments_Dict.update({pageNo : pref})
        else:
            AutoComments_Dict.update({pageNo : AutoComments_Dict[pageNo] + "; " + pref})

#AutoComments Dictionary Population Function
def checkStrForNull(fieldName):
    fieldValue = row.getValue(fieldName)
    if fieldValue == None:
        fieldValue = ""
    return fieldValue


"""May Need to setup a summary table to hold values with key---SAH"""

# Add Fields
# arcpy.AddField_management(streetCopy, "MainlineArea", "DOUBLE", "", 2, "", "", "NULLABLE"); print "Area field added..."
# arcpy.AddField_management(streetCopy, "Str_Ave_Slope", "DOUBLE", "", "", "", "", "NULLABLE"); print "Average slope field added..."
# arcpy.AddField_management(streetCopy, "Str_Ave_Depth", "DOUBLE", "", "", "", "", "NULLABLE"); print "Average depth field added..."
# arcpy.AddField_management(streetCopy, "Grindings", "LONG", "", "", "", "", "NULLABLE"); print "Grindings field added..."

# Lists and Dictionaries
print "Exstablishing Dictionaries..."
# CurbGutter
print "..."
T3L = {} #T3 Length
T3rL = {} #T3 Parkway Restoration Length
T3RL = {} #T3R Length
T3RrL = {} #T3R Parkway Restoration Length
T3AL = {} #T3 Arterial Length
T3ArL = {} #T3 Arterial Parkway Restoration Length
T3ARL = {} #T3R Arterial Length
T3ARrL = {} #T3R Arterial Parkway Restoration Length
T3DWL = {} #T3 D/W Alley Residential Length
T3DWAL = {} #T3 D/W Alley Arterial Length
T4L = {} #T4 Length
T4rL = {} #T4 Parkway Restoration Length
T4RL = {} #T4R Length
T4RrL = {} #T4R Parkway Restoration Length

# SideWalk
print "..."
PCC_5_SF = {} #5in PCC Sidewalk Area (SF)
PCC_5_RL = {} #5in PCC Sidewalk Restoration Length
PCC_5_rmp_SF = {} #5in PCC Sidewalk Ramp Area (SF)
PCC_5_rmp_RL = {} #5in PCC Sidewalk Ramp Restoration Length
PCC_8_SF = {} #8in PCC Sidewalk Area (SF)
PCC_8_RL = {} #8in PCC Sidewalk Restoration Length
PCC_8_rmp_SF = {} #8in PCC Sidewalk Ramp Area (SF)
PCC_8_rmp_RL = {} #8in PCC Sidewalk Ramp Restoration Length
Side_rmp_Remove = {} #Sidewalk/Ramp Remove Only

""" **UPDATED PER REVISIONS """
HES_PCC_Sidewalk_8in = {} #High Early Strength PCC Sidewalk 8 inch
"""**"""

# Alley Driveway and H.E.S Alley/Driveway Pavement
print "..."
PCC_Driveway = {} #PCC Driveway (SY)
PCC_Alley = {} #PCC Alley (SY)
Drive_Alley_ATO = {} #Driveway/Alley ATO (SY)
Drive_Alley_ATO_Tons = {}  #Driveway/Alley ATO (Tons)

""" **UPDATED PER REVISIONS """
HES_PCC_Alley_8in = {} #High Early Strength PCC Alley Pavement 8 inch
HES_PCC_Driveway_8in = {} #High Early Strength PCC Driveway Pavement 8 inch
"""**"""

# Pavement
print "..."
Drive_Remove = {} #Driveway Remove Only
c_BusPad = {} #Concrete Bus Pad
c_BusPad_L = {} #Concrete Bus Pad Length
c_BusPad_W = {} #Concrete Bus Pad Width
c_Pave = {} #Concrete Pavement
c_Pave_L = {} #Concrete Pavement Length
c_Pave_W = {} #Concrete Pavement Width
PCC_Pave10in = {} #PCC Pavement 10 inch """UPDATED PER REVISION"""
PCC_Pave12in = {} #PCC Pavement 12 inch """UPDATED PER REVISION"""
Prot_Conc_Sealer = {} #Protective Concrete Sealer

# Pavement Marking Dictionaries # MAKE NOTE
SDC_Dict = {} #Standard Crosswalk
DYC_Dict = {} #International Crosswalk
SB_Dict = {} #Stop Bar
IC_Dict = {} #Skip Dash Centerline
SC_Dict = {} #Double Yellow Centerline

#Block Centerline Dictionaries
TreesInPits_No_Dict = {}
NumberInRamps5in_Dict = {}
NumberInRamps8in_Dict = {}
DrainUtil_Adjusted_No_Dict = {}
WaterServ_Box_No_Dict = {}
DrainStruct_Clean_No_Dict = {}
Tree_Protect_No_Dict = {}
RootPruning_No_Dict = {}
AlleyApron_Recon_No_Dict = {}

#Misc Block Dictionaries
CornerHouse_Dict = {}

#Auto-Comments Dictionary
AutoComments_Dict = {}

#Bike Rack Type Dictionary
BikeRack_Dict = {}

#Ramp Status Dictionary
RampStatus_Dict = {}

""" All dictionaries should be set to pageNo : 0.0 by running a search cursor on BlockCenterline ---SAH"""

# Setting Dictionaries
print "Setting Ditionary values to 0.0..."
# CurbGutter
s_cursor = arcpy.SearchCursor(blockCL, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
count =  0
for row in s_cursor:
    pageNo = row.getValue("PageNo"); print "..."
    """Add SurveyBy value for Final Calcs"""#TBU-0123-2014
    SurveyBy = row.getValue("SurveyBy")
    SurveyByDate = row.getValue("SurveyByDate")
    value = 0.0
    #Fill 12 Dictionaries for T3 and T4
    #T3L
    if pageNo in T3L:
        T3L.update({pageNo : T3L[pageNo] + value})
    elif pageNo not in T3L:
        T3L.update({pageNo : value})
    #T3rL
    if pageNo in T3rL:
        T3rL.update({pageNo : T3rL[pageNo] + value})
    elif pageNo not in T3rL:
        T3rL.update({pageNo : value})
    #T3RL
    if pageNo in T3RL:
        T3RL.update({pageNo : T3RL[pageNo] + value})
    elif pageNo not in T3RL:
        T3RL.update({pageNo : value})
    #T3RrL
    if pageNo in T3RrL:
        T3RrL.update({pageNo : T3RrL[pageNo] + value})
    elif pageNo not in T3RrL:
        T3RrL.update({pageNo : value})
    #T3AL
    if pageNo in T3AL:
        T3AL.update({pageNo : T3AL[pageNo] + value})
    elif pageNo not in T3AL:
        T3AL.update({pageNo : value})
    #T3ArL
    if pageNo in T3ArL:
        T3ArL.update({pageNo : T3ArL[pageNo] + value})
    elif pageNo not in T3ArL:
        T3ArL.update({pageNo : value})
    #T3ARL
    if pageNo in T3ARL:
        T3ARL.update({pageNo : T3ARL[pageNo] + value})
    elif pageNo not in T3ARL:
        T3ARL.update({pageNo : value})
    #T3ARrL
    if pageNo in T3ARrL:
        T3ARrL.update({pageNo : T3ARrL[pageNo] + value})
    elif pageNo not in T3ARrL:
        T3ARrL.update({pageNo : value})
    #T3DWL * ADDED FROM NEW REVISIONS
    if pageNo in T3DWL:
        T3DWL.update({pageNo : T3DWL[pageNo] + value})
    elif pageNo not in T3DWL:
        T3DWL.update({pageNo : value})
    #T3DWAL * ADDED FROM NEW REVISIONS
    if pageNo in T3DWAL:
        T3DWAL.update({pageNo : T3DWAL[pageNo] + value})
    elif pageNo not in T3DWAL:
        T3DWAL.update({pageNo : value})
    #T4L
    if pageNo in T4L:
        T4L.update({pageNo : T4L[pageNo] + value})
    elif pageNo not in T4L:
        T4L.update({pageNo : value})
    #T4rL
    if pageNo in T4rL:
        T4rL.update({pageNo : T4rL[pageNo] + value})
    elif pageNo not in T4rL:
        T4rL.update({pageNo : value})
    #T4RL
    if pageNo in T4RL:
        T4RL.update({pageNo : T4RL[pageNo] + value})
    elif pageNo not in T4RL:
        T4RL.update({pageNo : value})
    #T4RrL
    if pageNo in T4RrL:
        T4RrL.update({pageNo : T4RrL[pageNo] + value})
    elif pageNo not in T4RrL:
        T4RrL.update({pageNo : value})
    # PCC_5_SF
    if pageNo in PCC_5_SF:
        PCC_5_SF.update({pageNo : PCC_5_SF[pageNo] + value})
    elif pageNo not in PCC_5_SF:
        PCC_5_SF.update({pageNo : value})
    # PCC_5_RL
    if pageNo in PCC_5_RL:
        PCC_5_RL.update({pageNo : PCC_5_RL[pageNo] + value})
    elif pageNo not in PCC_5_RL:
        PCC_5_RL.update({pageNo : value})
    # PCC_5_rmp_SF
    if pageNo in PCC_5_rmp_SF:
        PCC_5_rmp_SF.update({pageNo : PCC_5_rmp_SF[pageNo] + value})
    elif pageNo not in PCC_5_rmp_SF:
        PCC_5_rmp_SF.update({pageNo : value})
    # PCC_5_rmp_RL
    if pageNo in PCC_5_rmp_RL:
        PCC_5_rmp_RL.update({pageNo : PCC_5_rmp_RL[pageNo] + value})
    elif pageNo not in PCC_5_rmp_RL:
        PCC_5_rmp_RL.update({pageNo : value})
    # PCC_8_SF
    if pageNo in PCC_8_SF:
        PCC_8_SF.update({pageNo : PCC_8_SF[pageNo] + value})
    elif pageNo not in PCC_8_SF:
        PCC_8_SF.update({pageNo : value})
    # PCC_8_RL
    if pageNo in PCC_8_RL:
        PCC_8_RL.update({pageNo : PCC_8_RL[pageNo] + value})
    elif pageNo not in PCC_8_RL:
        PCC_8_RL.update({pageNo : value})
    # PCC_8_rmp_SF
    if pageNo in PCC_8_rmp_SF:
        PCC_8_rmp_SF.update({pageNo : PCC_8_rmp_SF[pageNo] + value})
    elif pageNo not in PCC_8_rmp_SF:
        PCC_8_rmp_SF.update({pageNo : value})
    # PCC_8_rmp_RL
    if pageNo in PCC_8_rmp_RL:
        PCC_8_rmp_RL.update({pageNo : PCC_8_rmp_RL[pageNo] + value})
    elif pageNo not in PCC_8_rmp_RL:
        PCC_8_rmp_RL.update({pageNo : value})
    # Side_rmp_Remove
    if pageNo in Side_rmp_Remove:
        Side_rmp_Remove.update({pageNo : Side_rmp_Remove[pageNo] + value})
    elif pageNo not in Side_rmp_Remove:
        Side_rmp_Remove.update({pageNo : value})
    # PCC_Driveway
    if pageNo in PCC_Driveway:
        PCC_Driveway.update({pageNo : PCC_Driveway[pageNo] + value})
    elif pageNo not in PCC_Driveway:
        PCC_Driveway.update({pageNo : value})
    # PCC_Alley
    if pageNo in PCC_Alley:
        PCC_Alley.update({pageNo : PCC_Alley[pageNo] + value})
    elif pageNo not in PCC_Alley:
        PCC_Alley.update({pageNo : value})
    # Drive_Alley_ATO
    if pageNo in Drive_Alley_ATO:
        Drive_Alley_ATO.update({pageNo : Drive_Alley_ATO[pageNo] + value})
    elif pageNo not in Drive_Alley_ATO:
        Drive_Alley_ATO.update({pageNo : value})
    # Drive_Alley_ATO_Tons
    if pageNo in Drive_Alley_ATO_Tons:
        Drive_Alley_ATO_Tons.update({pageNo : Drive_Alley_ATO_Tons[pageNo] + value})
    elif pageNo not in Drive_Alley_ATO_Tons:
        Drive_Alley_ATO_Tons.update({pageNo : value})
    # Drive_Remove
    if pageNo in Drive_Remove:
        Drive_Remove.update({pageNo : Drive_Remove[pageNo] + value})
    elif pageNo not in Drive_Remove:
        Drive_Remove.update({pageNo : value})
    # c_BusPad
    if pageNo in c_BusPad:
        c_BusPad.update({pageNo : c_BusPad[pageNo] + value})
    elif pageNo not in c_BusPad:
        c_BusPad.update({pageNo : value})
    # c_BusPad_L
    if pageNo in c_BusPad_L:
        c_BusPad_L.update({pageNo : c_BusPad_L[pageNo] + value})
    elif pageNo not in c_BusPad_L:
        c_BusPad_L.update({pageNo : value})
    # c_BusPad_W
    if pageNo in c_BusPad_W:
        c_BusPad_W.update({pageNo : c_BusPad_W[pageNo] + value})
    elif pageNo not in c_BusPad_W:
        c_BusPad_W.update({pageNo : value})
    # c_Pave
    if pageNo in c_Pave:
        c_Pave.update({pageNo : c_Pave[pageNo] + value})
    elif pageNo not in c_Pave:
        c_Pave.update({pageNo : value})
    # c_Pave_L
    if pageNo in c_Pave_L:
        c_Pave_L.update({pageNo : c_Pave_L[pageNo] + value})
    elif pageNo not in c_Pave_L:
        c_Pave_L.update({pageNo : value})
    # c_Pave_W
    if pageNo in c_Pave_W:
        c_Pave_W.update({pageNo : c_Pave_W[pageNo] + value})
    elif pageNo not in c_Pave_W:
        c_Pave_W.update({pageNo : value})
    # Prot_Conc_Sealer """UPDATED PER REVISION"""
    if pageNo in Prot_Conc_Sealer:
        Prot_Conc_Sealer.update({pageNo : Prot_Conc_Sealer[pageNo] + value})
    elif pageNo not in Prot_Conc_Sealer:
        Prot_Conc_Sealer.update({pageNo : value})

    """ **UPDATES PER REVISIONS """
    # PCC_Pave10in
    if pageNo in PCC_Pave10in:
        PCC_Pave10in.update({pageNo : PCC_Pave10in[pageNo] + value})
    elif pageNo not in PCC_Pave10in:
        PCC_Pave10in.update({pageNo : value})
    # PCC_Pave12in
    if pageNo in PCC_Pave12in:
        PCC_Pave12in.update({pageNo : PCC_Pave12in[pageNo] + value})
    elif pageNo not in PCC_Pave12in:
        PCC_Pave12in.update({pageNo : value})

    # HES_PCC_Alley_8in
    if pageNo in HES_PCC_Alley_8in:
        HES_PCC_Alley_8in.update({pageNo : HES_PCC_Alley_8in[pageNo] + value})
    elif pageNo not in HES_PCC_Alley_8in:
        HES_PCC_Alley_8in.update({pageNo : value})
    # HES_PCC_Driveway_8in
    if pageNo in HES_PCC_Driveway_8in:
        HES_PCC_Driveway_8in.update({pageNo : HES_PCC_Driveway_8in[pageNo] + value})
    elif pageNo not in HES_PCC_Driveway_8in:
        HES_PCC_Driveway_8in.update({pageNo : value})
    # HES_PCC_Sidewalk_8in
    if pageNo in HES_PCC_Sidewalk_8in:
        HES_PCC_Sidewalk_8in.update({pageNo : HES_PCC_Sidewalk_8in[pageNo] + value})
    elif pageNo not in HES_PCC_Sidewalk_8in:
        HES_PCC_Sidewalk_8in.update({pageNo : value})


    """**"""

    # Pavement Markings Set for 0.0
    if pageNo in SDC_Dict:
        SDC_Dict.update({pageNo : SDC_Dict[pageNo] + value})
    elif pageNo not in SDC_Dict:
        SDC_Dict.update({pageNo : value})
    if pageNo in DYC_Dict:
        DYC_Dict.update({pageNo : DYC_Dict[pageNo] + value})
    elif pageNo not in DYC_Dict:
        DYC_Dict.update({pageNo : value})
    if pageNo in SB_Dict:
        SB_Dict.update({pageNo : SB_Dict[pageNo] + value})
    elif pageNo not in SB_Dict:
        SB_Dict.update({pageNo : value})
    if pageNo in IC_Dict:
        IC_Dict.update({pageNo : IC_Dict[pageNo] + value})
    elif pageNo not in IC_Dict:
        IC_Dict.update({pageNo : value})
    if pageNo in SC_Dict:
        SC_Dict.update({pageNo : SC_Dict[pageNo] + value})
    elif pageNo not in SC_Dict:
        SC_Dict.update({pageNo : value})

    TreesInPits_No_Dict.update({pageNo : value})
    NumberInRamps5in_Dict.update({pageNo : value})
    NumberInRamps8in_Dict.update({pageNo : value})
    DrainUtil_Adjusted_No_Dict.update({pageNo : value})
    WaterServ_Box_No_Dict.update({pageNo : value})
    DrainStruct_Clean_No_Dict.update({pageNo : value})
    Tree_Protect_No_Dict.update({pageNo : value})
    RootPruning_No_Dict.update({pageNo : value})
    AlleyApron_Recon_No_Dict.update({pageNo : value})

    #Misc Block Dictionaries
    CornerHouse_Dict.update({pageNo : ""})

    AutoComments_Dict.update({pageNo : ""})

    BikeRack_Dict.update({pageNo : ""})

    RampStatus_Dict.update({pageNo : ""})

    print "Row Number... " + str(count)
    count = count + 1
del s_cursor


#Update Dictionaries for Curb/Gutter lengths and parkway resoration lengths
print "Updating Dictionaries for T3 and T4..."
arcpy.AddMessage("Processing Curbgutter data from project " + cceNo)
s_cursor = arcpy.SearchCursor(cgCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
count = 1
for row in s_cursor:
    pageNo = row.getValue("PageNo")
    length = row.getValue("MeasureLength")
    LengthR = row.getValue("ParkwayRestorationLength")
    measureType = row.getValue("MeasureType")
    #T3L
    if measureType == "T3 Residential":
        if pageNo in T3L:
            T3L.update({pageNo : T3L[pageNo] + length}); print "...T3L"
        elif pageNo not in T3L:
            T3L.update({pageNo : length}); print "...T3L"
    #T3rL
    if measureType == "T3 Residential":
        if pageNo in T3rL:
            T3rL.update({pageNo : T3rL[pageNo] + LengthR}); print "...T3rL"
        elif pageNo not in T3rL:
            T3rL.update({pageNo : LengthR}); print "...T3rL"
    #T3RL
    if measureType == "T3R Residential":
        if pageNo in T3RL:
            T3RL.update({pageNo : T3RL[pageNo] + length}); print "...T3RL"
        elif pageNo not in T3RL:
            T3RL.update({pageNo : length}); print "...T3RL"
    #T3RrL
    if measureType == "T3R Residential":
        if pageNo in T3RrL:
            T3RrL.update({pageNo : T3RrL[pageNo] + LengthR}); print "...T3RrL"
        elif pageNo not in T3RrL:
            T3RrL.update({pageNo : LengthR}); print "...T3RrL"
    #T3AL
    if measureType == "T3 Arterial":
        if pageNo in T3AL:
            T3AL.update({pageNo : T3AL[pageNo] + length}); print "...T3AL"
        elif pageNo not in T3AL:
            T3AL.update({pageNo : length}); print "...T3AL"
    #T3ArL
    if measureType == "T3 Arterial":
        if pageNo in T3ArL:
            T3ArL.update({pageNo : T3ArL[pageNo] + LengthR}); print "...T3ArL"
        elif pageNo not in T3ArL:
            T3ArL.update({pageNo : LengthR}); print "...T3ArL"
    #T3ARL
    if measureType == "T3R Arterial":
        if pageNo in T3ARL:
            T3ARL.update({pageNo : T3ARL[pageNo] + length}); print "...T3ARL"
        elif pageNo not in T3ARL:
            T3ARL.update({pageNo : length}); print "...T3ARL"
    #T3ARrL
    if measureType == "T3R Arterial":
        if pageNo in T3ARrL:
            T3ARrL.update({pageNo : T3ARrL[pageNo] + LengthR}); print "...T3ARrL"
        elif pageNo not in T3ARrL:
            T3ARrL.update({pageNo : LengthR}); print "...T3ARrL"
    #T3DWL * ADDED WITH NEW REVISION
    if measureType == "T3 D/W Alley Residential":
        if pageNo in T3DWL:
            T3DWL.update({pageNo : T3DWL[pageNo] + length}); print "...T3DWL"
        elif pageNo not in T3DWL:
            T3DWL.update({pageNo : length}); print "...T3DWL"
    #T3DWAL * ADDED WITH NEW REVISION
    if measureType == "T3 D/W Alley Arterial":
        if pageNo in T3DWAL:
            T3DWAL.update({pageNo : T3DWAL[pageNo] + length}); print "...T3DWAL"
        elif pageNo not in T3DWAL:
            T3DWAL.update({pageNo : length}); print "...T3DWAL"
    #T4L
    if measureType == "T4":
        if pageNo in T4L:
            T4L.update({pageNo : T4L[pageNo] + length}); print "...T4L"
        elif pageNo not in T4L:
            T4L.update({pageNo : length}); print "...T4L"
    #T4rL
    if measureType == "T4":
        if pageNo in T4rL:
            T4rL.update({pageNo : T4rL[pageNo] + LengthR}); print "...T4rL"
        elif pageNo not in T4rL:
            T4rL.update({pageNo : LengthR}); print "...T4rL"
    #T4RL
    if measureType == "T4R":
        if pageNo in T4RL:
            T4RL.update({pageNo : T4RL[pageNo] + length}); print "...T4RL"
        elif pageNo not in T4RL:
            T4RL.update({pageNo : length}); print "...T4RL"
    #T4RrL
    if measureType == "T4R":
        if pageNo in T4RrL:
            T4RrL.update({pageNo : T4RrL[pageNo] + LengthR}); print "...T4RrL"
        elif pageNo not in T4RrL:
            T4RrL.update({pageNo : LengthR}); print "...T4RrL"

    print "Row Number... " + str(count)
    count = count + 1
del s_cursor

# SideWalk
print "Updating Dictionaries for Sidewalk..."
arcpy.AddMessage("Processing Sidewalk data from project " + cceNo)
count = 0
s_cursor = arcpy.SearchCursor(swCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:
    pageNo = row.getValue("PageNo")
    areaSF = row.getValue("MeasureLength") * row.getValue("MeasureWidth")
    LengthR = row.getValue("ParkwayRestorationLength")
    DWArea = row.getValue("MeasureLength") + row.getValue("MeasureWidth")
    measureType = row.getValue("MeasureType")
    # PCC_5_SF
    if measureType == "5 in. PCC Sidewalk":
        if pageNo in PCC_5_SF:
            PCC_5_SF.update({pageNo : PCC_5_SF[pageNo] + areaSF}); print "...PCC_5_SF"
        elif pageNo not in PCC_5_SF:
            PCC_5_SF.update({pageNo : areaSF}); print "...PCC_5_SF"
    # PCC_5_RL
    if measureType == "5 in. PCC Sidewalk":
        if pageNo in PCC_5_RL:
            PCC_5_RL.update({pageNo : PCC_5_RL[pageNo] + LengthR}); print "...PCC_5_RL"
        elif pageNo not in PCC_5_RL:
            PCC_5_RL.update({pageNo : LengthR}); print "...PCC_5_RL"
    # PCC_8_SF
    if measureType == "8 in. PCC Sidewalk":
        if pageNo in PCC_8_SF:
            PCC_8_SF.update({pageNo : PCC_8_SF[pageNo] + areaSF}); print "...PCC_8_SF"
        elif pageNo not in PCC_8_SF:
            PCC_8_SF.update({pageNo : areaSF}); print "...PCC_8_SF"
    # PCC_8_RL
    if measureType == "8 in. PCC Sidewalk":
        if pageNo in PCC_8_RL:
            PCC_8_RL.update({pageNo : PCC_8_RL[pageNo] + LengthR}); print "...PCC_8_RL"
        elif pageNo not in PCC_8_RL:
            PCC_8_RL.update({pageNo : LengthR}); print "...PCC_8_RL"
        """ ** UPDATES PER REVISIONS"""
        # HES_PCC_Sidewalk_8in
        #if measureType == "D":'
        if pageNo in HES_PCC_Sidewalk_8in:
            HES_PCC_Sidewalk_8in.update({pageNo : HES_PCC_Sidewalk_8in[pageNo] + areaSF}); print "...HES_PCC_Sidewalk_8in"
        elif pageNo not in HES_PCC_Sidewalk_8in:
            HES_PCC_Sidewalk_8in.update({pageNo : areaSF}); print "...HES_PCC_Sidewalk_8in"
    """**"""

    print "Row Number... " + str(count)
    count = count + 1
del s_cursor

############ JUST ADDEDEDEDEDED ##############
# SideWalk Ramp
print "Updating Dictionaries for Sidewalk Ramp..."
arcpy.AddMessage("Processing Sidewalk Ramp data from project " + cceNo)
count = 0
s_cursor = arcpy.SearchCursor(swRampCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:
    pageNo = row.getValue("PageNo")
    areaSF = row.getValue("MeasureLength") * row.getValue("MeasureWidth")
    LengthR = row.getValue("ParkwayRestorationLength")
    measureType = row.getValue("MeasureType")
    RampStatus = row.getValue("RampStatus")
    RampStatusText = checkStrForNull("RampStatusText")
    RampStatusOther = checkStrForNull("RampStatusOther")


    # PCC_5_rmp_SF
    if measureType == "5 in. PCC Sidewalk Ramp":
        if pageNo in PCC_5_rmp_SF:
            PCC_5_rmp_SF.update({pageNo : PCC_5_rmp_SF[pageNo] + areaSF})
        elif pageNo not in PCC_5_rmp_SF:
            PCC_5_rmp_SF.update({pageNo : areaSF})
    # PCC_5_rmp_RL
    if measureType == "5 in. PCC Sidewalk Ramp":
        if pageNo in PCC_5_rmp_RL:
            PCC_5_rmp_RL.update({pageNo : PCC_5_rmp_RL[pageNo] + LengthR})
        elif pageNo not in PCC_5_rmp_RL:
            PCC_5_rmp_RL.update({pageNo : LengthR})
    # PCC_8_rmp_SF
    if measureType == "8 in. PCC Sidewalk Ramp":
        if pageNo in PCC_8_rmp_SF:
            PCC_8_rmp_SF.update({pageNo : PCC_8_rmp_SF[pageNo] + areaSF})
        elif pageNo not in PCC_8_rmp_SF:
            PCC_8_rmp_SF.update({pageNo : areaSF})
    # PCC_8_rmp_RL
    if measureType == "8 in. PCC Sidewalk Ramp":
        if pageNo in PCC_8_rmp_RL:
            PCC_8_rmp_RL.update({pageNo : PCC_8_rmp_RL[pageNo] + LengthR})
        elif pageNo not in PCC_8_rmp_RL:
            PCC_8_rmp_RL.update({pageNo : LengthR})


    if "tiles, but" in RampStatus:
        if len(RampStatus_Dict[pageNo]) == 0:
            RampStatus_Dict.update({pageNo : RampStatusText + ": existing ramp has tiles, but non-compliant"})
        else:
            RampStatus_Dict.update({pageNo : RampStatus_Dict[pageNo] + "; " + RampStatusText + ": existing ramp has tiles, but non-compliant"})

    if "parking IS NOT" in RampStatus:
        if len(RampStatus_Dict[pageNo]) == 0:
            RampStatus_Dict.update({pageNo : RampStatusText + ": Parking sign coord"})
        else:
            RampStatus_Dict.update({pageNo : RampStatus_Dict[pageNo] + "; " + RampStatusText + ": Parking sign coord"})
    #Other Ramp Status commented out for now
##    if RampStatus == "Other":
##        if len(RampStatus_Dict[pageNo]) == 0:
##            RampStatus_Dict.update({pageNo : "Other Ramp Status: " + RampStatusOther})
##        else:
##            RampStatus_Dict.update({pageNo : RampStatus_Dict[pageNo] + "; Other Ramp Status: " + RampStatusOther})

    print "Row Number... " + str(count)
    count = count + 1
del s_cursor
########### JUST ADDEDEDEDEDED ##############

"""Corrected the below calc to be for Square Yards instead of square feet ---SAH"""
# Sidewalk/Ramp Remove
print "Updating Dictionaries for Sidewalk/Ramp Remove..."
arcpy.AddMessage("Processing Sidewalk Ramp/Remove data from project " + cceNo)
s_cursor = arcpy.SearchCursor(swRampRemoveCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
count = 0
for row in s_cursor:
    pageNo = row.getValue("PageNo")
    areaSF = (row.getValue("MeasureLength") * row.getValue("MeasureWidth"))
    areaSY = areaSF / 9.0
    if pageNo in Side_rmp_Remove:
        Side_rmp_Remove.update({pageNo : Side_rmp_Remove[pageNo] + areaSY}); print "...Side_rmp_Remove"
    elif pageNo not in Side_rmp_Remove:
        Side_rmp_Remove.update({pageNo : areaSY}); print "...Side_rmp_Remove"

    print "Row Number... " + str(count)
    count = count + 1
del s_cursor

# Alley Driveway
print "Updating Dictionaries for Alley Driveway..."
arcpy.AddMessage("Processing Alley Driveway data from project " + cceNo)
s_cursor = arcpy.SearchCursor(aDriveCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
count = 0
for row in s_cursor:
    pageNo = row.getValue("PageNo")
    measureType = row.getValue("MeasureType")
    areaSF = (row.getValue("MeasureLength") * row.getValue("MeasureWidth"))
    areaSY = (row.getValue("MeasureLength") * row.getValue("MeasureWidth")) / 9.0
    ## CHECK THE CALCS TO SEE IF FORMULA IS WRITTEN CORRECTLY ##
    TON = ((areaSF / 9.0) * 2.0 * 112.0) / 2000.0
    # PCC_Driveway
    if measureType == "PCC Driveway":
        if pageNo in PCC_Driveway:
            PCC_Driveway.update({pageNo : PCC_Driveway[pageNo] + areaSY}); print "...PCC_Driveway"
        elif pageNo not in PCC_Driveway:
            PCC_Driveway.update({pageNo : value}); print "...PCC_Driveway"
        # HES_PCC_Driveway_8in
        if pageNo in HES_PCC_Driveway_8in:
            HES_PCC_Driveway_8in.update({pageNo : HES_PCC_Driveway_8in[pageNo] + areaSY}); print "...HES_PCC_Driveway_8in"
        elif pageNo not in HES_PCC_Driveway_8in:
            HES_PCC_Driveway_8in.update({pageNo : areaSY}); print "...HES_PCC_Driveway_8in"
    # PCC_Alley
    if measureType == "PCC Alley":
        if pageNo in PCC_Alley:
            PCC_Alley.update({pageNo : PCC_Alley[pageNo] + areaSY}); print "...PCC_Alley"
        elif pageNo not in PCC_Alley:
            PCC_Alley.update({pageNo : value}); print "...PCC_Alley"
        # HES_PCC_Alley_8in
        if pageNo in HES_PCC_Alley_8in:
            HES_PCC_Alley_8in.update({pageNo : HES_PCC_Alley_8in[pageNo] + areaSY}); print "...HES_PCC_Alley_8in"
        elif pageNo not in HES_PCC_Alley_8in:
            HES_PCC_Alley_8in.update({pageNo : areaSY}); print "...HES_PCC_Alley_8in"
    # Drive_Alley_ATO """UPDATED PER REVISION"""
    if measureType == "Driveway/Alley ATO":
        if pageNo in Drive_Alley_ATO:
            Drive_Alley_ATO.update({pageNo : Drive_Alley_ATO[pageNo] + areaSY}); print "...Drive_Alley_ATO"
        elif pageNo not in Drive_Alley_ATO:
            Drive_Alley_ATO.update({pageNo : value}); print "...Drive_Alley_ATO"

        if pageNo in Drive_Alley_ATO_Tons:
            Drive_Alley_ATO_Tons.update({pageNo : Drive_Alley_ATO_Tons[pageNo] + TON}); print "...Drive_Alley_ATO_Tons"
        elif pageNo not in Drive_Alley_ATO_Tons:
            Drive_Alley_ATO_Tons.update({pageNo : value}); print "...Drive_Alley_ATO_Tons"


    print "Row Number... " + str(count)
    count = count + 1
del s_cursor

# Concrete Bus Pad
print "Updating Dictionaries for Bus Pad..."
arcpy.AddMessage("Processing Bus Pad data from project " + cceNo)
s_cursor = arcpy.SearchCursor(cBusPadCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
count = 0
for row in s_cursor:
    pageNo = row.getValue("PageNo")
    ## NEED TO FIND WHAT ARE REMOVE FEATURES ##

    length = row.getValue("MeasureLength")
    width = row.getValue("MeasureWidth")
    areaSF = row.getValue("MeasureLength") * row.getValue("MeasureWidth")
    areaSY = areaSF / 9.0
##    # Drive_Remove
##    if pageNo in Drive_Remove:
##        if remove == "":
##            Drive_Remove.update({pageNo : Drive_Remove[pageNo] + areaSF}); print "...Drive_Remove"
##    elif pageNo not in Drive_Remove:
##        if remove == "":
##            Drive_Remove.update({pageNo : areaSF}); print "...Drive_Remove"
    # c_BusPad
    if pageNo in c_BusPad:
        c_BusPad.update({pageNo : c_BusPad[pageNo] + areaSY}); print "...c_BusPad"
    elif pageNo not in c_BusPad:
        c_BusPad.update({pageNo : areaSY}); print "...c_BusPad"
    # c_BusPad_L
    if pageNo in c_BusPad_L:
        c_BusPad_L.update({pageNo : c_BusPad_L[pageNo] + length}); print "...c_BusPad_L"
    elif pageNo not in c_BusPad_L: #Corrected variable <SAH>
        c_BusPad_L.update({pageNo : length}); print "...c_BusPad_L"
    # c_BusPad_W
    if pageNo in c_BusPad_W:
        c_BusPad_W.update({pageNo : c_BusPad_W[pageNo] + width}); print "...c_BusPad_W"
    elif pageNo not in c_BusPad_W:
        c_BusPad_W.update({pageNo : width}); print "...c_BusPad_W"
    # PCC_Pave12in
    if pageNo in PCC_Pave12in:
        PCC_Pave12in.update({pageNo : PCC_Pave12in[pageNo] + areaSY}); print "...PCC_Pave12in"
    elif pageNo not in PCC_Pave12in:
        PCC_Pave12in.update({pageNo : areaSY}); print "...PCC_Pave12in"



    print "Row Number... " + str(count)
    count = count + 1
del s_cursor

# Concrete Pavement
print "Updating Dictionaries for Pavement..."
arcpy.AddMessage("Processing Pavement data from project " + cceNo)
s_cursor = arcpy.SearchCursor(c_PaveaveCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
count = 0
for row in s_cursor:
    pageNo = row.getValue("PageNo")
    ## NEED TO FIND WHAT ARE REMOVE FEATURES ##

    length = row.getValue("MeasureLength")
    width = row.getValue("MeasureWidth")
    areaSF = row.getValue("MeasureLength") * row.getValue("MeasureWidth")
    areaSY = areaSF / 9.0

    # c_Pave
    if pageNo in c_Pave:
        c_Pave.update({pageNo : c_Pave[pageNo] + areaSY}); print "...c_Pave"
    elif pageNo not in c_Pave:
        c_Pave.update({pageNo : areaSY}); print "...c_Pave"
    # c_Pave_L
    if pageNo in c_Pave_L:
        c_Pave_L.update({pageNo : c_Pave_L[pageNo] + length}); print "...c_Pave_L"
    elif pageNo not in c_Pave_L: #Corrected variable <SAH>
        c_Pave_L.update({pageNo : length}); print "...c_Pave_L"
    # c_Pave_W
    if pageNo in c_Pave_W:
        c_Pave_W.update({pageNo : c_Pave_W[pageNo] + width}); print "...c_Pave_W"
    elif pageNo not in c_Pave_W:
        c_Pave_W.update({pageNo : width}); print "...c_Pave_W"

    """ **UPDATES PER REVISIONS """
    # PCC_Pave10in
    if pageNo in PCC_Pave10in:
        PCC_Pave10in.update({pageNo : PCC_Pave10in[pageNo] + areaSY}); print "...PCC_Pave10in"
    elif pageNo not in PCC_Pave10in:
        PCC_Pave10in.update({pageNo : areaSY}); print "...PCC_Pave10in"


    print "Row Number... " + str(count)
    count = count + 1
del s_cursor

"""Added Driveway Remove Only Dictionary------SAH"""
# Driveway Remove
print "Updating Dictionaries for Driveway Remove..."
arcpy.AddMessage("Processing Driveway Remove data from project " + cceNo)
s_cursor = arcpy.SearchCursor(aDriveRemoveCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
count = 0
for row in s_cursor:
    pageNo = row.getValue("PageNo")
    areaSF = row.getValue("MeasureLength") * row.getValue("MeasureWidth")
    areaSY = areaSF/9.0
    if pageNo in Drive_Remove:
        Drive_Remove.update({pageNo : Drive_Remove[pageNo] + areaSY}); print "...Drive_Remove"
    elif pageNo not in Drive_Remove:
        Drive_Remove.update({pageNo : areaSY}); print "...Drive_Remove"

    print "Row Number... " + str(count)
    count = count + 1
del s_cursor

# Pavement Marking # MAKE NOTE
arcpy.AddMessage("Processing Pavement Markings data from project " + cceNo)
s_cursor = arcpy.SearchCursor(paveMarksCopy)
for row in s_cursor:
    markingType = row.getValue("MarkingType"); print markingType
    pageNo = row.getValue("PageNo")
    if markingType == "Skip Dash Centerline":
        if pageNo in SDC_Dict:
            SDC = row.getValue("MeasureLength"); print SDC
            SDC_Dict.update({pageNo : SDC_Dict[pageNo] + SDC})
        else:
            SDC = row.getValue("MeasureLength"); print SDC
            SDC_Dict.update({pageNo : SDC})
    if markingType == "Double Yellow Centerline":
        if pageNo in DYC_Dict:
            DYC = row.getValue("MeasureLength"); print DYC
            DYC_Dict.update({pageNo : DYC_Dict[pageNo] + DYC})
        else:
            DYC = row.getValue("MeasureLength"); print DYC
            DYC_Dict.update({pageNo : DYC})
    if markingType == "Stop Bar":
        if pageNo in SB_Dict:
            SB = row.getValue("MeasureLength"); print SB
            SB_Dict.update({pageNo : SB_Dict[pageNo] + SB})
        else:
            SB = row.getValue("MeasureLength"); print SB
            SB_Dict.update({pageNo : SB})
    if markingType == "International Crosswalk":
        if pageNo in IC_Dict:
            IC = row.getValue("MeasureLength"); print IC
            IC_Dict.update({pageNo : IC_Dict[pageNo] + IC})
        else:
            IC = row.getValue("MeasureLength"); print IC
            IC_Dict.update({pageNo : IC})
    if markingType == "Standard Crosswalk":
        if pageNo in SC_Dict:
            SC = row.getValue("MeasureLength"); print SC
            SC_Dict.update({pageNo : SC_Dict[pageNo] + SC})
        else:
            SC = row.getValue("MeasureLength"); print SC
            SC_Dict.update({pageNo : SC})

del s_cursor

arcpy.AddMessage("Processing Bike Rack data from project " + cceNo)
s_cursor = arcpy.SearchCursor(bikeRackCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:

    pageNo = row.getValue("PageNo")
    measureType = row.getValue("MeasureType")


    if "Shared" in measureType:
        bikeLocType = row.getValue("BikeRackLocationType")
        bikeLoc = row.getValue("BikeRackLocationType")
        if bikeLoc is None:
            bikeLoc = "";
        comString = "Bike Sharing Stations in " + bikeLocType + ": " + bikeLoc

        if len(BikeRack_Dict[pageNo]) == 0:
            BikeRack_Dict.update({pageNo : comString})
        else:
            BikeRack_Dict.update({pageNo : BikeRack_Dict[pageNo] + "; " + comString})


del s_cursor


print "Finished Calcs..."

print "... T3L"; print T3L
print "... T3rL"; print T3rL
print "... T3RL"; print T3RL
print "... T3RrL"; print T3RrL
print "... T3AL"; print T3AL
print "... T3ArL"; print T3ArL
print "... T3ARL"; print T3ARL
print "... T3ARrL"; print T3ARrL
print "... T3DWL"; print T3DWL
print "... T3DWAL"; print T3DWAL
print "... T4L"; print T4L
print "... T4rL"; print T4rL
print "... T4RL";print T4RL
print "... T4RrL"; print T4RrL
print "... PCC_5_SF"; print PCC_5_SF;
print "... PCC_5_RL"; print PCC_5_RL
print "... PCC_5_rmp_SF"; print PCC_5_rmp_SF
print "... PCC_5_rmp_RL"; print PCC_5_rmp_RL
print "... PCC_8_SF"; print PCC_8_SF
print "... PCC_8_RL"; print PCC_8_RL
print "... PCC_8_rmp_SF"; print PCC_8_rmp_SF
print "... PCC_8_rmp_RL"; print PCC_8_rmp_RL
print "... Side_rmp_Remove"; print Side_rmp_Remove
print "... PCC_Driveway"; print PCC_Driveway
print "... PCC_Alley"; print PCC_Alley
print "... Drive_Alley_ATO"; print Drive_Alley_ATO
print "... Drive_Remove"; print Drive_Remove
print "... c_BusPad"; print c_BusPad
print "... c_BusPad_L"; print c_BusPad_L
print "... c_BusPad_W"; print c_BusPad_W
print "... c_Pave"; print c_Pave
print "... PCC_Pave10in"; print PCC_Pave10in #"""UPDATED PER REVISION"""
print "... PCC_Pave12in"; print PCC_Pave12in #"""UPDATED PER REVISION"""
print "... Drive_Remove"; print Drive_Remove
print "... DC_Dict"; print SDC_Dict
print "... DYC_Dict"; print DYC_Dict
print "... SB_Dict"; print SB_Dict
print "... IC_Dict"; print IC_Dict
print "... SC_Dict"; print SC_Dict
print "... HES_PCC_Alley_8in"; print HES_PCC_Alley_8in
print "... HES_PCC_Driveway_8in"; print HES_PCC_Driveway_8in
print "... HES_PCC_Sidewalk_8in"; print HES_PCC_Sidewalk_8in
print "... Prot_Conc_Sealer"; print Prot_Conc_Sealer

# Start Search Cursor on Block Centerline to set Values and update Final Calcs
s_cursor = arcpy.SearchCursor(blockCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:

    pageNo = row.getValue("PageNo")

    TreesInPits_No = row.getValue("TreesInPits_No")
    TreesInPits_No_Dict.update({pageNo : TreesInPits_No})

    NumberInRamps5in = row.getValue("Number5inRamps") #"""UPDATED PER REVISION"""
    NumberInRamps5in_Dict.update({pageNo : NumberInRamps5in})

    NumberInRamps8in = row.getValue("Number8inRamps") #"""UPDATED PER REVISION"""
    NumberInRamps8in_Dict.update({pageNo : NumberInRamps8in})

    DrainUtil_Adjusted_No = row.getValue("DrainUtil_Adjusted_No")
    DrainUtil_Adjusted_No_Dict.update({pageNo : DrainUtil_Adjusted_No})

    WaterServ_Box_No = row.getValue("WaterServ_Box_No")
    WaterServ_Box_No_Dict.update({pageNo : WaterServ_Box_No})

    DrainStruct_Clean_No = row.getValue("DrainStruct_Clean_No")
    DrainStruct_Clean_No_Dict.update({pageNo : DrainStruct_Clean_No})

    Tree_Protect_No = row.getValue("Tree_Protect_No")
    Tree_Protect_No_Dict.update({pageNo : Tree_Protect_No})

    RootPruning_No = row.getValue("RootPruning_No")
    RootPruning_No_Dict.update({pageNo : RootPruning_No})

    AlleyApron_Recon_No = row.getValue("AlleyApron_Recon_No")
    AlleyApron_Recon_No_Dict.update({pageNo : AlleyApron_Recon_No})

    CornerHouse = row.getValue("strBlockCornerHouse")
    if CornerHouse == None:
           CornerHouse = ""
    CornerHouse_Dict.update({pageNo : CornerHouse}); print CornerHouse

#AutoComments: Get Field Values

    #Surface Conditon - AA, AS, RA, RS
    SurfaceCondition = checkStrForNull("SurfaceCondition")
    ShowSurfaceCondition = checkStrForNull("AutoComShow2_YN")
    #Alley Drainage Issues- AA
    DrainAlleyPotFloodYN = checkStrForNull("DrainAlleyPotFloodYN")
    ShowDrainAlleyPotFlood = checkStrForNull("AutoComShow12_YN")
    DrainAlleyCSRResurfPotFloodYN = checkStrForNull("DrainAlleyCSRResurfPotFloodYN")
    ShowDrainAlleyPotFlood = checkStrForNull("AutoComShow12_YN")
    #Special Locations - All
    SchoolYN = checkStrForNull("SchoolYN")
    ShowSchoolYN = checkStrForNull("AutoComShow3_YN")
    FireStationYN = checkStrForNull("FireStationYN")
    ShowFireStationYN = checkStrForNull("AutoComShow4_YN")
    PoliceStationYN = checkStrForNull("PoliceStationYN")
    ShowPoliceStationYN = checkStrForNull("AutoComShow5_YN")
    ChurchYN = checkStrForNull("ChurchYN")
    ShowChurchYN = checkStrForNull("AutoComShow6_YN")
    FuneralHomeYN = checkStrForNull("FuneralHomeYN")
    ShowFuneralHomeYN = checkStrForNull("AutoComShow7_YN")
    HospitalYN = checkStrForNull("HospitalYN")
    ShowHospitalYN = checkStrForNull("AutoComShow8_YN")
    OtherSpecialLocYN = checkStrForNull("OtherSpecialLocYN")
    ShowOtherSpecialLocYN = checkStrForNull("AutoComShow9_YN")
    #Street Drainage Issues - AS
    DrainStreetStandWaterYN = checkStrForNull("DrainStreetStandWaterYN")
    ShowDrainStreetStandWaterYN = checkStrForNull("AutoComShow10_YN")
    DrainStreetDebrisYN = checkStrForNull("DrainStreetDebrisYN")
    ShowDrainStreetDebrisYN = checkStrForNull("AutoComShow11_YN")
    #Other Pavement Markings
    OtherPaveMarksYN = checkStrForNull("OtherPaveMarksYN")
    ShowOtherPaveMarksYN = checkStrForNull("AutoComShow13_YN")
    #Special Conditions
    LoopDetectorsYN = checkStrForNull("LoopDetectorsYN")
    ShowLoopDetectorsYN = checkStrForNull("AutoComShow14_YN")
    BusStopYN = checkStrForNull("BusStopYN")
    ShowBusStopYN = checkStrForNull("AutoComShow15_YN")
    ParkPayBoxesYN = checkStrForNull("ParkPayBoxesYN")
    ShowParkPayBoxesYN = checkStrForNull("AutoComShow16_YN")
    HeightRestrictYN = checkStrForNull("HeightRestrictYN")
    ShowHeightRestrictYN = checkStrForNull("AutoComShow17_YN")
    ViaductYN = checkStrForNull("ViaductYN")
    ShowViaductYN = checkStrForNull("AutoComShow18_YN")
    WPABlockYN = checkStrForNull("WPABlockYN")
    ShowWPABlockYN = checkStrForNull("AutoComShow19_YN")
    CurbGutterPoorYN = checkStrForNull("CurbGutterPoorYN")
    ShowCurbGutterPoorYN = checkStrForNull("AutoComShow20_YN")
    GutterPanOverlaidYN = checkStrForNull("GutterPanOverlaidYN")
    ShowGutterPanOverlaidYN = checkStrForNull("AutoComShow21_YN")
    StructureRepairYN = checkStrForNull("StructureRepairYN")
    ShowStructureRepairYN = checkStrForNull("AutoComShow22_YN")
    CuldeSacYN = checkStrForNull("CulDeSacYN")
    ShowCuldeSacYN = checkStrForNull("AutoComShow23_YN")
    DeadEndYN = checkStrForNull("DeadEndYN")
    ShowDeadEndYN = checkStrForNull("AutoComShow24_YN")
    GuardrailYN = checkStrForNull("GuardrailYN")
    ShowGuardrailYN = checkStrForNull("AutoComShow25_YN")
    DecorFenceYN = checkStrForNull("DecorFenceYN")
    ShowDecorFenceYN = checkStrForNull("AutoComShow26_YN")
    #Survey Draw Comments
    SurveyDrawComments = checkStrForNull("SurveyDrawComments")
    ShowSurveyDrawComments = checkStrForNull("AutoComShow28_YN")

    ShowBikeRack = checkStrForNull("AutoComShow27_YN")
    ShowRampStatus = checkStrForNull("AutoComShow1_YN")

    #Apply Comments to Dictionary
    if SchoolYN == "Yes" and ShowSchoolYN != "No":
        updateAutoCommentsDict("School", "SchoolNotes", True)
    if FireStationYN == "Yes" and ShowFireStationYN != "No":
        updateAutoCommentsDict("Fire Station", "FireStationNotes", True)
    if PoliceStationYN == "Yes" and ShowPoliceStationYN != "No":
        updateAutoCommentsDict("Police Station", "PoliceStationNotes", True)
    if ChurchYN == "Yes" and ShowChurchYN != "No":
        updateAutoCommentsDict("Church", "ChurchNotes", True)
    if FuneralHomeYN == "Yes" and ShowFuneralHomeYN != "No":
        updateAutoCommentsDict("Funeral Home", "FuneralHomeNotes", True)
    if HospitalYN == "Yes" and ShowHospitalYN != "No":
        updateAutoCommentsDict("Hosptital", "HosptitalNotes", True)
    if OtherSpecialLocYN == "Yes" and ShowOtherSpecialLocYN != "No":
        updateAutoCommentsDict("Other Special Location", "OtherSpecialLocNotes", True)
    if OtherPaveMarksYN == "Yes" and ShowOtherPaveMarksYN != "No" and (projectType == "AA" or projectType == "AR" or projectType == "AS" or projectType == "CC" or projectType == "CO" or projectType == "CS"):
        updateAutoCommentsDict("Pavement Markings not shown", "OtherPaveMarksNotes", True)
    if LoopDetectorsYN == "Yes" and ShowLoopDetectorsYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Loop Detectors Present", "LoopDetectorNotes", True)
    if BusStopYN == "Yes" and ShowBusStopYN != "No":
        updateAutoCommentsDict("Bus Stop", "BusStopLocation", True)
    if ParkPayBoxesYN == "Yes" and ShowParkPayBoxesYN != "No":
        updateAutoCommentsDict("Parking Pay Boxes Present", "ParkPayBoxesNotes", True)
    if HeightRestrictYN == "Yes" and ShowHeightRestrictYN != "No" and (projectType == "AA" or projectType == "AS"):
        updateAutoCommentsDict("Height Restriction", "None", False)
    if ViaductYN == "Yes" and ShowViaductYN != "No" and (projectType == "AA" or projectType == "AS"):
        updateAutoCommentsDict("Viaduct", "ViaductNotes", True)
    if WPABlockYN == "Yes" and ShowWPABlockYN != "No" and projectType == "AS":
        updateAutoCommentsDict("WPA Block", "None", False)
    if CurbGutterPoorYN == "Yes" and ShowCurbGutterPoorYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Curb and Gutter in poor shape - Suggest Replacement", "None", False)
    if GutterPanOverlaidYN == "Yes" and ShowGutterPanOverlaidYN != "No":
        updateAutoCommentsDict("Gutter Pan Overlaid", "None", False)
    if StructureRepairYN == "Yes" and ShowStructureRepairYN != "No" and (projectType == "AA" or projectType == "AS"):
        updateAutoCommentsDict("Structure Repair", "StructureRepairNotes", True)
    if CuldeSacYN == "Yes" and ShowCuldeSacYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Cul-de-Sac Present", "None", False)
    if DeadEndYN == "Yes" and ShowDeadEndYN != "No" and projectType == "AS":
        updateAutoCommentsDict("Dead End Street", "None", False)
    if GuardrailYN == "Yes" and ShowGuardrailYN != "No":
        updateAutoCommentsDict("Guardrail", "GuardrailNotes", True)
    if DecorFenceYN == "Yes" and ShowDecorFenceYN != "No" and (projectType == "AR" or projectType == "CC" or projectType == "CO" or projectType == "CS" or projectType == "CA" or projectType == "RS"):
        updateAutoCommentsDict("Existing Decorative Fence", "DecorFenceNotes", True)

    if len(BikeRack_Dict[pageNo]) > 0 and ShowBikeRack != "No":
        updateAutoCommentsDict(BikeRack_Dict[pageNo], "None", False)

    if len(RampStatus_Dict[pageNo]) > 0 and ShowRampStatus != "No":
        updateAutoCommentsDict(RampStatus_Dict[pageNo], "None", False)

    #Survey Comments
    if len(SurveyDrawComments) > 0 and ShowSurveyDrawComments != "No":
        updateAutoCommentsDict("General Comments", "SurveyDrawComments", True)

    #Apply Overriding Comments
    if DrainAlleyPotFloodYN == "Yes" and ShowDrainAlleyPotFlood == "Yes" and projectType == "AA":
        AutoComments_Dict.update({pageNo : "Drop - Potential for flooding into private property. Recommend Green Alley Solution."})
    if DrainAlleyCSRResurfPotFloodYN == "Yes" and ShowDrainAlleyPotFlood and projectType == "AA":
        AutoComments_Dict.update({pageNo : "Drop - Potential for flooding into private property. Recommend Green Alley Solution."})
    if "Drop" in SurfaceCondition and ShowSurfaceCondition == "Yes" and (projectType == "AA" or projectType == "AS"):
        AutoComments_Dict.update({pageNo : "Drop - Good Condition"})
    if "Drop" in SurfaceCondition and ShowSurfaceCondition == "Yes" and (projectType == "RA" or projectType == "RS"):
        AutoComments_Dict.update({pageNo : "Drop - Resurfacing Project Dropped"})

del s_cursor

WardID = ""
MenuID = ""
strMenu = ""

arcpy.AddMessage("Processing ProjectCenterline data from project " + cceNo)
s_cursor = arcpy.SearchCursor(projectCopy, "\"strCCEProjectNumber\"" + " = '" + cceNo + "'")
for row in s_cursor:


    WardID = row.getValue("lngWardID")
    MenuID = row.getValue("lngMenuID")

    s_cursor2 = arcpy.SearchCursor(tblMenu, "\"LNGMENUID\"" + " = '" + str(MenuID) + "'")

    for s_row in s_cursor2:
        strMenu = s_row.getValue("strMenu")

del s_cursor

# Create Final Calc Dictionaries # MAY NOT NEED

##edit = arcpy.da.Editor(r"\\lex-srv02\gis\projects\IL\Chicago\v4\Spatial\gdb\Lex_CDOT_Menu_v4_Testing_Target.sde")
##edit.startEditing(False, True)
##edit.startOperation()

cceNoCalcs = cceNo

#Find corresponding combo number
if "-ASlRS-" in cceNoCalcs:
    cceNoCalcs = cceNo.replace("-ASlRS-", "-RS-")
if "-AAlRA-" in cceNoCalcs:
    cceNoCalcs = cceNo.replace("-AAlRA-", "-RA-")

# Final Calcs
print "Updating Final Calcs..."
arcpy.AddMessage("Updating Final Calculations " + cceNo)
u_cursor = arcpy.UpdateCursor(FinalCalcs, "\"strCCEProjectNumber\"" + " = '" + cceNoCalcs + "'")
for row in u_cursor:
    # Update Final Calc values
    pageNo = row.getValue("PageNo"); print pageNo

    #Find corresponding combo number in Dictionaries
    if "-RS-" in pageNo:
        pageNo = pageNo.replace("-RS-", "-ASlRS-")
    if "-RA-" in pageNo:
        pageNo = pageNo.replace("-RA-", "-AAlRA-")

    # CurbGutter T3 Length Sum
    # * ADDED T3DWL AND T3DWAL PER REVISIONS
    RSCurbGutT3LF = math.ceil(T3L[pageNo]) + math.ceil(T3AL[pageNo]) + math.ceil(T3DWL[pageNo]) + math.ceil(T3DWAL[pageNo])
    row.setValue("RSCurbGutT3LF", RSCurbGutT3LF); print RSCurbGutT3LF; print "...RSCurbGutT3LF"
    # CurbGutter T3R Length Sum
    RSCurbGutT3LFR = math.ceil(T3RL[pageNo]) + math.ceil(T3ARL[pageNo])
    row.setValue("RSCurbGutRampT3LF", RSCurbGutT3LFR); print RSCurbGutT3LFR; print "...RSCurbGutRampT3LF"
    # High Early Strength PCC Combination Curb and Gutter, Type B-V.12 """UPDATED PER REVISION"""
    CICCurbGutT3_CoreLFT = math.ceil(T3DWL[pageNo]) + math.ceil(T3DWAL[pageNo])
    row.setValue("CICCurbGutT3_CoreLFT", CICCurbGutT3_CoreLFT); print CICCurbGutT3_CoreLFT; print "...CICCurbGutT3_CoreLFT"
    # Vertical Curb T4 Length Sum """UPDATED PER REVISION"""
    CICVertCurbT4_CoreLFT = math.ceil(T4L[pageNo])
    RSVertCurbGutT4 = math.ceil(T4L[pageNo])
    row.setValue("CICVertCurbT4_CoreLFT", CICVertCurbT4_CoreLFT); print CICVertCurbT4_CoreLFT; print "...CICVertCurbT4_CoreLFT"
    row.setValue("RSVertCurbGutT4", RSVertCurbGutT4)
    # Vertical Curb T4R Length Sum """UPDATED PER REVISION"""
    CICVertCurbT4_ADA_FT = math.ceil(T4RL[pageNo])
    RSVertCurbRampT4 = math.ceil(T4RL[pageNo])
    row.setValue("CICVertCurbT4_ADA_FT", CICVertCurbT4_ADA_FT); print CICVertCurbT4_ADA_FT; print "...CICVertCurbT4_ADA_FT"
    row.setValue("RSVertCurbRampT4", RSVertCurbRampT4)
    # 5" PCC Sidewalk SF
    RS5inPCCSidewalkSF = math.ceil(PCC_5_SF[pageNo])
    row.setValue("RS5inPCCSidewalkSF", RS5inPCCSidewalkSF); print RS5inPCCSidewalkSF; print "...RS5inPCCSidewalkSF"
    # 5" PCC Sidewalk Ramp SF
    RS5inPCCSidewalkRampSF = math.ceil(PCC_5_rmp_SF[pageNo])
    row.setValue("RS5inPCCSidewalkRampSF", RS5inPCCSidewalkRampSF); print RS5inPCCSidewalkRampSF; print "...RS5inPCCSidewalkRampSF"
    # 8" PCC Sidewalk SF
    RS8inPCCSidewalkSF = math.ceil(PCC_8_SF[pageNo])
    row.setValue("RS8inPCCSidewalkSF", RS8inPCCSidewalkSF); print RS8inPCCSidewalkSF; print "...RS8inPCCSidewalkSF"
    # 8" PCC Sidewalk Ramp SF
    RS8inPCCSidewalkRampSF = math.ceil(PCC_8_rmp_SF[pageNo])
    row.setValue("RS8inPCCSidewalkRampSF", RS8inPCCSidewalkRampSF); print RS8inPCCSidewalkRampSF; print "...RS8inPCCSidewalkRampSF"
    # 7" PCC Base Course SY (ADA only)
    RS7ftPCCBaseCourseSY = math.ceil((RSCurbGutT3LFR * 2.0) / 9.0)
    row.setValue("RS7ftPCCBaseCourseSY", RS7ftPCCBaseCourseSY); print RS7ftPCCBaseCourseSY; print "...RS7ftPCCBaseCourseSY"
    # ATO 2" TON
    #RS7ftPCCATOTons = math.ceil((((RSCurbGutT3LF + RSCurbGutT3LFR) * 2.0) / 9.0) * 0.112)
    RS7ftPCCATOTons = math.ceil(((((RSCurbGutT3LF + RSCurbGutT3LFR) * 2.0) / 9.0) * 0.112) + ((((c_BusPad_L[pageNo] + (2.0 * c_BusPad_W[pageNo])) * 2.0) / 9.0) * 0.112))
    row.setValue("RS7ftPCCATOTons", RS7ftPCCATOTons); print RS7ftPCCATOTons; print "...RS7ftPCCATOTons"
    # Sawcut Length
    RSSawCutLF = math.ceil((RSCurbGutT3LF + RSCurbGutT3LFR) + ((2.0 *c_BusPad_L[pageNo]) + (2.0 * c_BusPad_W[pageNo])))
    row.setValue("RSSawCutLF", RSSawCutLF); print "...RSSawCutLF"; print RSSawCutLF
    # D/A Concrete SY
    """This needs revising per Kristen - 12/20/13"""
    RSDrivewayAlleyConcreteSY = math.ceil((PCC_Driveway[pageNo]) + (PCC_Alley[pageNo]))
    #CICDrivewayAlleyConcreteSY = math.ceil(PCC_Driveway[pageNo]) + math.ceil(PCC_Alley[pageNo]) ##May not be needed - SAH
    row.setValue("RSDrivewayAlleyConcreteSY", RSDrivewayAlleyConcreteSY); print RSDrivewayAlleyConcreteSY; print "...RSDrivewayAlleyConcreteSY"
    #row.setValue("CICDrivewayAlleyConcreteSY", CICDrivewayAlleyConcreteSY); print CICDrivewayAlleyConcreteSY; print "...CICDrivewayAlleyConcreteSY" ##May not be needed - SAH
    # D/A Asphalt TON
    RSDrivewayAlleyATOTons = math.ceil(Drive_Alley_ATO_Tons[pageNo])
    row.setValue("RSDrivewayAlleyATOTons", RSDrivewayAlleyATOTons); print RSDrivewayAlleyATOTons; print "...RSDrivewayAlleyATOTons"
    # Ramp Numbers
    row.setValue("RS5inPCCSidewalkRampNum", NumberInRamps5in_Dict[pageNo])
    row.setValue("RS8inPCCSidewalkRampNum", NumberInRamps8in_Dict[pageNo])


    # Concrete Bus Pad SY
    c_BusPadSY = math.ceil(c_BusPad[pageNo])

    # Concrete Pavement SY
    cpSY = math.ceil(c_Pave[pageNo])

    # CICProtConcSealer_CoreLFT
    CICProtConcSealer_CoreLFT = math.ceil((c_BusPad[pageNo] + c_Pave[pageNo]))
    row.setValue("CICProtConcSealer_CoreLFT", CICProtConcSealer_CoreLFT); print CICProtConcSealer_CoreLFT; print "...CICProtConcSealer_CoreLFT"

    """Added the calcs for hydroseed and topsoil---SAH"""
    # Hydroseed SY
    RSHydroseedSY = math.ceil(((math.ceil(PCC_5_RL[pageNo]) + math.ceil(PCC_5_rmp_RL[pageNo]) + math.ceil(PCC_8_RL[pageNo]) + math.ceil(PCC_8_rmp_RL[pageNo])) * 0.056) + ((math.ceil(T3rL[pageNo]) + math.ceil(T3RrL[pageNo]) + math.ceil(T3ArL[pageNo]) + math.ceil(T3ARrL[pageNo]) + math.ceil(T4rL[pageNo]) + math.ceil(T4RrL[pageNo])) * 0.167)) +  math.ceil((math.ceil(Drive_Remove[pageNo])) + math.ceil(Side_rmp_Remove[pageNo]))
    row.setValue("RSHydroseedSY", RSHydroseedSY)
    CICHydraulicSeed_CoreSY = RSHydroseedSY
    row.setValue("CICHydraulicSeed_CoreSY", CICHydraulicSeed_CoreSY)

    # Topsoil CY
    RSTopsoilCY = math.ceil(((math.ceil(PCC_5_RL[pageNo]) + math.ceil(PCC_5_rmp_RL[pageNo]) + math.ceil(PCC_8_RL[pageNo]) + math.ceil(PCC_8_rmp_RL[pageNo])) * 0.01) + ((math.ceil(T3rL[pageNo]) + math.ceil(T3RrL[pageNo]) + math.ceil(T3ArL[pageNo]) + math.ceil(T3ARrL[pageNo]) + math.ceil(T4rL[pageNo]) + math.ceil(T4RrL[pageNo])) * 0.111)) +  math.ceil(((math.ceil(Drive_Remove[pageNo])) + math.ceil(Side_rmp_Remove[pageNo])) * 0.25)
    row.setValue("RSTopsoilCY", RSTopsoilCY)
    CICPulvTopsoilMix_CoreCY = RSTopsoilCY
    row.setValue("CICPulvTopsoilMix_CoreCY", CICPulvTopsoilMix_CoreCY)

    # Drill and Grout
      # PCC Base - CORE # **UPDATES PER REVISIONS
##    RCMAdgtbCORE7 = math.ceil(T3L[pageNo] / 1.5) # 7" PCC Base
##    RCMAdgtbCORE9 = math.ceil(T3AL[pageNo] / 1.5) # 9" PCC Base
    """T3 curb removed from CORE calculation for Drill and Grout - TBU-03/12/2014"""
##    CIC_T3_DGDTB_CORE = math.ceil(RSCurbGutT3LF / 1.5) # T3 Curb and Gutter PCC Base
    CIC_dgtbCOREbp = math.ceil((((c_BusPad_L[pageNo]) * 2.0) + ((c_BusPad_W[pageNo]) * 2.0)) / 1.5) # Bus Pad
    CIC_dgtbCOREcul = math.ceil(((c_Pave_L[pageNo]) + (math.ceil(c_Pave_W[pageNo]) * 2.0)) / 1.5) # Diag Parking or Cul-de-sac # **UPDATES PER REVISIONS
    CICDrillGroutTieBars_CoreEA = math.ceil(CIC_dgtbCOREbp) + math.ceil(CIC_dgtbCOREcul) ## + math.ceil(CIC_T3_DGDTB_CORE)
    row.setValue("CICDrillGroutTieBars_CoreEA", CICDrillGroutTieBars_CoreEA) # **UPDATES PER REVISIONS
    print CICDrillGroutTieBars_CoreEA; print "...CICDrillGroutTieBars_CoreEA"
      # PCC Base - ADA # **UPDATES PER REVISIONS
    CIC_T3RL_DGTB_ADA = math.ceil(T3RL[pageNo])
    CIC_T3AR_DGTB_ADA = math.ceil(T3ARL[pageNo])
    CICDrillGroutTieBars_ADA_EA = math.ceil((CIC_T3RL_DGTB_ADA + CIC_T3AR_DGTB_ADA) / 1.5)
    row.setValue("CICDrillGroutTieBars_ADA_EA", CICDrillGroutTieBars_ADA_EA)
    print CICDrillGroutTieBars_ADA_EA; print "...CICDrillGroutTieBars_ADA_EA"

#Removed, calced above <SAH>
##    # Pulverized Topsoil Mix """UPDATED PER REVISION"""
##    swLength = math.ceil(PCC_5_RL[pageNo]) + math.ceil(PCC_5_rmp_RL[pageNo]) + math.ceil(PCC_8_RL[pageNo]) + math.ceil(PCC_8_rmp_RL[pageNo])
##    curbLength = math.ceil(T3rL[pageNo]) + math.ceil(T3RrL[pageNo]) + math.ceil(T3ArL[pageNo]) + math.ceil(T3ARrL[pageNo]) + math.ceil(T4rL[pageNo]) + math.ceil(T4RrL[pageNo])
##    pTopmix = (swLength * 0.01) + (curbLength * 0.111)
##    sDrive_RemoveemoveAreaTop = math.ceil((Side_rmp_Remove[pageNo]) / ((9.0 + math.ceil(Drive_Remove[pageNo])) * 0.25)) # Sidewalk/Driveway Remove
##    CICPulvTopsoilMix_CoreCY = math.ceil(pTopmix + sDrive_RemoveemoveAreaTop)
##    row.setValue("CICPulvTopsoilMix_CoreCY", CICPulvTopsoilMix_CoreCY)
##    print CICPulvTopsoilMix_CoreCY; print "...CICPulvTopsoilMix_CoreCY"
##
##    # Hydraulic Seeding """UPDATED PER REVISION"""
##    hSeed = (swLength * 0.056) + (curbLength * 0.167)
##    sDrive_RemoveemoveAreaSeed = math.ceil((Side_rmp_Remove[pageNo]) / (9.0 + (Drive_Remove[pageNo]))) # Sidewalk/Driveway Remove
##    sDrive_RemoveemoveTopmix = math.ceil(pTopmix + sDrive_RemoveemoveAreaTop)
##    CICHydraulicSeed_CoreSY = math.ceil(hSeed + sDrive_RemoveemoveAreaSeed)
##    row.setValue("CICHydraulicSeed_CoreSY", CICHydraulicSeed_CoreSY)
##    print CICHydraulicSeed_CoreSY; print "...CICHydraulicSeed_CoreSY"

    # SubBase Granular Material, Type B - CORE + Concrete Bus Pads """UPDATED PER REVISION"""
##    SBGMcoreBP = (((math.ceil(c_BusPad_L[pageNo]) + 2) * (math.ceil(c_BusPad_W[pageNo]))) * 4) / 9
    """SubBase Granular Material T3RCurb Area calculation adjusted per changes - TBU-03/12/2014"""
    SBGMcoreT3sy = ((math.ceil(T3L[pageNo]) + math.ceil(T3AL[pageNo])) * 4.58) / 9.0
    CICSubGranMatTypeB_CoreCY = math.ceil(((math.ceil(PCC_Driveway[pageNo]) * 0.5) / 3.0) + ((math.ceil(PCC_Alley[pageNo]) * 0.5) / 3.0) + ((SBGMcoreT3sy * 0.25) / 3.0) + ((math.ceil(c_BusPadSY) * 0.5) / 3.0) + math.ceil((cpSY * 0.5) / 3.0) + ((((math.ceil(T4L[pageNo]) * 1.5) / 9.0) * 0.5) / 3.0) + (((((math.ceil(T3DWL[pageNo]) + math.ceil(T3DWAL[pageNo])) * 1.58) / 9.0) * 0.25) / 3.0)) #"""UPDATED PER REVISION 2/3/13"""
    row.setValue("CICSubGranMatTypeB_CoreCY", CICSubGranMatTypeB_CoreCY)
    print CICSubGranMatTypeB_CoreCY; print "...CICSubGranMatTypeB_CoreCY"

    # SubBase Granular Material, Type B - ADA """UPDATED PER REVISION"""
    CICSubGranMatTypeB_ADA_CY = math.ceil(math.ceil((((((T3RL[pageNo]) + (T3ARL[pageNo])) * 2.58) / 9.0) * 0.25) / 3.0) + math.ceil(((((T4RL[pageNo]) * 1.5) / 9.0) * 0.5) / 3.0)) #"""UPDATED PER REVISION 2/3/13"""
    row.setValue("CICSubGranMatTypeB_ADA_CY", CICSubGranMatTypeB_ADA_CY)
    print CICSubGranMatTypeB_ADA_CY; print "...CICSubGranMatTypeB_ADA_CY"

    # Pavement Markings (#117,#118,#121,#122) """UPDATED PER REVISION"""
    CICThermoPave4in_CoreLFT = math.ceil(((SDC_Dict[pageNo])/4.0) + (DYC_Dict[pageNo])*2.0)
    row.setValue("CICThermoPave4in_CoreLFT", CICThermoPave4in_CoreLFT); print CICThermoPave4in_CoreLFT; print "...CICThermoPave4in_CoreLFT"

    CICThermoPave6in_CoreLFT = math.ceil((SC_Dict[pageNo]) * 2.0)
    row.setValue("CICThermoPave6in_CoreLFT", CICThermoPave6in_CoreLFT); print CICThermoPave6in_CoreLFT; print "...CICThermoPave6in_CoreLFT"

    CICThermoPave24in_CoreLFT = math.ceil(((IC_Dict[pageNo]) * 6.0) / 4.0) + (SB_Dict[pageNo])
    row.setValue("CICThermoPave24in_CoreLFT", CICThermoPave24in_CoreLFT); print CICThermoPave24in_CoreLFT; print "...CICThermoPave24in_CoreLFT"

    CICPaveMarkRemove_CoreSF = math.ceil((((CICThermoPave4in_CoreLFT * 4.0) + (CICThermoPave6in_CoreLFT * 6.0) + (CICThermoPave24in_CoreLFT * 24.0)) / 12.0))
    row.setValue("CICPaveMarkRemove_CoreSF", CICPaveMarkRemove_CoreSF); print CICPaveMarkRemove_CoreSF; print "...CICPaveMarkRemove_CoreSF"

    """ **UPDATES PER REVISIONS """
    """T3RL no longer included for Surface Removal ADAN30 - TBU-03/17/2014"""
    # HMA Surface Removal Variable Depth N30 - CORE and ADA """UPDATED PER REVISION"""
    HMASurfRem_Core_N30 = math.ceil((((T3L[pageNo])* 2.0)/9.0) + (((T3DWL[pageNo]) * 2.0) / 9.0) + math.ceil(Drive_Alley_ATO[pageNo]))
    CICHMAN30HM_CoreTON = math.ceil((((HMASurfRem_Core_N30) * 112.0) * 3.0) / 2000.0)
    HMASurfRem_ADA_N30 = math.ceil(((T3RL[pageNo]) * 2.0) / 9.0)
    CICHMAN30HM_ADATON = math.ceil((((HMASurfRem_ADA_N30) * 112.0) * 3.0) / 2000.0)

##    if  HMASurRem_Eval_N30 < 15.0:
##        row.setValue("CICHMAN30Type1_CoreSY", HMASurfRem_Core_N30); print HMASurfRem_Core_N30; print "...CICHMAN30Type1_CoreSY" # TYPE 1 - CORE
##        row.setValue("CICHMAN30Type1_ADA_SY", HMASurfRem_ADA_N30); print HMASurfRem_ADA_N30; print "...CICHMAN30Type1_ADA_SY" # TYPE 1 - ADA
##        row.setValue("CICHMAN30Type2_CoreSY", 0.0); print 0.0; print "...CICHMAN30Type2_CoreSY" # TYPE 2 - CORE
##        row.setValue("CICHMAN30Type2_ADA_SY", 0.0); print 0.0; print "...CICHMAN30Type2_ADA_SY" # TYPE 2 - ADA
##    else:
##        row.setValue("CICHMAN30Type1_CoreSY", 0.0); print 0.0; print "...CICHMAN30Type1_CoreSY" # TYPE 1 - CORE
##        row.setValue("CICHMAN30Type1_ADA_SY", 0.0); print 0.0; print "...CICHMAN30Type1_ADA_SY" # TYPE 1 - ADA
##        row.setValue("CICHMAN30Type2_CoreSY", HMASurfRem_Core_N30); print HMASurfRem_Core_N30; print "...CICHMAN30Type2_CoreSY" # TYPE 2 - CORE
##        row.setValue("CICHMAN30Type2_ADA_SY", HMASurfRem_ADA_N30); print HMASurfRem_ADA_N30; print "...CICHMAN30Type2_ADA_SY" # TYPE 2 - ADA

    # HMA Surface Removal Variable Depth N70 - CORE and ADA """UPDATED PER REVISION"""
    """T3ARL no longer included for Surface Removal ADAN70 - TBU-03/17/2014"""
    HMASurfRem_CORE_N70 = math.ceil((((T3AL[pageNo]) * 2.0) / 9.0) + (((T3DWAL[pageNo]) * 2.0) /9.0) + (((c_BusPad_L[pageNo]) + ((c_BusPad_W[pageNo]) * 2.0)) * 2.0) / 9.0)
    CICHMAN70HM_CoreTON = math.ceil((((HMASurfRem_CORE_N70) * 112.0) * 3.0) / 2000.0)
    HMASurfRem_ADA_N70 = math.ceil(((T3ARL[pageNo]) * 2.0) / 9.0)
    CICHMAN70HM_ADATON = math.ceil((((HMASurfRem_ADA_N70) * 112.0) * 3.0) / 2000.0)

    # HMA Surface Removal Course, Patch, Hand Method
    """No longer measure for CICHMASurfaceRemVD_ADASY - Calcs changed - TBU-03/17/2014"""
    CICHMASurfRemVD_CoreSY = HMASurfRem_CORE_N70 + HMASurfRem_Core_N30
##    CICHMASurfRemVD_ADASY =  HMASurfRem_ADA_N70 + HMASurfRem_ADA_N30
    CICHMASurfRemVD_ADASY = 0

    row.setValue("CICHMASurfRemVD_CoreSY", CICHMASurfRemVD_CoreSY); print CICHMASurfRemVD_CoreSY; print "...CICHMASurfRemVD_CoreSY"
    row.setValue("CICHMASurfRemVD_ADASY", CICHMASurfRemVD_ADASY); print CICHMASurfRemVD_ADASY; print "...CICHMASurfRemVD_ADASY"
    row.setValue("CICHMAN30HM_CoreTON", CICHMAN30HM_CoreTON); print CICHMAN30HM_CoreTON; print "...CICHMAN30HM_CoreTON"
    row.setValue("CICHMAN70HM_CoreTON", CICHMAN70HM_CoreTON); print CICHMAN70HM_CoreTON; print "...CICHMAN70HM_CoreTON"
    row.setValue("CICHMAN30HM_ADATON", CICHMAN30HM_ADATON); print CICHMAN30HM_ADATON; print "...CICHMAN30HM_ADATON"
    row.setValue("CICHMAN70HM_ADATON", CICHMAN70HM_ADATON); print CICHMAN70HM_ADATON; print "...CICHMAN70HM_ADATON"
##    if HMASurfRem_Eval_n70 < 15.0:
##        row.setValue("CICHMAN70Type1_CoreSY", HMASurfRem_CORE_N70) # TYPE 1 - CORE
##        print HMASurfRem_CORE_N70; print "...CICHMAN70Type1_CoreSY"
##        row.setValue("CICHMAN70Type1_ADA_SY", HMASurfRem_ADA_N70) # TYPE 1 - ADA
##        print HMASurfRem_ADA_N70; print "...CICHMAN70Type1_ADA_SY"
##        row.setValue("CICHMAN70Type2_CoreSY", 0.0) # TYPE 2 - CORE
##        print 0.0; print "...CICHMAN70Type2_CoreSY"
##        row.setValue("CICHMAN70Type2_ADA_SY", 0.0) # TYPE 2 - ADA
##        print 0.0; print "...CICHMAN70Type2_ADA_SY"

##    else:
##        row.setValue("CICHMAN70Type1_CoreSY", 0.0) # TYPE 1 - CORE
##        print 0.0; print "...CICHMAN70Type1_CoreSY"
##        row.setValue("CICHMAN70Type1_ADA_SY", 0.0) # TYPE 1 - ADA
##        print 0.0; print "...CICHMAN70Type1_ADA_SY"
##        row.setValue("CICHMAN70Type2_CoreSY", HMASurfRem_CORE_N70) # TYPE 2 - CORE
##        print HMASurfRem_CORE_N70; print "...CICHMAN70Type2_CoreSY"
##        row.setValue("CICHMAN70Type2_ADA_SY", HMASurfRem_ADA_N70) # TYPE 2 - ADA
##        print HMASurfRem_ADA_N70; print "...CICHMAN70Type2_ADA_SY"
    """**"""


    # Bituminous Materials Prime Coat - CORE """UPDATED PER REVISION"""
    CICBitumMatPrimeCoat_CoreGAL = math.ceil((HMASurfRem_Core_N30 + HMASurfRem_CORE_N70) * 0.1)
    row.setValue("CICBitumMatPrimeCoat_CoreGAL", CICBitumMatPrimeCoat_CoreGAL)
    print CICBitumMatPrimeCoat_CoreGAL; print "...CICBitumMatPrimeCoat_CoreGAL"

    # Bituminous Materials Prime Coat - ADA """UPDATED PER REVISION"""
    CICBitumMatPrimeCoat_ADA_GAL = math.ceil((HMASurfRem_ADA_N30 + HMASurfRem_ADA_N70) * 0.1)
    row.setValue("CICBitumMatPrimeCoat_ADA_GAL", CICBitumMatPrimeCoat_ADA_GAL)
    print CICBitumMatPrimeCoat_ADA_GAL; print "...CICBitumMatPrimeCoat_ADA_GAL"


##    # Alley Pavement Removal - CORE
##    RCMAAlleyPaveRemove_CoreSY = math.ceil(PCC_Alley[pageNo]) + math.ceil(Drive_Alley_ATO[pageNo])
##    row.setValue("RCMAAlleyPaveRemove_CoreSY", RCMAAlleyPaveRemove_CoreSY)
    # Driveway and Alley Return Pavement Removal - CORE """UPDATED PER REVISION"""
    CICDrvAlleyPaveRemove_CoreSY = math.ceil(PCC_Driveway[pageNo]) + math.ceil(Drive_Remove[pageNo]) + math.ceil(PCC_Alley[pageNo]) #Fixed varable name <SAH>
    row.setValue("CICDrvAlleyPaveRemove_CoreSY", CICDrvAlleyPaveRemove_CoreSY); print CICDrvAlleyPaveRemove_CoreSY; print "... CICDrvAlleyPaveRemove_CoreSY"

    # Sidewalk Removal - CORE """UPDATED PER REVISION"""
    CICSidewalkRemove_CoreSF = math.ceil(PCC_5_SF[pageNo]) + math.ceil(PCC_8_SF[pageNo]) + math.ceil(Side_rmp_Remove[pageNo] * 9.0)
    row.setValue("CICSidewalkRemove_CoreSF", CICSidewalkRemove_CoreSF); print CICSidewalkRemove_CoreSF; print "... CICSidewalkRemove_CoreSF"
    # Sidewalk Removal - ADA """UPDATED PER REVISION"""
    CICSidewalkRemove_ADA_SF = math.ceil(PCC_5_rmp_SF[pageNo]) + math.ceil(PCC_8_rmp_SF[pageNo])
    row.setValue("CICSidewalkRemove_ADA_SF", CICSidewalkRemove_ADA_SF); print CICSidewalkRemove_ADA_SF; print "... CICSidewalkRemove_ADA_SF"

    # Pavement Removal - CORE """UPDATED PER REVISION"""
    CICPaveRemove_CoreSY = math.ceil(c_BusPad[pageNo]) #Fixed Dictionary <SAH>
    row.setValue("CICPaveRemove_CoreSY", CICPaveRemove_CoreSY); print CICPaveRemove_CoreSY; print "...CICPaveRemove_CoreSY"
    """Added Pavement Removal for T3Curb"""
    # Pavement Removal - ADA
    CICPaveRemove_ADA_SY_T3ARL = ((math.ceil(T3ARL[pageNo]) * 2.0) / 9.0)
    CICPaveRemove_ADA_SY_T3RL = ((math.ceil(T3RL[pageNo]) * 2.0) / 9.0)
    row.setValue("CICPaveRemove_ADASY", CICPaveRemove_ADA_SY_T3RL + CICPaveRemove_ADA_SY_T3ARL)

    # Curb Installation
    # T3 Curb/Gutter Removal  - CORE """UPDATED PER REVISION"""
    CICCurbGutRemove_CoreFT = RSCurbGutT3LF
    row.setValue("CICCurbGutRemove_CoreFT", CICCurbGutRemove_CoreFT); print CICCurbGutRemove_CoreFT; print "... CICCurbGutRemove_CoreFT"
    # T3 Curb/Gutter Removal - ADA """UPDATED PER REVISION"""
    CICCurbGutRemove_ADA_FT = RSCurbGutT3LFR
    row.setValue("CICCurbGutRemove_ADA_FT", CICCurbGutRemove_ADA_FT); print CICCurbGutRemove_ADA_FT; print "... CICCurbGutRemove_ADA_FT"
    # T4 Curb Removal - CORE """UPDATED PER REVISION"""
    CICT4CurbRemove_CoreFT = math.ceil(T4L[pageNo])
    row.setValue("CICT4CurbRemove_CoreFT", CICT4CurbRemove_CoreFT); print CICT4CurbRemove_CoreFT; print "... CICT4CurbRemove_CoreFT"
    # T4 Curb Removal - ADA """UPDATED PER REVISION"""
    CICT4CurbRemove_ADA_FT = math.ceil(T4RL[pageNo])
    row.setValue("CICT4CurbRemove_ADA_FT", CICT4CurbRemove_ADA_FT); print CICT4CurbRemove_ADA_FT; print "... CICT4CurbRemove_ADA_FT"

    # Earth Excavation - CORE * UPDATED
    totalT3Curb = ((((math.ceil(T3L[pageNo]) + math.ceil(T3AL[pageNo])) * 2.58) / 9.0) * 0.25) / 3.0 # Total T3 - CORE """UPDATED PER REVISION 2/3/13"""
    totalHEST3Curb = ((((math.ceil(T3DWL[pageNo]) + math.ceil(T3DWAL[pageNo])) * 1.58) / 9.0) * 0.25) / 3.0 # Total H.E.S. T3 Curb - CORE """UPDATED PER REVISION 2/3/13"""
    totalT4Curb = (((math.ceil(T4L[pageNo]) * 1.5) / 9.0) * 0.5) / 3.0 # Total T4 - CORE """UPDATED PER REVISION"""
##    totalRPRestorationCORE = ((math.ceil(RSPCCbcSY[pageNo]) + math.ceil(RCMApccBCcoreA[pageNo])) * 0.75) / 3 # Total Roadway Pavement Restoration - CORE
    cBusPadCY = (math.ceil(c_BusPad[pageNo]) * 0.75) / 3.0 # Concrete Bus Pad - CORE **UPDATED PER REVISIONS #Changed variable name to avoid confusion, fixed dictionary reference
    c_PavediagparkingCDS = (cpSY * 1.83) / 3.0 # Concrete Pavement for Diagonal Parking or Cul-De-Sac - CORE
    totalCDPave = (math.ceil(PCC_Driveway[pageNo]) * 0.75) / 3.0 # Total Concrete Driveway Pavement - CORE
    totalCAPave = (math.ceil(PCC_Alley[pageNo]) * 0.75) / 3.0 # Total Concrete Alley Pavement - CORE
##    totalBitDARest = (math.ceil(Drive_Alley_ATO[pageNo]) * 0.75) / 3 # Total Bituminous Driveway or Alley Restoration - CORE
    CICEarthExec_CoreCY = math.ceil(totalT3Curb + totalHEST3Curb + totalT4Curb + cBusPadCY + c_PavediagparkingCDS + totalCDPave + totalCAPave) ; print CICEarthExec_CoreCY #"""UPDATED PER REVISION 2/3/13"""
    row.setValue("CICEarthExec_CoreCY", CICEarthExec_CoreCY); print "... CICEarthExec_CoreCY"

    # Earth Excavation - ADA * UPDATED
    """Earth Excavation T3RCurb Depth changed to .25 and Area calculation adjusted per changes - TBU-03/12/2014"""
    totalT3RCurb = (((RSCurbGutT3LFR * 4.58) / 9.0) * 0.25) / 3.0 # Total T3R - ADA """UPDATED PER REVISION"""
    totalT4RCurb = (((math.ceil(T4RL[pageNo]) * 1.5) / 9.0) * 0.5) / 3.0 # Total T4R - ADA """UPDATED PER REVISION"""
##    totalRPRestorationADA = ((math.ceil(RCMApccBCadaR[pageNo]) + math.ceil(RCMApccBCadaA[pageNo])) * 0.75) / 3 # Total Roadway Pavement Restoration - ADA
    CICEarthExec_ADA_CY = math.ceil(totalT3RCurb + totalT4RCurb)
    row.setValue("CICEarthExec_ADA_CY", CICEarthExec_ADA_CY); print CICEarthExec_ADA_CY; print "... CICEarthExec_ADA_CY"

    # Search Cursor Final Calcs Updates
    CICShredHardwoodBark_CoreCY = (TreesInPits_No_Dict[pageNo] * 5.0) * (5.0 / 9.0)
    row.setValue("CICShredHardwoodBark_CoreCY", CICShredHardwoodBark_CoreCY) #"""UPDATED PER REVISION"""
    print ((TreesInPits_No_Dict[pageNo] * 5.0) * (5.0 / 9.0)); print "... TreesInPits_No"
    CICLinearDetWarnTiles_ADA_SF = ((NumberInRamps5in_Dict[pageNo] * 12.0) + (NumberInRamps8in_Dict[pageNo] * 12.0))
    row.setValue("CICLinearDetWarnTiles_ADA_SF" , CICLinearDetWarnTiles_ADA_SF) #"""UPDATED PER REVISION"""
    print (NumberInRamps5in_Dict[pageNo] * 12.0) + (NumberInRamps8in_Dict[pageNo] * 12.0); print "... NumberInRamps5in"
    row.setValue("CICDrainUtilityAdj_CoreEA" , DrainUtil_Adjusted_No_Dict[pageNo]) #"""UPDATED PER REVISION"""
    print DrainUtil_Adjusted_No_Dict[pageNo]; print "... DrainUtil_Adjusted_No"
    row.setValue("CICWaterShutRem_CoreEA" , WaterServ_Box_No_Dict[pageNo]) #"""UPDATED PER REVISION"""
    print WaterServ_Box_No_Dict[pageNo]; print "... WaterServ_Box_No"
    row.setValue("CICCatchBasinMHEtc_CoreEA" , DrainStruct_Clean_No_Dict[pageNo]) #"""UPDATED PER REVISION"""
    print DrainStruct_Clean_No_Dict[pageNo]; print "... DrainStruct_Clean_No"
    row.setValue("CICTreeProtection_CoreEA" , Tree_Protect_No_Dict[pageNo]) #"""UPDATED PER REVISION"""
    print Tree_Protect_No_Dict[pageNo]; print "... Tree_Protect_No"
    row.setValue("CICRootPruning_CoreEA" , (RootPruning_No_Dict[pageNo] * 20.0)) #"""UPDATED PER REVISION"""
    print (RootPruning_No_Dict[pageNo] * 20.0); print "... RootPruning_No"
##    row.setValue("CICCrushedStone_CoreTON" , (AlleyApron_Recon_No_Dict[pageNo] * 10.0)) #"""UPDATED PER REVISION"""
##    print (AlleyApron_Recon_No_Dict[pageNo] * 10.0); print "... AlleyApron_Recon_No"
    """Crushed Stone (Temporary Use) additional ADA Ramp Replacement and Driveway to calculation - TBU-03/17/2014"""
    alleyReturn = AlleyApron_Recon_No_Dict[pageNo] * 10.0
    Ramps_8in_5in = (RS5inPCCSidewalkRampSF + RS8inPCCSidewalkRampSF) * 2.5
    areaSY = math.ceil(PCC_Driveway[pageNo] / 9.0)
    row.setValue("CICCrushedStone_CoreTON" , math.ceil((alleyReturn + Ramps_8in_5in + (areaSY * 0.625))))


    """ **UPDATES PER REVISION - NEWEST ADDITION TO FINAL CALCS """
    # CICPCCBaseCourse10in_CoreSY
    CICPCCBaseCourse10in_CoreSY = math.ceil(PCC_Pave10in[pageNo]); print CICPCCBaseCourse10in_CoreSY; print "... CICPCCBaseCourse10in_CoreSY"
    row.setValue("CICPCCBaseCourse10in_CoreSY", CICPCCBaseCourse10in_CoreSY) #"""UPDATED PER REVISION"""
    # CICPCCBaseCourse12in_CoreSY
    CICPCCBaseCourse12in_CoreSY = math.ceil(PCC_Pave12in[pageNo]); print CICPCCBaseCourse12in_CoreSY; print "... CICPCCBaseCourse12in_CoreSY"
    row.setValue("CICPCCBaseCourse12in_CoreSY", CICPCCBaseCourse12in_CoreSY) #"""UPDATED PER REVISION"""

    # CICAlleyHESPCC8in_CoreSY
    CICAlleyHESPCC8in_CoreSY = math.ceil(HES_PCC_Alley_8in[pageNo]); print CICAlleyHESPCC8in_CoreSY; print "... CICAlleyHESPCC8in_CoreSY"
    row.setValue("CICAlleyHESPCC8in_CoreSY", CICAlleyHESPCC8in_CoreSY) #"""UPDATED PER REVISION"""
    # CICDriveHESPCC8in_CoreSY
    CICDriveHESPCC8in_CoreSY = math.ceil(HES_PCC_Driveway_8in[pageNo]); print CICDriveHESPCC8in_CoreSY; print "... CICDriveHESPCC8in_CoreSY"
    row.setValue("CICDriveHESPCC8in_CoreSY", CICDriveHESPCC8in_CoreSY) #"""UPDATED PER REVISION"""
    # CICSidewalkHESPCC8in_CoreSY
    CICSidewalkHESPCC8in_CoreSY = math.ceil(HES_PCC_Sidewalk_8in[pageNo]); print CICSidewalkHESPCC8in_CoreSY; print "... CICSidewalkHESPCC8in_CoreSY"
    row.setValue("CICSidewalkHESPCC8in_CoreSY", CICSidewalkHESPCC8in_CoreSY) #"""UPDATED PER REVISION"""

    # CICPCCADACurbRamp5in_ADA_SF
    CICPCCADACurbRamp5in_ADA_SF = math.ceil(PCC_5_rmp_SF[pageNo]); print CICPCCADACurbRamp5in_ADA_SF; print "... CICPCCADACurbRamp5in_ADA_SF"
    row.setValue("CICPCCADACurbRamp5in_ADA_SF", CICPCCADACurbRamp5in_ADA_SF) #"""UPDATED PER REVISION"""
    # CICPCCADACurbRamp8in_ADA_SF
    CICPCCADACurbRamp8in_ADA_SF = math.ceil(PCC_8_rmp_SF[pageNo]); print CICPCCADACurbRamp8in_ADA_SF; print "... CICPCCADACurbRamp8in_ADA_SF"
    row.setValue("CICPCCADACurbRamp8in_ADA_SF", CICPCCADACurbRamp8in_ADA_SF) #"""UPDATED PER REVISION"""

    """ LOOK OVER CAREFULLY TO CHECK IF IT WORKS """
    # CICPCCSW5inLess1800_CoreSF
#     PCC_5_SF_Value = PCC_5_SF.get([pageNo])
    if (PCC_5_SF[pageNo]) <= 1800.0:
        CICPCCSW5inLess1800_CoreSF = math.ceil(PCC_5_SF[pageNo]); print CICPCCSW5inLess1800_CoreSF; print "... CICPCCSW5inLess1800_CoreSF"
        row.setValue("CICPCCSW5inLess1800_CoreSF", CICPCCSW5inLess1800_CoreSF)
        row.setValue("CICPCCSW5inGreater1800_CoreSF", 0)
    # CICPCCSW5inLess1800_CoreSF
    if (PCC_5_SF[pageNo]) > 1800.0:
        CICPCCSW5inGreater1800_CoreSF = math.ceil(PCC_5_SF[pageNo]); print CICPCCSW5inGreater1800_CoreSF; print "... CICPCCSW5inGreater1800_CoreSF"
        row.setValue("CICPCCSW5inGreater1800_CoreSF", CICPCCSW5inGreater1800_CoreSF)
        row.setValue("CICPCCSW5inLess1800_CoreSF", 0)
    """**"""

    """ UPDATES PER REVISIONS - ADDING Combination Concrete Curb and Gutter, Type B-V.12 """
    # Combination Concrete Curb and Gutter > 300
    CICCurbGut300_Eval = math.ceil(T3L[pageNo]) + math.ceil(T3RL[pageNo]) + math.ceil(T3AL[pageNo]) + math.ceil(T3ARL[pageNo]); print CICCurbGut300_Eval; print "... CICCurbGut300_Eval"
    CICCurbGut300_ADAFill = math.ceil(T3RL[pageNo]) + math.ceil(T3ARL[pageNo]); print CICCurbGut300_ADAFill; print "... CICCurbGut300_ADAFill"
    CICCurbGut300_CoreFill = math.ceil(T3L[pageNo]) + math.ceil(T3AL[pageNo]); print CICCurbGut300_CoreFill; print "... CICCurbGut300_CoreFill"

    if  CICCurbGut300_Eval <= 300.0:
        row.setValue("CICCurbGutLess300_CoreLFT", CICCurbGut300_CoreFill) # TYPE 1 - CORE
        row.setValue("CICCurbGutLess300_ADA_FT", CICCurbGut300_ADAFill) # TYPE 2 - ADA
        row.setValue("CICCurbGutGreater300_CoreLFT", 0.0) # TYPE 1 - CORE
        row.setValue("CICCurbGutGreater300_ADA_FT", 0.0) # TYPE 2 - ADA
    else:
        row.setValue("CICCurbGutGreater300_CoreLFT",  CICCurbGut300_CoreFill) # TYPE 1 - CORE
        row.setValue("CICCurbGutGreater300_ADA_FT", CICCurbGut300_ADAFill) # TYPE 2 - ADA
        row.setValue("CICCurbGutLess300_CoreLFT", 0.0) # TYPE 1 - CORE
        row.setValue("CICCurbGutLess300_ADA_FT", 0.0) # TYPE 2 - ADA

    #Corner House
    row.setValue("strBlockCornerHouse", CornerHouse_Dict[pageNo])

    #Total Number of Ramps (IHC)
    row.setValue("RSRampTotalNum", NumberInRamps5in_Dict[pageNo] + NumberInRamps8in_Dict[pageNo])
    #Bus Pad SY (IHC)
    row.setValue("RSBusPadSY", c_BusPadSY)
    #Concrete Pavement SY (IHC)
    row.setValue("RSConcPaveSY", cpSY)

    #CIC PCC Base Course (ADA) <SAH> Added 3/18/2014
    PCC_7_ADA = ((math.ceil(T3RL[pageNo]) * 2.0) * CICHMAN30HM_ADATON) / 9.0
    row.setValue("CIC7ftPCCBaseCourse_ADASY", math.ceil(PCC_7_ADA))
    PCC_9_ADA = ((math.ceil(T3ARL[pageNo]) * 2.0) * CICHMAN70HM_ADATON) / 9.0
    row.setValue("CIC9ftPCCBaseCourse_ADASY", math.ceil(PCC_9_ADA))

    #Record Calc Date
    print today
    row.setValue("CalcByDate", today.strftime("%m/%d/%Y"))
    row.setValue("CalcBy", userInit)
    row.setValue("ReviewBy", reviewedBy)
    row.setValue("ReviewByDate", reviewByDate.split(" ")[0])

    """Added"""#TBU-01/23/2014
    #Survey By
    print SurveyBy
    arcpy.AddMessage("Surveyed By: " + SurveyBy)
    row.setValue("SurveyBy", SurveyBy)

    #Survey By Date
    print SurveyByDate
    #row.setvalue("SurveyByDate", SurveyByDate)
    row.setValue("SurveyByDate", SurveyByDate.strftime("%m/%d/%Y"))

    #Project Attributes
    row.setValue("lngMenuID", MenuID)
    row.setValue("lngWardID", WardID)
    row.setValue("strMenu", strMenu)

    if "-RS-" in cceNoCalcs:
        row.setValue("strMenu", "Ramp-Street")
        row.setValue("lngMenuID", "23")

    if "-RA-" in cceNoCalcs:
        row.setValue("strMenu", "Ramp-Alley")
        row.setValue("lngMenuID", "22")


    #Auto - Comments

    """Added to wrap comments"""#TBU-01/31/2014
    comments = AutoComments_Dict[pageNo]

    # Wrap the Comments to a list of strings
    newComments = []
    if "-AA-" in cceNo:
        newComments = textwrap.wrap(comments, 60)
    else:
        newComments = textwrap.wrap(comments, 100)

    # Add Escape sequences for newlines and concatenate
    newCommentsString= ""
    for x in newComments:
        if newComments.index(x) != (len(newComments) - 1):
            newCommentsString += x + " \n"
        else:
            newCommentsString += x

    #Set the value
    row.setValue("Comments", newCommentsString)

    #update the row
    u_cursor.updateRow(row); print "..."

del u_cursor


###Stop the editing session.
##edit.stopOperation()
##edit.stopEditing(True)
print "Finished FINAL Calcs..."

