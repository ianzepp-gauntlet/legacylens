"""209 suggestion-derived benchmark queries spanning 20 categories.

Expected files are auto-extracted from program names in query text.
For queries without explicit program names, the top search result
from the initial suggestion run is used as ground truth.
"""

from benchmarks.config import BenchmarkQuery


QUERIES_SUGGESTIONS: list[BenchmarkQuery] = [
    # -- User Management --
    BenchmarkQuery(
        query="What does COUSR00C do?",
        expected_files=['COUSR00C'],
        expected_chunks=[],
        description="User Management: What does COUSR00C do?",
    ),
    BenchmarkQuery(
        query="How does the user list screen work in COUSR00C?",
        expected_files=['COUSR00C'],
        expected_chunks=[],
        description="User Management: How does the user list screen work in COUSR00C?",
    ),
    BenchmarkQuery(
        query="How does COUSR01C handle user inquiry?",
        expected_files=['COUSR01C'],
        expected_chunks=[],
        description="User Management: How does COUSR01C handle user inquiry?",
    ),
    BenchmarkQuery(
        query="Explain the user add logic in COUSR02C",
        expected_files=['COUSR02C'],
        expected_chunks=[],
        description="User Management: Explain the user add logic in COUSR02C",
    ),
    BenchmarkQuery(
        query="How does COUSR03C update user records?",
        expected_files=['COUSR03C'],
        expected_chunks=[],
        description="User Management: How does COUSR03C update user records?",
    ),
    BenchmarkQuery(
        query="How is the USRSEC user security file accessed?",
        expected_files=['USRSEC'],
        expected_chunks=[],
        description="User Management: How is the USRSEC user security file accessed?",
    ),
    BenchmarkQuery(
        query="What is the user authentication flow in CardDemo?",
        expected_files=['CSUSR01Y'],
        expected_chunks=[],
        description="User Management: What is the user authentication flow in CardDemo?",
    ),
    BenchmarkQuery(
        query="How are user roles and permissions managed?",
        expected_files=['COUSR01'],
        expected_chunks=[],
        description="User Management: How are user roles and permissions managed?",
    ),
    BenchmarkQuery(
        query="How does the sign-on screen COSGN00C work?",
        expected_files=['COSGN00C'],
        expected_chunks=[],
        description="User Management: How does the sign-on screen COSGN00C work?",
    ),
    BenchmarkQuery(
        query="What validation happens during user login?",
        expected_files=['COUSR01C'],
        expected_chunks=['PROCESS-ENTER-KEY'],
        description="User Management: What validation happens during user login?",
    ),

    # -- Account Processing --
    BenchmarkQuery(
        query="What does COACTUPC do for account updates?",
        expected_files=['COACTUPC'],
        expected_chunks=[],
        description="Account Processing: What does COACTUPC do for account updates?",
    ),
    BenchmarkQuery(
        query="How does COACTVWC display account activity?",
        expected_files=['COACTVWC'],
        expected_chunks=[],
        description="Account Processing: How does COACTVWC display account activity?",
    ),
    BenchmarkQuery(
        query="What is the account inquiry logic in CBACT01C?",
        expected_files=['CBACT01C'],
        expected_chunks=[],
        description="Account Processing: What is the account inquiry logic in CBACT01C?",
    ),
    BenchmarkQuery(
        query="How does CBACT02C add new accounts?",
        expected_files=['CBACT02C'],
        expected_chunks=[],
        description="Account Processing: How does CBACT02C add new accounts?",
    ),
    BenchmarkQuery(
        query="How does CBACT03C modify account records?",
        expected_files=['CBACT03C'],
        expected_chunks=[],
        description="Account Processing: How does CBACT03C modify account records?",
    ),
    BenchmarkQuery(
        query="Explain the DB2 account delete in CBACT04C",
        expected_files=['CBACT04C'],
        expected_chunks=[],
        description="Account Processing: Explain the DB2 account delete in CBACT04C",
    ),
    BenchmarkQuery(
        query="How are account balances calculated?",
        expected_files=['CBACT04C'],
        expected_chunks=['1050-UPDATE-ACCOUNT'],
        description="Account Processing: How are account balances calculated?",
    ),
    BenchmarkQuery(
        query="How is the account cross-reference file used?",
        expected_files=['CBACT03C'],
        expected_chunks=[],
        description="Account Processing: How is the account cross-reference file used?",
    ),
    BenchmarkQuery(
        query="What is the account record structure in CVACT01Y?",
        expected_files=['CVACT01Y'],
        expected_chunks=[],
        description="Account Processing: What is the account record structure in CVACT01Y?",
    ),
    BenchmarkQuery(
        query="How does COACCT01 handle VSAM account operations?",
        expected_files=['COACCT01'],
        expected_chunks=[],
        description="Account Processing: How does COACCT01 handle VSAM account operations?",
    ),

    # -- Card Processing --
    BenchmarkQuery(
        query="What does COCRDLIC do for card listing?",
        expected_files=['COCRDLIC'],
        expected_chunks=[],
        description="Card Processing: What does COCRDLIC do for card listing?",
    ),
    BenchmarkQuery(
        query="How does the card selection screen COCRDSLC work?",
        expected_files=['COCRDSLC'],
        expected_chunks=[],
        description="Card Processing: How does the card selection screen COCRDSLC work?",
    ),
    BenchmarkQuery(
        query="Explain the card update logic in COCRDUPC",
        expected_files=['COCRDUPC'],
        expected_chunks=[],
        description="Card Processing: Explain the card update logic in COCRDUPC",
    ),
    BenchmarkQuery(
        query="How are credit card numbers validated?",
        expected_files=['COCRDSLC'],
        expected_chunks=['2220-EDIT-CARD, 2220-EDIT-CARD-EXIT'],
        description="Card Processing: How are credit card numbers validated?",
    ),
    BenchmarkQuery(
        query="What is the card record structure in CVACT02Y?",
        expected_files=['CVACT02Y'],
        expected_chunks=[],
        description="Card Processing: What is the card record structure in CVACT02Y?",
    ),
    BenchmarkQuery(
        query="How is the card cross-reference CVACT03Y used?",
        expected_files=['CVACT03Y'],
        expected_chunks=[],
        description="Card Processing: How is the card cross-reference CVACT03Y used?",
    ),
    BenchmarkQuery(
        query="What card work areas are defined in CVCRD01Y?",
        expected_files=['CVCRD01Y'],
        expected_chunks=[],
        description="Card Processing: What card work areas are defined in CVCRD01Y?",
    ),
    BenchmarkQuery(
        query="How does CardDemo handle card activation?",
        expected_files=['COCOM01Y'],
        expected_chunks=[],
        description="Card Processing: How does CardDemo handle card activation?",
    ),
    BenchmarkQuery(
        query="How does the card list BMS map COCRDLI work?",
        expected_files=['COCRDLI'],
        expected_chunks=[],
        description="Card Processing: How does the card list BMS map COCRDLI work?",
    ),
    BenchmarkQuery(
        query="What card data is stored in CARDFILE?",
        expected_files=['CARDFILE'],
        expected_chunks=[],
        description="Card Processing: What card data is stored in CARDFILE?",
    ),

    # -- Transaction Processing --
    BenchmarkQuery(
        query="How does CBTRN01C process daily transactions?",
        expected_files=['CBTRN01C'],
        expected_chunks=[],
        description="Transaction Processing: How does CBTRN01C process daily transactions?",
    ),
    BenchmarkQuery(
        query="Explain the DB2 transaction handling in CBTRN02C",
        expected_files=['CBTRN02C'],
        expected_chunks=[],
        description="Transaction Processing: Explain the DB2 transaction handling in CBTRN02C",
    ),
    BenchmarkQuery(
        query="What does the batch transaction program CBTRN03C do?",
        expected_files=['CBTRN03C'],
        expected_chunks=[],
        description="Transaction Processing: What does the batch transaction program CBTRN03C d",
    ),
    BenchmarkQuery(
        query="How does COTRN00C handle transaction inquiry?",
        expected_files=['COTRN00C'],
        expected_chunks=[],
        description="Transaction Processing: How does COTRN00C handle transaction inquiry?",
    ),
    BenchmarkQuery(
        query="Explain the transaction add flow in COTRN01C",
        expected_files=['COTRN01C'],
        expected_chunks=[],
        description="Transaction Processing: Explain the transaction add flow in COTRN01C",
    ),
    BenchmarkQuery(
        query="How does COTRN02C display transaction details?",
        expected_files=['COTRN02C'],
        expected_chunks=[],
        description="Transaction Processing: How does COTRN02C display transaction details?",
    ),
    BenchmarkQuery(
        query="What does COTRTLIC do for transaction type listing?",
        expected_files=['COTRTLIC'],
        expected_chunks=[],
        description="Transaction Processing: What does COTRTLIC do for transaction type listing",
    ),
    BenchmarkQuery(
        query="How does COTRTUPC update transactions via DB2?",
        expected_files=['COTRTUPC'],
        expected_chunks=[],
        description="Transaction Processing: How does COTRTUPC update transactions via DB2?",
    ),
    BenchmarkQuery(
        query="What is the transaction category balance in CVTRA01Y?",
        expected_files=['CVTRA01Y'],
        expected_chunks=[],
        description="Transaction Processing: What is the transaction category balance in CVTRA0",
    ),
    BenchmarkQuery(
        query="What transaction types are defined in CVTRA03Y?",
        expected_files=['CVTRA03Y'],
        expected_chunks=[],
        description="Transaction Processing: What transaction types are defined in CVTRA03Y?",
    ),
    BenchmarkQuery(
        query="How is the daily transaction file DALYTRAN used?",
        expected_files=['DALYTRAN'],
        expected_chunks=[],
        description="Transaction Processing: How is the daily transaction file DALYTRAN used?",
    ),
    BenchmarkQuery(
        query="What is the transaction record structure in CVTRA05Y?",
        expected_files=['CVTRA05Y'],
        expected_chunks=[],
        description="Transaction Processing: What is the transaction record structure in CVTRA0",
    ),
    BenchmarkQuery(
        query="Explain the transaction posting logic",
        expected_files=['POSTTRAN'],
        expected_chunks=[],
        description="Transaction Processing: Explain the transaction posting logic",
    ),
    BenchmarkQuery(
        query="How are transaction amounts validated?",
        expected_files=['COTRN02C'],
        expected_chunks=['VALIDATE-INPUT-DATA-FIELDS'],
        description="Transaction Processing: How are transaction amounts validated?",
    ),
    BenchmarkQuery(
        query="How does transaction reversal work?",
        expected_files=['TRANREPT'],
        expected_chunks=[],
        description="Transaction Processing: How does transaction reversal work?",
    ),

    # -- Export/Import --
    BenchmarkQuery(
        query="How does CBEXPORT export customer data?",
        expected_files=['CBEXPORT'],
        expected_chunks=[],
        description="Export/Import: How does CBEXPORT export customer data?",
    ),
    BenchmarkQuery(
        query="What account export format does CBEXPORT use?",
        expected_files=['CBEXPORT'],
        expected_chunks=[],
        description="Export/Import: What account export format does CBEXPORT use?",
    ),
    BenchmarkQuery(
        query="How does CBEXPORT handle cross-reference exports?",
        expected_files=['CBEXPORT'],
        expected_chunks=[],
        description="Export/Import: How does CBEXPORT handle cross-reference exports?",
    ),
    BenchmarkQuery(
        query="Explain the transaction export in CBEXPORT",
        expected_files=['CBEXPORT'],
        expected_chunks=[],
        description="Export/Import: Explain the transaction export in CBEXPORT",
    ),
    BenchmarkQuery(
        query="How does CBEXPORT export card records?",
        expected_files=['CBEXPORT'],
        expected_chunks=[],
        description="Export/Import: How does CBEXPORT export card records?",
    ),
    BenchmarkQuery(
        query="What does the CBIMPORT import utility do?",
        expected_files=['CBIMPORT'],
        expected_chunks=[],
        description="Export/Import: What does the CBIMPORT import utility do?",
    ),
    BenchmarkQuery(
        query="How does export file creation work?",
        expected_files=['CBEXPORT'],
        expected_chunks=[],
        description="Export/Import: How does export file creation work?",
    ),
    BenchmarkQuery(
        query="What validation does CBIMPORT perform on import?",
        expected_files=['CBIMPORT'],
        expected_chunks=[],
        description="Export/Import: What validation does CBIMPORT perform on import?",
    ),
    BenchmarkQuery(
        query="How are export records formatted?",
        expected_files=['CBEXPORT'],
        expected_chunks=['5700-CREATE-CARD-EXPORT-RECORD'],
        description="Export/Import: How are export records formatted?",
    ),
    BenchmarkQuery(
        query="What is the CREATE-CUSTOMER-EXP-REC paragraph?",
        expected_files=['CREATE', 'CUSTOMER'],
        expected_chunks=['CREATE-CUSTOMER-EXP-REC'],
        description="Export/Import: What is the CREATE-CUSTOMER-EXP-REC paragraph?",
    ),

    # -- Admin & Menu --
    BenchmarkQuery(
        query="What does the admin menu COADM01C do?",
        expected_files=['COADM01C'],
        expected_chunks=[],
        description="Admin & Menu: What does the admin menu COADM01C do?",
    ),
    BenchmarkQuery(
        query="How does the menu program COMEN01C work?",
        expected_files=['COMEN01C'],
        expected_chunks=[],
        description="Admin & Menu: How does the menu program COMEN01C work?",
    ),
    BenchmarkQuery(
        query="Explain the bill display logic in COBIL00C",
        expected_files=['COBIL00C'],
        expected_chunks=[],
        description="Admin & Menu: Explain the bill display logic in COBIL00C",
    ),
    BenchmarkQuery(
        query="How does CORPT00C generate reports?",
        expected_files=['CORPT00C'],
        expected_chunks=[],
        description="Admin & Menu: How does CORPT00C generate reports?",
    ),
    BenchmarkQuery(
        query="What is the admin transaction CA00?",
        expected_files=['COADM02Y'],
        expected_chunks=[],
        description="Admin & Menu: What is the admin transaction CA00?",
    ),
    BenchmarkQuery(
        query="What admin options are in COADM02Y?",
        expected_files=['COADM02Y'],
        expected_chunks=[],
        description="Admin & Menu: What admin options are in COADM02Y?",
    ),
    BenchmarkQuery(
        query="How does the admin menu BMS screen work?",
        expected_files=['COADM01'],
        expected_chunks=[],
        description="Admin & Menu: How does the admin menu BMS screen work?",
    ),
    BenchmarkQuery(
        query="What functions are available from the main menu?",
        expected_files=['COMEN01C'],
        expected_chunks=['POPULATE-HEADER-INFO'],
        description="Admin & Menu: What functions are available from the main menu?",
    ),
    BenchmarkQuery(
        query="How does navigation between screens work?",
        expected_files=['COACTUPC'],
        expected_chunks=['3400-SEND-SCREEN'],
        description="Admin & Menu: How does navigation between screens work?",
    ),
    BenchmarkQuery(
        query="What is the COBSWAIT wait command used for?",
        expected_files=['COBSWAIT'],
        expected_chunks=[],
        description="Admin & Menu: What is the COBSWAIT wait command used for?",
    ),

    # -- Date/Utility Programs --
    BenchmarkQuery(
        query="How does CSUTLDTC handle date and time?",
        expected_files=['CSUTLDTC'],
        expected_chunks=[],
        description="Date/Utility Programs: How does CSUTLDTC handle date and time?",
    ),
    BenchmarkQuery(
        query="What does the VSAM date handler CODATE01 do?",
        expected_files=['CODATE01'],
        expected_chunks=[],
        description="Date/Utility Programs: What does the VSAM date handler CODATE01 do?",
    ),
    BenchmarkQuery(
        query="How does CODATECN perform date conversion?",
        expected_files=['CODATECN'],
        expected_chunks=[],
        description="Date/Utility Programs: How does CODATECN perform date conversion?",
    ),
    BenchmarkQuery(
        query="What date utilities are in CSDAT01Y?",
        expected_files=['CSDAT01Y'],
        expected_chunks=[],
        description="Date/Utility Programs: What date utilities are in CSDAT01Y?",
    ),
    BenchmarkQuery(
        query="How does CSUTLDWY format dates?",
        expected_files=['CSUTLDWY'],
        expected_chunks=[],
        description="Date/Utility Programs: How does CSUTLDWY format dates?",
    ),
    BenchmarkQuery(
        query="What string formatting does CSSTRPFY provide?",
        expected_files=['CSSTRPFY'],
        expected_chunks=[],
        description="Date/Utility Programs: What string formatting does CSSTRPFY provide?",
    ),
    BenchmarkQuery(
        query="How does CSSETATY set screen attributes?",
        expected_files=['CSSETATY'],
        expected_chunks=[],
        description="Date/Utility Programs: How does CSSETATY set screen attributes?",
    ),
    BenchmarkQuery(
        query="What lookup codes are in CSLKPCDY?",
        expected_files=['CSLKPCDY'],
        expected_chunks=[],
        description="Date/Utility Programs: What lookup codes are in CSLKPCDY?",
    ),
    BenchmarkQuery(
        query="How is GENERATE-TIMESTAMP implemented?",
        expected_files=['GENERATE'],
        expected_chunks=['GENERATE-TIMESTAMP'],
        description="Date/Utility Programs: How is GENERATE-TIMESTAMP implemented?",
    ),
    BenchmarkQuery(
        query="What user utilities does CSUSR01Y provide?",
        expected_files=['CSUSR01Y'],
        expected_chunks=[],
        description="Date/Utility Programs: What user utilities does CSUSR01Y provide?",
    ),

    # -- Copybook Structures --
    BenchmarkQuery(
        query="What is the customer record structure in CVCUS01Y?",
        expected_files=['CVCUS01Y'],
        expected_chunks=[],
        description="Copybook Structures: What is the customer record structure in CVCUS01Y?",
    ),
    BenchmarkQuery(
        query="Explain the communication area COCOM01Y",
        expected_files=['COCOM01Y'],
        expected_chunks=[],
        description="Copybook Structures: Explain the communication area COCOM01Y",
    ),
    BenchmarkQuery(
        query="What fields are in the account record CVACT01Y?",
        expected_files=['CVACT01Y'],
        expected_chunks=[],
        description="Copybook Structures: What fields are in the account record CVACT01Y?",
    ),
    BenchmarkQuery(
        query="How is the transaction category type CVTRA04Y structured?",
        expected_files=['CVTRA04Y'],
        expected_chunks=[],
        description="Copybook Structures: How is the transaction category type CVTRA04Y stru",
    ),
    BenchmarkQuery(
        query="What is in the reporting copybook CVTRA07Y?",
        expected_files=['CVTRA07Y'],
        expected_chunks=[],
        description="Copybook Structures: What is in the reporting copybook CVTRA07Y?",
    ),
    BenchmarkQuery(
        query="How is the disclosure group structure CVTRA02Y used?",
        expected_files=['CVTRA02Y'],
        expected_chunks=[],
        description="Copybook Structures: How is the disclosure group structure CVTRA02Y use",
    ),
    BenchmarkQuery(
        query="What message handling does CSMSG01Y provide?",
        expected_files=['CSMSG01Y'],
        expected_chunks=[],
        description="Copybook Structures: What message handling does CSMSG01Y provide?",
    ),
    BenchmarkQuery(
        query="What message arrays are in CSMSG02Y?",
        expected_files=['CSMSG02Y'],
        expected_chunks=[],
        description="Copybook Structures: What message arrays are in CSMSG02Y?",
    ),
    BenchmarkQuery(
        query="What DB2 working storage is in CSDB2RWY?",
        expected_files=['CSDB2RWY'],
        expected_chunks=[],
        description="Copybook Structures: What DB2 working storage is in CSDB2RWY?",
    ),
    BenchmarkQuery(
        query="What DB2 procedures are in CSDB2RPY?",
        expected_files=['CSDB2RPY'],
        expected_chunks=[],
        description="Copybook Structures: What DB2 procedures are in CSDB2RPY?",
    ),

    # -- BMS Maps & Screens --
    BenchmarkQuery(
        query="How is the sign-on BMS map COSGN00 structured?",
        expected_files=['COSGN00'],
        expected_chunks=[],
        description="BMS Maps & Screens: How is the sign-on BMS map COSGN00 structured?",
    ),
    BenchmarkQuery(
        query="What fields does the account view map COACTVW have?",
        expected_files=['COACTVW'],
        expected_chunks=[],
        description="BMS Maps & Screens: What fields does the account view map COACTVW have",
    ),
    BenchmarkQuery(
        query="How is the transaction inquiry map COTRN00 laid out?",
        expected_files=['COTRN00'],
        expected_chunks=[],
        description="BMS Maps & Screens: How is the transaction inquiry map COTRN00 laid ou",
    ),
    BenchmarkQuery(
        query="What does the transaction add map COTRN01 contain?",
        expected_files=['COTRN01'],
        expected_chunks=[],
        description="BMS Maps & Screens: What does the transaction add map COTRN01 contain?",
    ),
    BenchmarkQuery(
        query="How is the report display map CORPT00 structured?",
        expected_files=['CORPT00'],
        expected_chunks=[],
        description="BMS Maps & Screens: How is the report display map CORPT00 structured?",
    ),
    BenchmarkQuery(
        query="What fields are on the user list map COUSR00?",
        expected_files=['COUSR00'],
        expected_chunks=[],
        description="BMS Maps & Screens: What fields are on the user list map COUSR00?",
    ),
    BenchmarkQuery(
        query="How is the authorization screen COPAU00 designed?",
        expected_files=['COPAU00'],
        expected_chunks=[],
        description="BMS Maps & Screens: How is the authorization screen COPAU00 designed?",
    ),
    BenchmarkQuery(
        query="What does the card update map COCRDUP contain?",
        expected_files=['COCRDUP'],
        expected_chunks=[],
        description="BMS Maps & Screens: What does the card update map COCRDUP contain?",
    ),
    BenchmarkQuery(
        query="How are BMS maps defined with DFHMSD and DFHMDI?",
        expected_files=['COCRDLI'],
        expected_chunks=[],
        description="BMS Maps & Screens: How are BMS maps defined with DFHMSD and DFHMDI?",
    ),
    BenchmarkQuery(
        query="What screen attributes are used in the BMS maps?",
        expected_files=['COCRDLI'],
        expected_chunks=[],
        description="BMS Maps & Screens: What screen attributes are used in the BMS maps?",
    ),

    # -- JCL Jobs --
    BenchmarkQuery(
        query="What does the ACCTFILE JCL job define?",
        expected_files=['ACCTFILE'],
        expected_chunks=[],
        description="JCL Jobs: What does the ACCTFILE JCL job define?",
    ),
    BenchmarkQuery(
        query="How does the CARDFILE JCL set up card data?",
        expected_files=['CARDFILE'],
        expected_chunks=[],
        description="JCL Jobs: How does the CARDFILE JCL set up card data?",
    ),
    BenchmarkQuery(
        query="What does the CUSTFILE JCL job do?",
        expected_files=['CUSTFILE'],
        expected_chunks=[],
        description="JCL Jobs: What does the CUSTFILE JCL job do?",
    ),
    BenchmarkQuery(
        query="How does the DEFGDGB JCL define GDG backups?",
        expected_files=['DEFGDGB'],
        expected_chunks=[],
        description="JCL Jobs: How does the DEFGDGB JCL define GDG backups?",
    ),
    BenchmarkQuery(
        query="What does the XREFFILE JCL create?",
        expected_files=['XREFFILE'],
        expected_chunks=[],
        description="JCL Jobs: What does the XREFFILE JCL create?",
    ),
    BenchmarkQuery(
        query="How does the TRANFILE JCL define transaction files?",
        expected_files=['TRANFILE'],
        expected_chunks=[],
        description="JCL Jobs: How does the TRANFILE JCL define transaction files",
    ),
    BenchmarkQuery(
        query="What does the READACCT JCL job do?",
        expected_files=['READACCT'],
        expected_chunks=[],
        description="JCL Jobs: What does the READACCT JCL job do?",
    ),
    BenchmarkQuery(
        query="How does the CLOSEFIL JCL close all files?",
        expected_files=['CLOSEFIL'],
        expected_chunks=[],
        description="JCL Jobs: How does the CLOSEFIL JCL close all files?",
    ),
    BenchmarkQuery(
        query="What does the OPENFIL JCL job open?",
        expected_files=['OPENFIL'],
        expected_chunks=[],
        description="JCL Jobs: What does the OPENFIL JCL job open?",
    ),
    BenchmarkQuery(
        query="How does the TRANREPT JCL generate reports?",
        expected_files=['TRANREPT'],
        expected_chunks=[],
        description="JCL Jobs: How does the TRANREPT JCL generate reports?",
    ),
    BenchmarkQuery(
        query="What does the CBEXPORT JCL job execute?",
        expected_files=['CBEXPORT'],
        expected_chunks=[],
        description="JCL Jobs: What does the CBEXPORT JCL job execute?",
    ),
    BenchmarkQuery(
        query="How does the CBIMPORT JCL run imports?",
        expected_files=['CBIMPORT'],
        expected_chunks=[],
        description="JCL Jobs: How does the CBIMPORT JCL run imports?",
    ),
    BenchmarkQuery(
        query="What does INTCALC calculate?",
        expected_files=['INTCALC'],
        expected_chunks=[],
        description="JCL Jobs: What does INTCALC calculate?",
    ),
    BenchmarkQuery(
        query="How does the POSTTRAN JCL post transactions?",
        expected_files=['POSTTRAN'],
        expected_chunks=[],
        description="JCL Jobs: How does the POSTTRAN JCL post transactions?",
    ),
    BenchmarkQuery(
        query="What does the CREADB21 JCL create in DB2?",
        expected_files=['CREADB21'],
        expected_chunks=[],
        description="JCL Jobs: What does the CREADB21 JCL create in DB2?",
    ),

    # -- CICS Operations --
    BenchmarkQuery(
        query="How does CardDemo use CICS LINK for program calls?",
        expected_files=['CBADMCDJ'],
        expected_chunks=[],
        description="CICS Operations: How does CardDemo use CICS LINK for program calls?",
    ),
    BenchmarkQuery(
        query="What EXEC CICS commands are most common?",
        expected_files=['CORPT00C'],
        expected_chunks=['RETURN-TO-CICS'],
        description="CICS Operations: What EXEC CICS commands are most common?",
    ),
    BenchmarkQuery(
        query="How is the COMMAREA used for inter-program communication?",
        expected_files=['COMMAREA'],
        expected_chunks=[],
        description="CICS Operations: How is the COMMAREA used for inter-program communi",
    ),
    BenchmarkQuery(
        query="How do CICS screen SEND operations work?",
        expected_files=['COCRDLIC'],
        expected_chunks=['1500-SEND-SCREEN, 1500-SEND-SCREEN-EXIT'],
        description="CICS Operations: How do CICS screen SEND operations work?",
    ),
    BenchmarkQuery(
        query="How does CICS RECEIVE capture user input?",
        expected_files=['COUSR00C'],
        expected_chunks=['RECEIVE-USRLST-SCREEN'],
        description="CICS Operations: How does CICS RECEIVE capture user input?",
    ),
    BenchmarkQuery(
        query="What CICS file control operations are used?",
        expected_files=['COCRDLIC'],
        expected_chunks=['WS-MISC-STORAGE'],
        description="CICS Operations: What CICS file control operations are used?",
    ),
    BenchmarkQuery(
        query="How are CICS response codes handled?",
        expected_files=['COCRDSLC'],
        expected_chunks=['WS-MISC-STORAGE'],
        description="CICS Operations: How are CICS response codes handled?",
    ),
    BenchmarkQuery(
        query="What CICS XCTL transfers exist between programs?",
        expected_files=['COTRN00C'],
        expected_chunks=['PROCESS-ENTER-KEY'],
        description="CICS Operations: What CICS XCTL transfers exist between programs?",
    ),
    BenchmarkQuery(
        query="How does CICS exception handling work?",
        expected_files=['COCRDUPC'],
        expected_chunks=['ABEND-ROUTINE'],
        description="CICS Operations: How does CICS exception handling work?",
    ),
    BenchmarkQuery(
        query="What transaction IDs (TRANIDs) are defined?",
        expected_files=['COTRN00C'],
        expected_chunks=['POPULATE-TRAN-DATA'],
        description="CICS Operations: What transaction IDs (TRANIDs) are defined?",
    ),

    # -- DB2 Operations --
    BenchmarkQuery(
        query="How does CardDemo use EXEC SQL statements?",
        expected_files=['CVACT02Y'],
        expected_chunks=[],
        description="DB2 Operations: How does CardDemo use EXEC SQL statements?",
    ),
    BenchmarkQuery(
        query="How is the SQLCA used for DB2 error handling?",
        expected_files=['CSDB2RPY'],
        expected_chunks=[],
        description="DB2 Operations: How is the SQLCA used for DB2 error handling?",
    ),
    BenchmarkQuery(
        query="What DB2 cursors are declared in the programs?",
        expected_files=['COTRTLIC'],
        expected_chunks=[],
        description="DB2 Operations: What DB2 cursors are declared in the programs?",
    ),
    BenchmarkQuery(
        query="How are DB2 SELECT queries structured?",
        expected_files=['CSDB2RPY'],
        expected_chunks=[],
        description="DB2 Operations: How are DB2 SELECT queries structured?",
    ),
    BenchmarkQuery(
        query="What DB2 INSERT operations exist?",
        expected_files=['DB2LTTYP'],
        expected_chunks=[],
        description="DB2 Operations: What DB2 INSERT operations exist?",
    ),
    BenchmarkQuery(
        query="How do DB2 UPDATE statements work in CardDemo?",
        expected_files=['COPAUS2C'],
        expected_chunks=['FRAUD-UPDATE'],
        description="DB2 Operations: How do DB2 UPDATE statements work in CardDemo?",
    ),
    BenchmarkQuery(
        query="How does DB2 COMMIT and ROLLBACK work?",
        expected_files=['DB2LTTYP'],
        expected_chunks=[],
        description="DB2 Operations: How does DB2 COMMIT and ROLLBACK work?",
    ),
    BenchmarkQuery(
        query="What WHENEVER statements handle DB2 errors?",
        expected_files=['CSDB2RPY'],
        expected_chunks=[],
        description="DB2 Operations: What WHENEVER statements handle DB2 errors?",
    ),
    BenchmarkQuery(
        query="How is the NOT FOUND condition handled in DB2?",
        expected_files=['DB2LTCAT'],
        expected_chunks=[],
        description="DB2 Operations: How is the NOT FOUND condition handled in DB2?",
    ),
    BenchmarkQuery(
        query="What DB2 tables does CardDemo define?",
        expected_files=['DB2CREAT'],
        expected_chunks=[],
        description="DB2 Operations: What DB2 tables does CardDemo define?",
    ),

    # -- VSAM File Operations --
    BenchmarkQuery(
        query="How does CardDemo use VSAM KSDS files?",
        expected_files=['CARDFILE'],
        expected_chunks=[],
        description="VSAM File Operations: How does CardDemo use VSAM KSDS files?",
    ),
    BenchmarkQuery(
        query="What VSAM file status codes are checked?",
        expected_files=['CBTRN02C'],
        expected_chunks=['9910-DISPLAY-IO-STATUS'],
        description="VSAM File Operations: What VSAM file status codes are checked?",
    ),
    BenchmarkQuery(
        query="How does STARTBR begin a VSAM browse?",
        expected_files=['READACCT'],
        expected_chunks=[],
        description="VSAM File Operations: How does STARTBR begin a VSAM browse?",
    ),
    BenchmarkQuery(
        query="How does READNEXT do sequential VSAM reads?",
        expected_files=['COUSR00C'],
        expected_chunks=['READNEXT-USER-SEC-FILE'],
        description="VSAM File Operations: How does READNEXT do sequential VSAM reads?",
    ),
    BenchmarkQuery(
        query="How does READPREV read VSAM records backward?",
        expected_files=['COCRDLIC'],
        expected_chunks=['9100-READ-BACKWARDS'],
        description="VSAM File Operations: How does READPREV read VSAM records backward?",
    ),
    BenchmarkQuery(
        query="How does ENDBR end a VSAM browse?",
        expected_files=['READACCT'],
        expected_chunks=[],
        description="VSAM File Operations: How does ENDBR end a VSAM browse?",
    ),
    BenchmarkQuery(
        query="What VSAM error handling patterns exist?",
        expected_files=['CSDB2RPY'],
        expected_chunks=[],
        description="VSAM File Operations: What VSAM error handling patterns exist?",
    ),
    BenchmarkQuery(
        query="How does READ-CUSTOMER-RECORD fetch customer data?",
        expected_files=['CUSTOMER', 'RECORD'],
        expected_chunks=['READ-CUSTOMER-RECORD'],
        description="VSAM File Operations: How does READ-CUSTOMER-RECORD fetch customer data?",
    ),
    BenchmarkQuery(
        query="How does READ-ACCOUNT-RECORD work?",
        expected_files=['ACCOUNT', 'RECORD'],
        expected_chunks=['READ-ACCOUNT-RECORD'],
        description="VSAM File Operations: How does READ-ACCOUNT-RECORD work?",
    ),
    BenchmarkQuery(
        query="How does READ-CARD-RECORD retrieve card data?",
        expected_files=['RECORD'],
        expected_chunks=['READ-CARD-RECORD'],
        description="VSAM File Operations: How does READ-CARD-RECORD retrieve card data?",
    ),

    # -- Paragraph/Section Patterns --
    BenchmarkQuery(
        query="What does the MAIN-PARA entry point do?",
        expected_files=[],
        expected_chunks=['MAIN-PARA'],
        description="Paragraph/Section Patterns: What does the MAIN-PARA entry point do?",
    ),
    BenchmarkQuery(
        query="How does 0000-MAIN-PROCESSING work in batch programs?",
        expected_files=[],
        expected_chunks=['0000-MAIN-PROCESSING'],
        description="Paragraph/Section Patterns: How does 0000-MAIN-PROCESSING work in batch progra",
    ),
    BenchmarkQuery(
        query="What happens in the 1000-INITIALIZE paragraph?",
        expected_files=[],
        expected_chunks=['1000-INITIALIZE'],
        description="Paragraph/Section Patterns: What happens in the 1000-INITIALIZE paragraph?",
    ),
    BenchmarkQuery(
        query="How does PROCESS-ENTER-KEY handle user input?",
        expected_files=['ENTER', 'PROCESS'],
        expected_chunks=['PROCESS-ENTER-KEY'],
        description="Paragraph/Section Patterns: How does PROCESS-ENTER-KEY handle user input?",
    ),
    BenchmarkQuery(
        query="How do PF key handlers like PROCESS-PF7-KEY work?",
        expected_files=['PROCESS'],
        expected_chunks=['PROCESS-PF7-KEY'],
        description="Paragraph/Section Patterns: How do PF key handlers like PROCESS-PF7-KEY work?",
    ),
    BenchmarkQuery(
        query="What does POPULATE-USER-DATA load?",
        expected_files=['POPULATE'],
        expected_chunks=['POPULATE-USER-DATA'],
        description="Paragraph/Section Patterns: What does POPULATE-USER-DATA load?",
    ),
    BenchmarkQuery(
        query="How does POPULATE-HEADER-INFO set screen headers?",
        expected_files=['HEADER', 'POPULATE'],
        expected_chunks=['POPULATE-HEADER-INFO'],
        description="Paragraph/Section Patterns: How does POPULATE-HEADER-INFO set screen headers?",
    ),
    BenchmarkQuery(
        query="What does INITIALIZE-USER-DATA reset?",
        expected_files=[],
        expected_chunks=['INITIALIZE-USER-DATA'],
        description="Paragraph/Section Patterns: What does INITIALIZE-USER-DATA reset?",
    ),
    BenchmarkQuery(
        query="How does Z-ABEND-PROGRAM handle abnormal ends?",
        expected_files=['ABEND', 'PROGRAM'],
        expected_chunks=['Z-ABEND-PROGRAM'],
        description="Paragraph/Section Patterns: How does Z-ABEND-PROGRAM handle abnormal ends?",
    ),
    BenchmarkQuery(
        query="What does Z-DISPLAY-IO-STATUS show?",
        expected_files=['STATUS'],
        expected_chunks=['Z-DISPLAY-IO-STATUS'],
        description="Paragraph/Section Patterns: What does Z-DISPLAY-IO-STATUS show?",
    ),

    # -- Data Elements --
    BenchmarkQuery(
        query="What is WS-PGMNAME used for?",
        expected_files=['PGMNAME'],
        expected_chunks=['WS-PGMNAME'],
        description="Data Elements: What is WS-PGMNAME used for?",
    ),
    BenchmarkQuery(
        query="How is WS-TRANID set in each program?",
        expected_files=[],
        expected_chunks=['WS-TRANID'],
        description="Data Elements: How is WS-TRANID set in each program?",
    ),
    BenchmarkQuery(
        query="What does WS-MESSAGE contain?",
        expected_files=['MESSAGE'],
        expected_chunks=['WS-MESSAGE'],
        description="Data Elements: What does WS-MESSAGE contain?",
    ),
    BenchmarkQuery(
        query="How are WS-RESP-CD and WS-REAS-CD used?",
        expected_files=[],
        expected_chunks=['WS-REAS-CD', 'WS-RESP-CD'],
        description="Data Elements: How are WS-RESP-CD and WS-REAS-CD used?",
    ),
    BenchmarkQuery(
        query="What record counters track in WS-REC-COUNT?",
        expected_files=['COUNT'],
        expected_chunks=['WS-REC-COUNT'],
        description="Data Elements: What record counters track in WS-REC-COUNT?",
    ),
    BenchmarkQuery(
        query="How is WS-ERR-FLG used for error detection?",
        expected_files=[],
        expected_chunks=['WS-ERR-FLG'],
        description="Data Elements: How is WS-ERR-FLG used for error detection?",
    ),
    BenchmarkQuery(
        query="How does WS-PAGE-NUM control pagination?",
        expected_files=[],
        expected_chunks=['WS-PAGE-NUM'],
        description="Data Elements: How does WS-PAGE-NUM control pagination?",
    ),
    BenchmarkQuery(
        query="What OCCURS clause arrays exist in the programs?",
        expected_files=['CBSTM03A'],
        expected_chunks=['WS-TRNX-TABLE'],
        description="Data Elements: What OCCURS clause arrays exist in the programs?",
    ),
    BenchmarkQuery(
        query="How are level 88 conditions used in CardDemo?",
        expected_files=['COBIL00'],
        expected_chunks=[],
        description="Data Elements: How are level 88 conditions used in CardDemo?",
    ),
    BenchmarkQuery(
        query="What is in the DFHCOMMAREA linkage section?",
        expected_files=['COTRTUPC'],
        expected_chunks=[],
        description="Data Elements: What is in the DFHCOMMAREA linkage section?",
    ),

    # -- Cross-Cutting Concerns --
    BenchmarkQuery(
        query="How does error handling work across COBOL programs?",
        expected_files=['COBOL'],
        expected_chunks=[],
        description="Cross-Cutting Concerns: How does error handling work across COBOL programs",
    ),
    BenchmarkQuery(
        query="What COPY statements are shared between programs?",
        expected_files=['COCOM01Y'],
        expected_chunks=[],
        description="Cross-Cutting Concerns: What COPY statements are shared between programs?",
    ),
    BenchmarkQuery(
        query="How does RETURN-TO-PREV-SCREEN navigate on errors?",
        expected_files=['SCREEN'],
        expected_chunks=['RETURN-TO-PREV-SCREEN'],
        description="Cross-Cutting Concerns: How does RETURN-TO-PREV-SCREEN navigate on errors?",
    ),
    BenchmarkQuery(
        query="What PERFORM targets are common across programs?",
        expected_files=['COCRDLIC'],
        expected_chunks=['9500-FILTER-RECORDS-EXIT'],
        description="Cross-Cutting Concerns: What PERFORM targets are common across programs?",
    ),
    BenchmarkQuery(
        query="How does page-forward and page-backward scrolling work?",
        expected_files=['COTRN00C'],
        expected_chunks=['PROCESS-PAGE-FORWARD'],
        description="Cross-Cutting Concerns: How does page-forward and page-backward scrolling ",
    ),
    BenchmarkQuery(
        query="What data validation patterns are reused?",
        expected_files=['COCRDLIC'],
        expected_chunks=['1250-SETUP-ARRAY-ATTRIBS, 1250-SETUP-ARRAY-ATTRIBS-EXIT'],
        description="Cross-Cutting Concerns: What data validation patterns are reused?",
    ),
    BenchmarkQuery(
        query="How do programs pass data via the communication area?",
        expected_files=['COCOM01Y'],
        expected_chunks=[],
        description="Cross-Cutting Concerns: How do programs pass data via the communication ar",
    ),
    BenchmarkQuery(
        query="What naming conventions do the COBOL programs follow?",
        expected_files=['COBOL'],
        expected_chunks=[],
        description="Cross-Cutting Concerns: What naming conventions do the COBOL programs foll",
    ),
    BenchmarkQuery(
        query="How are WORKING-STORAGE sections organized?",
        expected_files=['STORAGE'],
        expected_chunks=['WORKING-STORAGE'],
        description="Cross-Cutting Concerns: How are WORKING-STORAGE sections organized?",
    ),
    BenchmarkQuery(
        query="What is the overall program call hierarchy?",
        expected_files=['COCRDSLC'],
        expected_chunks=['WS-THIS-PROGCOMMAREA'],
        description="Cross-Cutting Concerns: What is the overall program call hierarchy?",
    ),

    # -- Business Domain --
    BenchmarkQuery(
        query="What is the end-to-end credit card transaction flow?",
        expected_files=['COCRDSLC'],
        expected_chunks=['COMMON-RETURN, 0000-MAIN-EXIT'],
        description="Business Domain: What is the end-to-end credit card transaction flo",
    ),
    BenchmarkQuery(
        query="How does CardDemo handle interest calculation?",
        expected_files=['COBIL00'],
        expected_chunks=[],
        description="Business Domain: How does CardDemo handle interest calculation?",
    ),
    BenchmarkQuery(
        query="What reporting capabilities does the application have?",
        expected_files=['CBTRN03C'],
        expected_chunks=['1111-WRITE-REPORT-REC'],
        description="Business Domain: What reporting capabilities does the application h",
    ),
    BenchmarkQuery(
        query="How does the daily transaction batch cycle work?",
        expected_files=['CBTRN02C'],
        expected_chunks=['9300-DALYREJS-CLOSE'],
        description="Business Domain: How does the daily transaction batch cycle work?",
    ),
    BenchmarkQuery(
        query="What reconciliation processes exist?",
        expected_files=['CREASTMT'],
        expected_chunks=[],
        description="Business Domain: What reconciliation processes exist?",
    ),
    BenchmarkQuery(
        query="How are transaction categories and types classified?",
        expected_files=['DB2LTCAT'],
        expected_chunks=[],
        description="Business Domain: How are transaction categories and types classifie",
    ),
    BenchmarkQuery(
        query="What is the customer-account-card relationship?",
        expected_files=['CUSTREC'],
        expected_chunks=[],
        description="Business Domain: What is the customer-account-card relationship?",
    ),
    BenchmarkQuery(
        query="How does CardDemo handle regulatory reporting?",
        expected_files=['CVTRA07Y'],
        expected_chunks=[],
        description="Business Domain: How does CardDemo handle regulatory reporting?",
    ),
    BenchmarkQuery(
        query="What audit trail capabilities exist?",
        expected_files=['COPAU01'],
        expected_chunks=[],
        description="Business Domain: What audit trail capabilities exist?",
    ),
    BenchmarkQuery(
        query="How does the application handle exception processing?",
        expected_files=['COCRDUPC'],
        expected_chunks=['ABEND-ROUTINE'],
        description="Business Domain: How does the application handle exception processi",
    ),

    # -- Architecture & Integration --
    BenchmarkQuery(
        query="What is the overall architecture of the CardDemo system?",
        expected_files=['COCOM01Y'],
        expected_chunks=[],
        description="Architecture & Integration: What is the overall architecture of the CardDemo s",
    ),
    BenchmarkQuery(
        query="How many COBOL programs make up CardDemo?",
        expected_files=['COBOL'],
        expected_chunks=[],
        description="Architecture & Integration: How many COBOL programs make up CardDemo?",
    ),
    BenchmarkQuery(
        query="What batch vs online programs exist?",
        expected_files=['CORPT00C'],
        expected_chunks=[],
        description="Architecture & Integration: What batch vs online programs exist?",
    ),
    BenchmarkQuery(
        query="How do online CICS programs differ from batch programs?",
        expected_files=['CORPT00C'],
        expected_chunks=[],
        description="Architecture & Integration: How do online CICS programs differ from batch prog",
    ),
    BenchmarkQuery(
        query="What is the relationship between BMS maps and COBOL programs?",
        expected_files=['COBOL'],
        expected_chunks=[],
        description="Architecture & Integration: What is the relationship between BMS maps and COBO",
    ),
    BenchmarkQuery(
        query="How does the ENVIRONMENT DIVISION configure file access?",
        expected_files=['CARDDEMO'],
        expected_chunks=[],
        description="Architecture & Integration: How does the ENVIRONMENT DIVISION configure file a",
    ),
    BenchmarkQuery(
        query="What FILE SECTION definitions exist in the DATA DIVISION?",
        expected_files=['PAUDBLOD'],
        expected_chunks=[],
        description="Architecture & Integration: What FILE SECTION definitions exist in the DATA DI",
    ),
    BenchmarkQuery(
        query="How is the PROCEDURE DIVISION structured across programs?",
        expected_files=['CORPT00C'],
        expected_chunks=[],
        description="Architecture & Integration: How is the PROCEDURE DIVISION structured across pr",
    ),
    BenchmarkQuery(
        query="What IDENTIFICATION DIVISION metadata is recorded?",
        expected_files=['DBUNLDGS'],
        expected_chunks=[],
        description="Architecture & Integration: What IDENTIFICATION DIVISION metadata is recorded?",
    ),
    BenchmarkQuery(
        query="How do copybooks reduce code duplication?",
        expected_files=['COPAU01'],
        expected_chunks=[],
        description="Architecture & Integration: How do copybooks reduce code duplication?",
    ),

    # -- Specific Operations --
    BenchmarkQuery(
        query="How does LOOKUP-XREF perform cross-reference lookups?",
        expected_files=['LOOKUP'],
        expected_chunks=['LOOKUP-XREF'],
        description="Specific Operations: How does LOOKUP-XREF perform cross-reference looku",
    ),
    BenchmarkQuery(
        query="What does CREATE-ACCOUNT-EXP-REC format for export?",
        expected_files=['ACCOUNT', 'CREATE'],
        expected_chunks=['CREATE-ACCOUNT-EXP-REC'],
        description="Specific Operations: What does CREATE-ACCOUNT-EXP-REC format for export",
    ),
    BenchmarkQuery(
        query="How does CREATE-XREF-EXPORT-RECORD work?",
        expected_files=['CREATE', 'EXPORT', 'RECORD'],
        expected_chunks=['CREATE-XREF-EXPORT-RECORD'],
        description="Specific Operations: How does CREATE-XREF-EXPORT-RECORD work?",
    ),
    BenchmarkQuery(
        query="What does CREATE-CARD-EXPORT-RECORD output?",
        expected_files=['CREATE', 'EXPORT', 'RECORD'],
        expected_chunks=['CREATE-CARD-EXPORT-RECORD'],
        description="Specific Operations: What does CREATE-CARD-EXPORT-RECORD output?",
    ),
    BenchmarkQuery(
        query="How does SEND-USRLST-SCREEN transmit the user list?",
        expected_files=['SCREEN', 'USRLST'],
        expected_chunks=['SEND-USRLST-SCREEN'],
        description="Specific Operations: How does SEND-USRLST-SCREEN transmit the user list",
    ),
    BenchmarkQuery(
        query="How does RECEIVE-USRLST-SCREEN capture user input?",
        expected_files=['SCREEN', 'USRLST'],
        expected_chunks=['RECEIVE-USRLST-SCREEN'],
        description="Specific Operations: How does RECEIVE-USRLST-SCREEN capture user input?",
    ),
    BenchmarkQuery(
        query="What does SEND-ACTVW-SCREEN display?",
        expected_files=['ACTVW', 'SCREEN'],
        expected_chunks=['SEND-ACTVW-SCREEN'],
        description="Specific Operations: What does SEND-ACTVW-SCREEN display?",
    ),
    BenchmarkQuery(
        query="How does SEND-ACTUP-SCREEN present account updates?",
        expected_files=['ACTUP', 'SCREEN'],
        expected_chunks=['SEND-ACTUP-SCREEN'],
        description="Specific Operations: How does SEND-ACTUP-SCREEN present account updates",
    ),
    BenchmarkQuery(
        query="How does SEND-CRDLI-SCREEN show the card list?",
        expected_files=['CRDLI', 'SCREEN'],
        expected_chunks=['SEND-CRDLI-SCREEN'],
        description="Specific Operations: How does SEND-CRDLI-SCREEN show the card list?",
    ),
    BenchmarkQuery(
        query="What does HANDLE-DB2-ERROR do on SQL failures?",
        expected_files=['ERROR', 'HANDLE'],
        expected_chunks=['HANDLE-DB2-ERROR'],
        description="Specific Operations: What does HANDLE-DB2-ERROR do on SQL failures?",
    ),

    # -- File Definitions --
    BenchmarkQuery(
        query="What files does the DALYREJS JCL handle?",
        expected_files=['DALYREJS'],
        expected_chunks=[],
        description="File Definitions: What files does the DALYREJS JCL handle?",
    ),
    BenchmarkQuery(
        query="How does the DISCGRP JCL delete disclosure groups?",
        expected_files=['DISCGRP'],
        expected_chunks=[],
        description="File Definitions: How does the DISCGRP JCL delete disclosure groups?",
    ),
    BenchmarkQuery(
        query="What does the TRANIDX JCL index?",
        expected_files=['TRANIDX'],
        expected_chunks=[],
        description="File Definitions: What does the TRANIDX JCL index?",
    ),
    BenchmarkQuery(
        query="How does the TRANTYPE JCL define transaction types?",
        expected_files=['TRANTYPE'],
        expected_chunks=[],
        description="File Definitions: How does the TRANTYPE JCL define transaction types",
    ),
    BenchmarkQuery(
        query="What does the TRANCATG JCL set up?",
        expected_files=['TRANCATG'],
        expected_chunks=[],
        description="File Definitions: What does the TRANCATG JCL set up?",
    ),
    BenchmarkQuery(
        query="How does COMBTRAN combine transaction data?",
        expected_files=['COMBTRAN'],
        expected_chunks=[],
        description="File Definitions: How does COMBTRAN combine transaction data?",
    ),
    BenchmarkQuery(
        query="What does the DUSRSECJ JCL do for user security?",
        expected_files=['DUSRSECJ'],
        expected_chunks=[],
        description="File Definitions: What does the DUSRSECJ JCL do for user security?",
    ),
    BenchmarkQuery(
        query="How does MNTTRDB2 maintain DB2 transaction data?",
        expected_files=['MNTTRDB2'],
        expected_chunks=[],
        description="File Definitions: How does MNTTRDB2 maintain DB2 transaction data?",
    ),
    BenchmarkQuery(
        query="What does the TCATBALF JCL process?",
        expected_files=['TCATBALF'],
        expected_chunks=[],
        description="File Definitions: What does the TCATBALF JCL process?",
    ),
]

