"""40 hand-curated benchmark queries spanning 20 categories.

Each query has manually verified expected_files and expected_chunks
for accurate relevance scoring.
"""

from benchmarks.config import BenchmarkQuery

QUERIES_CURATED: list[BenchmarkQuery] = [
    # ── User Management (2) ──
    BenchmarkQuery(
        query="What does COUSR00C do?",
        expected_files=["COUSR00C"],
        expected_chunks=["RECEIVE-USRLST-SCREEN", "SEND-USRLST-SCREEN"],
        description="Identify user list program",
    ),
    BenchmarkQuery(
        query="How does the sign-on screen COSGN00C work?",
        expected_files=["COSGN00C"],
        expected_chunks=["SEND-SIGNON-SCREEN", "MAIN-PARA"],
        description="Sign-on screen logic",
    ),
    # ── Account Processing (2) ──
    BenchmarkQuery(
        query="What does COACTUPC do for account updates?",
        expected_files=["COACTUPC"],
        expected_chunks=["9000-READ-ACCT"],
        description="Account update program",
    ),
    BenchmarkQuery(
        query="What is the account record structure in CVACT01Y?",
        expected_files=["CVACT01Y"],
        expected_chunks=[],
        description="Account record copybook lookup",
    ),
    # ── Card Processing (2) ──
    BenchmarkQuery(
        query="How are credit card numbers validated?",
        expected_files=["COCRDSLC", "COCRDUPC", "COCRDLIC"],
        expected_chunks=["EDIT-CARD"],
        description="Credit card validation logic",
    ),
    BenchmarkQuery(
        query="How does the card list BMS map COCRDLI work?",
        expected_files=["COCRDLI"],
        expected_chunks=["CCRDLIA"],
        description="Card list BMS map",
    ),
    # ── Transaction Processing (2) ──
    BenchmarkQuery(
        query="How does CBTRN01C process daily transactions?",
        expected_files=["CBTRN01C"],
        expected_chunks=["1000-DALYTRAN-GET-NEXT", "0000-DALYTRAN-OPEN"],
        description="Daily transaction batch processing",
    ),
    BenchmarkQuery(
        query="How are transaction amounts validated?",
        expected_files=["COTRN02C", "CBTRN02C"],
        expected_chunks=["VALIDATE"],
        description="Transaction amount validation",
    ),
    # ── Export/Import (2) ──
    BenchmarkQuery(
        query="How does CBEXPORT export customer data?",
        expected_files=["CBEXPORT"],
        expected_chunks=["2200-CREATE-CUSTOMER-EXP-REC", "2000-EXPORT-CUSTOMERS"],
        description="Customer data export",
    ),
    BenchmarkQuery(
        query="What validation does CBIMPORT perform on import?",
        expected_files=["CBIMPORT"],
        expected_chunks=["3000-VALIDATE-IMPORT", "0000-MAIN-PROCESSING"],
        description="Import validation logic",
    ),
    # ── Admin & Menu (2) ──
    BenchmarkQuery(
        query="How does the menu program COMEN01C work?",
        expected_files=["COMEN01C"],
        expected_chunks=["POPULATE-HEADER-INFO", "MAIN-PARA"],
        description="Main menu program",
    ),
    BenchmarkQuery(
        query="What admin options are in COADM02Y?",
        expected_files=["COADM02Y"],
        expected_chunks=["BUILD-MENU-OPTIONS"],
        description="Admin options copybook",
    ),
    # ── Date/Utility Programs (2) ──
    BenchmarkQuery(
        query="How does CSUTLDTC handle date and time?",
        expected_files=["CSUTLDTC"],
        expected_chunks=["A000-MAIN"],
        description="Date/time utility program",
    ),
    BenchmarkQuery(
        query="How is GENERATE-TIMESTAMP implemented?",
        expected_files=["CBEXPORT"],
        expected_chunks=["1050-GENERATE-TIMESTAMP"],
        description="Timestamp generation",
    ),
    # ── Copybook Structures (2) ──
    BenchmarkQuery(
        query="What is the customer record structure in CVCUS01Y?",
        expected_files=["CVCUS01Y"],
        expected_chunks=[],
        description="Customer record copybook",
    ),
    BenchmarkQuery(
        query="Explain the communication area COCOM01Y",
        expected_files=["COCOM01Y"],
        expected_chunks=["DFHCOMMAREA"],
        description="Communication area copybook",
    ),
    # ── BMS Maps & Screens (2) ──
    BenchmarkQuery(
        query="How is the sign-on BMS map COSGN00 structured?",
        expected_files=["COSGN00"],
        expected_chunks=["COSGN0A"],
        description="Sign-on BMS map structure",
    ),
    BenchmarkQuery(
        query="What does the card update map COCRDUP contain?",
        expected_files=["COCRDUP"],
        expected_chunks=["CCRDUPA"],
        description="Card update BMS map",
    ),
    # ── JCL Jobs (2) ──
    BenchmarkQuery(
        query="How does the POSTTRAN JCL post transactions?",
        expected_files=["POSTTRAN"],
        expected_chunks=["2000-POST-TRANSACTION"],
        description="Transaction posting JCL",
    ),
    BenchmarkQuery(
        query="What does the CREADB21 JCL create in DB2?",
        expected_files=["CREADB21"],
        expected_chunks=[],
        description="DB2 creation JCL",
    ),
    # ── CICS Operations (2) ──
    BenchmarkQuery(
        query="How is the COMMAREA used for inter-program communication?",
        expected_files=["COCOM01Y"],
        expected_chunks=["WS-COMMAREA"],
        description="COMMAREA inter-program communication",
    ),
    BenchmarkQuery(
        query="How does CICS RECEIVE capture user input?",
        expected_files=["COUSR00C", "COUSR01C", "COMEN01C"],
        expected_chunks=["RECEIVE"],
        description="CICS RECEIVE operations",
    ),
    # ── DB2 Operations (2) ──
    BenchmarkQuery(
        query="How is the SQLCA used for DB2 error handling?",
        expected_files=["CSDB2RPY"],
        expected_chunks=[],
        description="SQLCA DB2 error handling",
    ),
    BenchmarkQuery(
        query="What DB2 tables does CardDemo define?",
        expected_files=["DB2CREAT"],
        expected_chunks=[],
        description="DB2 table definitions",
    ),
    # ── VSAM File Operations (2) ──
    BenchmarkQuery(
        query="What VSAM file status codes are checked?",
        expected_files=["CBTRN02C", "CBTRN03C", "CBACT01C"],
        expected_chunks=["9910-DISPLAY-IO-STATUS"],
        description="VSAM file status code checks",
    ),
    BenchmarkQuery(
        query="How does STARTBR begin a VSAM browse?",
        expected_files=["COTRN00C", "COUSR00C"],
        expected_chunks=["STARTBR"],
        description="VSAM browse start operations",
    ),
    # ── Paragraph/Section Patterns (2) ──
    BenchmarkQuery(
        query="What does the MAIN-PARA entry point do?",
        expected_files=["COMEN01C", "COADM01C"],
        expected_chunks=["MAIN-PARA"],
        description="MAIN-PARA entry point",
    ),
    BenchmarkQuery(
        query="How does PROCESS-ENTER-KEY handle user input?",
        expected_files=["COTRN00C", "COSGN00C"],
        expected_chunks=["PROCESS-ENTER-KEY"],
        description="Enter key processing pattern",
    ),
    # ── Data Elements (2) ──
    BenchmarkQuery(
        query="What is WS-PGMNAME used for?",
        expected_files=[],
        expected_chunks=["DATA DIVISION"],
        description="WS-PGMNAME working storage variable",
    ),
    BenchmarkQuery(
        query="What is in the DFHCOMMAREA linkage section?",
        expected_files=["COCOM01Y"],
        expected_chunks=["DFHCOMMAREA"],
        description="DFHCOMMAREA linkage section",
    ),
    # ── Cross-Cutting Concerns (2) ──
    BenchmarkQuery(
        query="How does RETURN-TO-PREV-SCREEN navigate on errors?",
        expected_files=["COUSR02C", "COTRN02C"],
        expected_chunks=["RETURN-TO-PREV-SCREEN"],
        description="Screen return navigation pattern",
    ),
    BenchmarkQuery(
        query="How do programs pass data via the communication area?",
        expected_files=["COCOM01Y"],
        expected_chunks=["WS-COMMAREA"],
        description="Communication area data passing",
    ),
    # ── Business Domain (2) ──
    BenchmarkQuery(
        query="How does CardDemo handle interest calculation?",
        expected_files=["CBACT04C", "INTCALC"],
        expected_chunks=["1300-COMPUTE-INTEREST"],
        description="Interest calculation logic",
    ),
    BenchmarkQuery(
        query="How are transaction categories and types classified?",
        expected_files=["CVTRA03Y", "CVTRA04Y"],
        expected_chunks=[],
        description="Transaction category/type classification",
    ),
    # ── Architecture & Integration (2) ──
    BenchmarkQuery(
        query="What batch vs online programs exist?",
        expected_files=["CBTRN01C", "CBACT01C"],
        expected_chunks=[],
        description="Batch vs online program inventory",
    ),
    BenchmarkQuery(
        query="How do copybooks reduce code duplication?",
        expected_files=["COCOM01Y", "CSUSR01Y"],
        expected_chunks=[],
        description="Copybook reuse patterns",
    ),
    # ── Specific Operations (2) ──
    BenchmarkQuery(
        query="How does LOOKUP-XREF perform cross-reference lookups?",
        expected_files=["CBACT03C", "CVACT03Y"],
        expected_chunks=["XREF"],
        description="Cross-reference lookup operation",
    ),
    BenchmarkQuery(
        query="What does HANDLE-DB2-ERROR do on SQL failures?",
        expected_files=["COPAUS2C"],
        expected_chunks=["FRAUD-UPDATE"],
        description="DB2 error handler",
    ),
    # ── File Definitions (2) ──
    BenchmarkQuery(
        query="How does COMBTRAN combine transaction data?",
        expected_files=["COMBTRAN"],
        expected_chunks=[],
        description="Transaction data combining JCL",
    ),
    BenchmarkQuery(
        query="What does the DUSRSECJ JCL do for user security?",
        expected_files=["DUSRSECJ"],
        expected_chunks=[],
        description="User security file JCL",
    ),
]
