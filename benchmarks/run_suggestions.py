"""Run all 200 suggestion queries against the best index and capture raw results.

Usage:
    python -u benchmarks/run_suggestions.py
"""

import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone, SearchQuery

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from legacylens.config import settings

INDEX_NAME = "legacylens-bench-llama-1024-paragraph"
NAMESPACE = "carddemo"
TOP_K = 10
RESULTS_DIR = Path(__file__).resolve().parent / "results"

# ── 200 curated suggestion queries, organized by category ──
SUGGESTIONS = [
    # ── User Management ──
    ("User Management", "What does COUSR00C do?"),
    ("User Management", "How does the user list screen work in COUSR00C?"),
    ("User Management", "How does COUSR01C handle user inquiry?"),
    ("User Management", "Explain the user add logic in COUSR02C"),
    ("User Management", "How does COUSR03C update user records?"),
    ("User Management", "How is the USRSEC user security file accessed?"),
    ("User Management", "What is the user authentication flow in CardDemo?"),
    ("User Management", "How are user roles and permissions managed?"),
    ("User Management", "How does the sign-on screen COSGN00C work?"),
    ("User Management", "What validation happens during user login?"),
    # ── Account Processing ──
    ("Account Processing", "What does COACTUPC do for account updates?"),
    ("Account Processing", "How does COACTVWC display account activity?"),
    ("Account Processing", "What is the account inquiry logic in CBACT01C?"),
    ("Account Processing", "How does CBACT02C add new accounts?"),
    ("Account Processing", "How does CBACT03C modify account records?"),
    ("Account Processing", "Explain the DB2 account delete in CBACT04C"),
    ("Account Processing", "How are account balances calculated?"),
    ("Account Processing", "How is the account cross-reference file used?"),
    ("Account Processing", "What is the account record structure in CVACT01Y?"),
    ("Account Processing", "How does COACCT01 handle VSAM account operations?"),
    # ── Card Processing ──
    ("Card Processing", "What does COCRDLIC do for card listing?"),
    ("Card Processing", "How does the card selection screen COCRDSLC work?"),
    ("Card Processing", "Explain the card update logic in COCRDUPC"),
    ("Card Processing", "How are credit card numbers validated?"),
    ("Card Processing", "What is the card record structure in CVACT02Y?"),
    ("Card Processing", "How is the card cross-reference CVACT03Y used?"),
    ("Card Processing", "What card work areas are defined in CVCRD01Y?"),
    ("Card Processing", "How does CardDemo handle card activation?"),
    ("Card Processing", "How does the card list BMS map COCRDLI work?"),
    ("Card Processing", "What card data is stored in CARDFILE?"),
    # ── Transaction Processing ──
    ("Transaction Processing", "How does CBTRN01C process daily transactions?"),
    ("Transaction Processing", "Explain the DB2 transaction handling in CBTRN02C"),
    ("Transaction Processing", "What does the batch transaction program CBTRN03C do?"),
    ("Transaction Processing", "How does COTRN00C handle transaction inquiry?"),
    ("Transaction Processing", "Explain the transaction add flow in COTRN01C"),
    ("Transaction Processing", "How does COTRN02C display transaction details?"),
    ("Transaction Processing", "What does COTRTLIC do for transaction type listing?"),
    ("Transaction Processing", "How does COTRTUPC update transactions via DB2?"),
    ("Transaction Processing", "What is the transaction category balance in CVTRA01Y?"),
    ("Transaction Processing", "What transaction types are defined in CVTRA03Y?"),
    ("Transaction Processing", "How is the daily transaction file DALYTRAN used?"),
    ("Transaction Processing", "What is the transaction record structure in CVTRA05Y?"),
    ("Transaction Processing", "Explain the transaction posting logic"),
    ("Transaction Processing", "How are transaction amounts validated?"),
    ("Transaction Processing", "How does transaction reversal work?"),
    # ── Export/Import ──
    ("Export/Import", "How does CBEXPORT export customer data?"),
    ("Export/Import", "What account export format does CBEXPORT use?"),
    ("Export/Import", "How does CBEXPORT handle cross-reference exports?"),
    ("Export/Import", "Explain the transaction export in CBEXPORT"),
    ("Export/Import", "How does CBEXPORT export card records?"),
    ("Export/Import", "What does the CBIMPORT import utility do?"),
    ("Export/Import", "How does export file creation work?"),
    ("Export/Import", "What validation does CBIMPORT perform on import?"),
    ("Export/Import", "How are export records formatted?"),
    ("Export/Import", "What is the CREATE-CUSTOMER-EXP-REC paragraph?"),
    # ── Admin & Menu ──
    ("Admin & Menu", "What does the admin menu COADM01C do?"),
    ("Admin & Menu", "How does the menu program COMEN01C work?"),
    ("Admin & Menu", "Explain the bill display logic in COBIL00C"),
    ("Admin & Menu", "How does CORPT00C generate reports?"),
    ("Admin & Menu", "What is the admin transaction CA00?"),
    ("Admin & Menu", "What admin options are in COADM02Y?"),
    ("Admin & Menu", "How does the admin menu BMS screen work?"),
    ("Admin & Menu", "What functions are available from the main menu?"),
    ("Admin & Menu", "How does navigation between screens work?"),
    ("Admin & Menu", "What is the COBSWAIT wait command used for?"),
    # ── Date/Utility Programs ──
    ("Date/Utility Programs", "How does CSUTLDTC handle date and time?"),
    ("Date/Utility Programs", "What does the VSAM date handler CODATE01 do?"),
    ("Date/Utility Programs", "How does CODATECN perform date conversion?"),
    ("Date/Utility Programs", "What date utilities are in CSDAT01Y?"),
    ("Date/Utility Programs", "How does CSUTLDWY format dates?"),
    ("Date/Utility Programs", "What string formatting does CSSTRPFY provide?"),
    ("Date/Utility Programs", "How does CSSETATY set screen attributes?"),
    ("Date/Utility Programs", "What lookup codes are in CSLKPCDY?"),
    ("Date/Utility Programs", "How is GENERATE-TIMESTAMP implemented?"),
    ("Date/Utility Programs", "What user utilities does CSUSR01Y provide?"),
    # ── Copybook Structures ──
    ("Copybook Structures", "What is the customer record structure in CVCUS01Y?"),
    ("Copybook Structures", "Explain the communication area COCOM01Y"),
    ("Copybook Structures", "What fields are in the account record CVACT01Y?"),
    ("Copybook Structures", "How is the transaction category type CVTRA04Y structured?"),
    ("Copybook Structures", "What is in the reporting copybook CVTRA07Y?"),
    ("Copybook Structures", "How is the disclosure group structure CVTRA02Y used?"),
    ("Copybook Structures", "What message handling does CSMSG01Y provide?"),
    ("Copybook Structures", "What message arrays are in CSMSG02Y?"),
    ("Copybook Structures", "What DB2 working storage is in CSDB2RWY?"),
    ("Copybook Structures", "What DB2 procedures are in CSDB2RPY?"),
    # ── BMS Maps & Screens ──
    ("BMS Maps & Screens", "How is the sign-on BMS map COSGN00 structured?"),
    ("BMS Maps & Screens", "What fields does the account view map COACTVW have?"),
    ("BMS Maps & Screens", "How is the transaction inquiry map COTRN00 laid out?"),
    ("BMS Maps & Screens", "What does the transaction add map COTRN01 contain?"),
    ("BMS Maps & Screens", "How is the report display map CORPT00 structured?"),
    ("BMS Maps & Screens", "What fields are on the user list map COUSR00?"),
    ("BMS Maps & Screens", "How is the authorization screen COPAU00 designed?"),
    ("BMS Maps & Screens", "What does the card update map COCRDUP contain?"),
    ("BMS Maps & Screens", "How are BMS maps defined with DFHMSD and DFHMDI?"),
    ("BMS Maps & Screens", "What screen attributes are used in the BMS maps?"),
    # ── JCL Jobs ──
    ("JCL Jobs", "What does the ACCTFILE JCL job define?"),
    ("JCL Jobs", "How does the CARDFILE JCL set up card data?"),
    ("JCL Jobs", "What does the CUSTFILE JCL job do?"),
    ("JCL Jobs", "How does the DEFGDGB JCL define GDG backups?"),
    ("JCL Jobs", "What does the XREFFILE JCL create?"),
    ("JCL Jobs", "How does the TRANFILE JCL define transaction files?"),
    ("JCL Jobs", "What does the READACCT JCL job do?"),
    ("JCL Jobs", "How does the CLOSEFIL JCL close all files?"),
    ("JCL Jobs", "What does the OPENFIL JCL job open?"),
    ("JCL Jobs", "How does the TRANREPT JCL generate reports?"),
    ("JCL Jobs", "What does the CBEXPORT JCL job execute?"),
    ("JCL Jobs", "How does the CBIMPORT JCL run imports?"),
    ("JCL Jobs", "What does INTCALC calculate?"),
    ("JCL Jobs", "How does the POSTTRAN JCL post transactions?"),
    ("JCL Jobs", "What does the CREADB21 JCL create in DB2?"),
    # ── CICS Operations ──
    ("CICS Operations", "How does CardDemo use CICS LINK for program calls?"),
    ("CICS Operations", "What EXEC CICS commands are most common?"),
    ("CICS Operations", "How is the COMMAREA used for inter-program communication?"),
    ("CICS Operations", "How do CICS screen SEND operations work?"),
    ("CICS Operations", "How does CICS RECEIVE capture user input?"),
    ("CICS Operations", "What CICS file control operations are used?"),
    ("CICS Operations", "How are CICS response codes handled?"),
    ("CICS Operations", "What CICS XCTL transfers exist between programs?"),
    ("CICS Operations", "How does CICS exception handling work?"),
    ("CICS Operations", "What transaction IDs (TRANIDs) are defined?"),
    # ── DB2 Operations ──
    ("DB2 Operations", "How does CardDemo use EXEC SQL statements?"),
    ("DB2 Operations", "How is the SQLCA used for DB2 error handling?"),
    ("DB2 Operations", "What DB2 cursors are declared in the programs?"),
    ("DB2 Operations", "How are DB2 SELECT queries structured?"),
    ("DB2 Operations", "What DB2 INSERT operations exist?"),
    ("DB2 Operations", "How do DB2 UPDATE statements work in CardDemo?"),
    ("DB2 Operations", "How does DB2 COMMIT and ROLLBACK work?"),
    ("DB2 Operations", "What WHENEVER statements handle DB2 errors?"),
    ("DB2 Operations", "How is the NOT FOUND condition handled in DB2?"),
    ("DB2 Operations", "What DB2 tables does CardDemo define?"),
    # ── VSAM File Operations ──
    ("VSAM File Operations", "How does CardDemo use VSAM KSDS files?"),
    ("VSAM File Operations", "What VSAM file status codes are checked?"),
    ("VSAM File Operations", "How does STARTBR begin a VSAM browse?"),
    ("VSAM File Operations", "How does READNEXT do sequential VSAM reads?"),
    ("VSAM File Operations", "How does READPREV read VSAM records backward?"),
    ("VSAM File Operations", "How does ENDBR end a VSAM browse?"),
    ("VSAM File Operations", "What VSAM error handling patterns exist?"),
    ("VSAM File Operations", "How does READ-CUSTOMER-RECORD fetch customer data?"),
    ("VSAM File Operations", "How does READ-ACCOUNT-RECORD work?"),
    ("VSAM File Operations", "How does READ-CARD-RECORD retrieve card data?"),
    # ── Paragraph/Section Patterns ──
    ("Paragraph/Section Patterns", "What does the MAIN-PARA entry point do?"),
    ("Paragraph/Section Patterns", "How does 0000-MAIN-PROCESSING work in batch programs?"),
    ("Paragraph/Section Patterns", "What happens in the 1000-INITIALIZE paragraph?"),
    ("Paragraph/Section Patterns", "How does PROCESS-ENTER-KEY handle user input?"),
    ("Paragraph/Section Patterns", "How do PF key handlers like PROCESS-PF7-KEY work?"),
    ("Paragraph/Section Patterns", "What does POPULATE-USER-DATA load?"),
    ("Paragraph/Section Patterns", "How does POPULATE-HEADER-INFO set screen headers?"),
    ("Paragraph/Section Patterns", "What does INITIALIZE-USER-DATA reset?"),
    ("Paragraph/Section Patterns", "How does Z-ABEND-PROGRAM handle abnormal ends?"),
    ("Paragraph/Section Patterns", "What does Z-DISPLAY-IO-STATUS show?"),
    # ── Data Elements ──
    ("Data Elements", "What is WS-PGMNAME used for?"),
    ("Data Elements", "How is WS-TRANID set in each program?"),
    ("Data Elements", "What does WS-MESSAGE contain?"),
    ("Data Elements", "How are WS-RESP-CD and WS-REAS-CD used?"),
    ("Data Elements", "What record counters track in WS-REC-COUNT?"),
    ("Data Elements", "How is WS-ERR-FLG used for error detection?"),
    ("Data Elements", "How does WS-PAGE-NUM control pagination?"),
    ("Data Elements", "What OCCURS clause arrays exist in the programs?"),
    ("Data Elements", "How are level 88 conditions used in CardDemo?"),
    ("Data Elements", "What is in the DFHCOMMAREA linkage section?"),
    # ── Cross-Cutting Concerns ──
    ("Cross-Cutting Concerns", "How does error handling work across COBOL programs?"),
    ("Cross-Cutting Concerns", "What COPY statements are shared between programs?"),
    ("Cross-Cutting Concerns", "How does RETURN-TO-PREV-SCREEN navigate on errors?"),
    ("Cross-Cutting Concerns", "What PERFORM targets are common across programs?"),
    ("Cross-Cutting Concerns", "How does page-forward and page-backward scrolling work?"),
    ("Cross-Cutting Concerns", "What data validation patterns are reused?"),
    ("Cross-Cutting Concerns", "How do programs pass data via the communication area?"),
    ("Cross-Cutting Concerns", "What naming conventions do the COBOL programs follow?"),
    ("Cross-Cutting Concerns", "How are WORKING-STORAGE sections organized?"),
    ("Cross-Cutting Concerns", "What is the overall program call hierarchy?"),
    # ── Business Domain ──
    ("Business Domain", "What is the end-to-end credit card transaction flow?"),
    ("Business Domain", "How does CardDemo handle interest calculation?"),
    ("Business Domain", "What reporting capabilities does the application have?"),
    ("Business Domain", "How does the daily transaction batch cycle work?"),
    ("Business Domain", "What reconciliation processes exist?"),
    ("Business Domain", "How are transaction categories and types classified?"),
    ("Business Domain", "What is the customer-account-card relationship?"),
    ("Business Domain", "How does CardDemo handle regulatory reporting?"),
    ("Business Domain", "What audit trail capabilities exist?"),
    ("Business Domain", "How does the application handle exception processing?"),
    # ── Architecture & Integration ──
    ("Architecture & Integration", "What is the overall architecture of the CardDemo system?"),
    ("Architecture & Integration", "How many COBOL programs make up CardDemo?"),
    ("Architecture & Integration", "What batch vs online programs exist?"),
    ("Architecture & Integration", "How do online CICS programs differ from batch programs?"),
    ("Architecture & Integration", "What is the relationship between BMS maps and COBOL programs?"),
    ("Architecture & Integration", "How does the ENVIRONMENT DIVISION configure file access?"),
    ("Architecture & Integration", "What FILE SECTION definitions exist in the DATA DIVISION?"),
    ("Architecture & Integration", "How is the PROCEDURE DIVISION structured across programs?"),
    ("Architecture & Integration", "What IDENTIFICATION DIVISION metadata is recorded?"),
    ("Architecture & Integration", "How do copybooks reduce code duplication?"),
    # ── Specific Operations ──
    ("Specific Operations", "How does LOOKUP-XREF perform cross-reference lookups?"),
    ("Specific Operations", "What does CREATE-ACCOUNT-EXP-REC format for export?"),
    ("Specific Operations", "How does CREATE-XREF-EXPORT-RECORD work?"),
    ("Specific Operations", "What does CREATE-CARD-EXPORT-RECORD output?"),
    ("Specific Operations", "How does SEND-USRLST-SCREEN transmit the user list?"),
    ("Specific Operations", "How does RECEIVE-USRLST-SCREEN capture user input?"),
    ("Specific Operations", "What does SEND-ACTVW-SCREEN display?"),
    ("Specific Operations", "How does SEND-ACTUP-SCREEN present account updates?"),
    ("Specific Operations", "How does SEND-CRDLI-SCREEN show the card list?"),
    ("Specific Operations", "What does HANDLE-DB2-ERROR do on SQL failures?"),
    # ── File Definitions ──
    ("File Definitions", "What files does the DALYREJS JCL handle?"),
    ("File Definitions", "How does the DISCGRP JCL delete disclosure groups?"),
    ("File Definitions", "What does the TRANIDX JCL index?"),
    ("File Definitions", "How does the TRANTYPE JCL define transaction types?"),
    ("File Definitions", "What does the TRANCATG JCL set up?"),
    ("File Definitions", "How does COMBTRAN combine transaction data?"),
    ("File Definitions", "What does the DUSRSECJ JCL do for user security?"),
    ("File Definitions", "How does MNTTRDB2 maintain DB2 transaction data?"),
    ("File Definitions", "What does the TCATBALF JCL process?"),
]

assert len(SUGGESTIONS) == 209, f"Expected 209 suggestions, got {len(SUGGESTIONS)}"


def run_suggestions():
    if not settings.pinecone_api_key:
        print("ERROR: PINECONE_API_KEY must be set")
        sys.exit(1)

    pc = Pinecone(api_key=settings.pinecone_api_key)

    # Verify index exists
    existing = [idx.name for idx in pc.list_indexes()]
    if INDEX_NAME not in existing:
        print(f"ERROR: Index {INDEX_NAME} not found. Available: {existing}")
        sys.exit(1)

    index = pc.Index(INDEX_NAME)
    all_results = []

    print(f"Running {len(SUGGESTIONS)} suggestion queries against {INDEX_NAME} (top_k={TOP_K})")
    print("=" * 100)

    for i, (category, query_text) in enumerate(SUGGESTIONS, 1):
        try:
            start = time.perf_counter()
            response = index.search_records(
                namespace=NAMESPACE,
                query=SearchQuery(
                    inputs={"text": query_text},
                    top_k=TOP_K,
                ),
            )
            elapsed = time.perf_counter() - start

            hits = []
            for hit in response.result.hits:
                fields = hit.fields or {}
                hits.append({
                    "id": hit.id,
                    "score": hit.score if hit.score is not None else 0.0,
                    "file_name": fields.get("file_name", ""),
                    "name": fields.get("name", ""),
                    "chunk_type": fields.get("chunk_type", ""),
                    "file_type": fields.get("file_type", ""),
                })

            result = {
                "index": i,
                "category": category,
                "query": query_text,
                "elapsed_s": round(elapsed, 3),
                "hit_count": len(hits),
                "top_results": hits[:5],
                "all_results": hits,
            }
            all_results.append(result)

            # Print summary: query + top-3 file hits
            top3 = hits[:3]
            top3_summary = " | ".join(
                f"{h['file_name']}:{h['name']} ({h['score'] or 0:.3f})"
                for h in top3
            )
            print(f"[{i:3d}/{len(SUGGESTIONS)}] [{category}] {query_text}")
            print(f"           -> {top3_summary}")

        except Exception as e:
            print(f"[{i:3d}/{len(SUGGESTIONS)}] ERROR: {e}")
            all_results.append({
                "index": i,
                "category": category,
                "query": query_text,
                "error": str(e),
            })

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / "suggestions_raw.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved {len(all_results)} results to {output_path}")

    # Category summary
    print("\n" + "=" * 100)
    print("CATEGORY SUMMARY")
    print("=" * 100)
    categories = {}
    for r in all_results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    for cat, results in categories.items():
        avg_hits = sum(r.get("hit_count", 0) for r in results) / len(results)
        avg_score = 0
        score_count = 0
        for r in results:
            if r.get("top_results"):
                avg_score += r["top_results"][0]["score"] or 0
                score_count += 1
        avg_top_score = avg_score / score_count if score_count else 0
        print(f"  {cat:<30} {len(results):2d} queries | avg hits: {avg_hits:.1f} | avg top score: {avg_top_score:.3f}")


if __name__ == "__main__":
    run_suggestions()
