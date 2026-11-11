"""Deterministic demonstration fixtures.

EVERYTHING IN THIS FILE IS FICTIONAL. Places (State X, the Republic of Aster…), people
(Candidate A/B/C), organisations, bills, filings and statistics are invented to exercise
SILO's features. Identifiers use a DEMO- prefix and records have no external URLs so they
cannot be mistaken for authentic government records.
"""
from datetime import date

DEMO_NOTE = "Fictional demonstration record created for the SILO prototype. Not a real government record."
D = "(demonstration record)"

PUBLISHERS = [
    {
        "slug": "riverside-daily-ledger", "name": "Riverside Daily Ledger",
        "legal_entity": "Riverside Ledger Publishing LLC", "parent_organization": "Northfield Media Holdings, Inc.",
        "ownership_type": "corporate",
        "description": "Fictional regional daily newspaper serving State X's capital region.",
        "relationships": [
            {"related_entity": "Northfield Media Holdings, Inc.", "relationship_type": "owner",
             "description": "Owns 100% of Riverside Ledger Publishing LLC.", "start_date": date(2019, 7, 1),
             "source_label": f"State X Secretary of State business filing DEMO-BF-88213 {D}"},
            {"related_entity": "Northfield Capital Group", "relationship_type": "parent",
             "description": "Private investment firm that holds a controlling stake in Northfield Media Holdings.",
             "start_date": date(2017, 3, 15), "source_label": f"Northfield Media Holdings annual statement 2025 {D}"},
            {"related_entity": "Northfield Capital Group Employee PAC", "relationship_type": "political_spending",
             "description": "The parent firm's employee PAC reported contributions of $7,500 to each of Candidate A's and Candidate B's committees in 2026-Q2.",
             "amount_usd": 15000, "start_date": date(2026, 5, 2),
             "source_label": f"Committee report DEMO-FIL-P03-Q2 {D}"},
            {"related_entity": "Editorial decisions", "relationship_type": "editorial_control",
             "description": "No public record establishes that the owner or parent firm directs news coverage. Ownership alone does not establish editorial influence.",
             "established": False, "source_label": "No supporting record found"},
        ],
    },
    {
        "slug": "metro-signal", "name": "Metro Signal",
        "legal_entity": "Metro Signal Newsroom, Inc.", "parent_organization": None,
        "ownership_type": "nonprofit",
        "description": "Fictional nonprofit newsroom (tax-exempt public charity) covering State X government.",
        "relationships": [
            {"related_entity": "Calder Valley Community Foundation", "relationship_type": "grant",
             "description": "General operating grant reported on the newsroom's annual information return.",
             "amount_usd": 400000, "start_date": date(2025, 1, 1), "end_date": date(2025, 12, 31),
             "source_label": f"Annual information return (Form 990-style), tax year 2025, Schedule B summary {D}"},
            {"related_entity": "Individual donors", "relationship_type": "funder",
             "description": "Individual donations accounted for 62% of reported 2025 revenue.",
             "start_date": date(2025, 1, 1), "end_date": date(2025, 12, 31),
             "source_label": f"Annual information return, tax year 2025, Part VIII {D}"},
            {"related_entity": "Board of directors", "relationship_type": "board",
             "description": "Nine-member volunteer board; two members are former State X agency employees.",
             "start_date": date(2026, 1, 1), "source_label": f"Metro Signal governance page snapshot {D}"},
        ],
    },
    {
        "slug": "civic-wire-cooperative", "name": "Civic Wire Cooperative",
        "legal_entity": "Civic Wire Cooperative Association", "parent_organization": None,
        "ownership_type": "cooperative",
        "description": "Fictional reader-owned news cooperative with about 4,100 member-owners.",
        "relationships": [
            {"related_entity": "Member-owners (about 4,100)", "relationship_type": "owner",
             "description": "Each member holds one equal share and one vote in board elections.",
             "start_date": date(2021, 9, 1), "source_label": f"State X cooperative registration DEMO-CO-2219 {D}"},
            {"related_entity": "Major institutional funders", "relationship_type": "funder",
             "description": "The cooperative reports no single funder above 5% of revenue. Individual funder names are not disclosed, so specific relationships are not established.",
             "established": False, "start_date": date(2025, 1, 1),
             "source_label": f"Cooperative annual report 2025 {D}"},
        ],
    },
]

EVIDENCE = [
    {"record_key": "DEMO-DOL-2026-Q3", "title": "Quarterly Labor Force Summary, Q3 2026", "organization": "State X Department of Labor",
     "source_type": "official_statistic", "record_date": date(2026, 10, 15), "entities": ["State X", "unemployment", "jobless"],
     "content": "State X's seasonally adjusted unemployment rate averaged 4.1 percent in the third quarter of 2026. The monthly estimate for September 2026 was 3.9 percent. In the third quarter of 2025 the quarterly average was 4.6 percent. Estimates are based on the State X household survey and are subject to revision."},
    {"record_key": "DEMO-DOL-CES-2026-09", "title": "Establishment Employment Survey, September 2026", "organization": "State X Department of Labor",
     "source_type": "official_statistic", "record_date": date(2026, 10, 15), "entities": ["State X", "manufacturing"],
     "content": "Manufacturing employment in State X was 212,400 in September 2026, up 4.0 percent from September 2025 (204,200). Total nonfarm employment rose 1.8 percent over the same period."},
    {"record_key": "DEMO-GOV-PR-2026-10-20", "title": "Transcript: Governor's press conference on the economy, October 20, 2026", "organization": "Office of the Governor of State X",
     "source_type": "official_transcript", "record_date": date(2026, 10, 20), "entities": ["Governor", "State X"],
     "content": "THE GOVERNOR: This is a historic turnaround, and every family in State X is feeling it. Our unemployment rate fell to 3.9 percent. Manufacturing employment grew 40 percent. [Office clarification issued October 21: the figure referred to the 4.0 percent annual increase.]"},
    {"record_key": "DEMO-COMP-FY2026", "title": "Preliminary Fiscal Year 2026 Closing Report", "organization": "State X Office of the Comptroller",
     "source_type": "primary_record", "record_date": date(2026, 8, 30), "entities": ["State X", "budget", "surplus"],
     "content": "The State X general fund closed fiscal year 2026 with a projected surplus of $1.2 billion. This figure is preliminary and unaudited; the audited statement is scheduled for publication in January 2027. Approximately $700 million of the projected surplus reflects one-time revenue."},
    {"record_key": "DEMO-HFA-RENT-2026", "title": "Capital Region Rent Survey 2026", "organization": "State X Housing Finance Agency",
     "source_type": "official_statistic", "record_date": date(2026, 6, 1), "entities": ["State X Housing Finance Agency", "rent"],
     "content": "Median asking rent in the capital region rose from $1,410 in 2024 to $1,537 in 2026, an increase of 9.0 percent. Median hourly wages in the region rose 5.1 percent over the same period."},
    {"record_key": "DEMO-RC-2026-041", "title": "Roll Call DEMO-RC-2026-041: DEMO-SB-12 final passage", "organization": "State X Senate Clerk",
     "source_type": "primary_record", "record_date": date(2026, 4, 14), "entities": ["River Restoration Act", "DEMO-SB-12", "State X Senate"],
     "content": "On April 14, 2026 the State X Senate voted on final passage of DEMO-SB-12, the River Restoration Act. Result: passed, 31 yeas, 19 nays. Candidate A (District 4) voted yea. Candidate B (District 11) voted nay."},
    {"record_key": "DEMO-SB-12-TEXT", "title": "DEMO-SB-12 River Restoration Act — enrolled text, Section 3", "organization": "State X Legislature",
     "source_type": "primary_record", "record_date": date(2026, 4, 14), "entities": ["River Restoration Act", "DEMO-SB-12", "Calder River"],
     "content": "Section 3. Appropriations. There is authorized $85,000,000 over fiscal years 2027 through 2031, of which $60,000,000 is for wastewater treatment upgrades and $25,000,000 is for wetland restoration along the Calder River."},
    {"record_key": "DEMO-SEN-TR-2026-04-14", "title": "Transcript: State X Senate floor debate on DEMO-SB-12, April 14, 2026", "organization": "State X Senate Clerk",
     "source_type": "official_transcript", "record_date": date(2026, 4, 14), "entities": ["Candidate A", "Candidate B", "River Restoration Act"],
     "content": "CANDIDATE A: This bill is a lifeline for every family on the river. CANDIDATE B: I support cleaner water. But this is a reckless spending spree that taxpayers cannot afford, and it duplicates the Clean Water Fund."},
    {"record_key": "DEMO-DEQ-PHOS-2025", "title": "Calder River Water Quality Monitoring Report, 2016–2025", "organization": "State X Department of Environmental Quality",
     "source_type": "official_statistic", "record_date": date(2026, 2, 1), "entities": ["Calder River", "phosphorus", "river"],
     "content": "Between 2016 and 2025, mean phosphorus concentrations increased at 3 of 7 monitoring stations, by between 30 and 110 percent. Concentrations at the remaining 4 stations showed no statistically significant change."},
    {"record_key": "DEMO-CWF-2025", "title": "Clean Water Fund Annual Report, Fiscal Year 2025", "organization": "State X Department of Environmental Quality",
     "source_type": "primary_record", "record_date": date(2025, 12, 1), "entities": ["Clean Water Fund", "State X"],
     "content": "The Clean Water Fund spent $40 million in fiscal year 2025, of which $31 million funded wastewater treatment projects and $9 million funded drinking-water systems. The fund financed no wetland restoration projects."},
    {"record_key": "DEMO-DOH-LIC-2026", "title": "Health Facility Licensure Registry extract, June 2026", "organization": "State X Department of Health",
     "source_type": "primary_record", "record_date": date(2026, 6, 30), "entities": ["clinic", "clinics", "Northfork", "Pine Hollow", "Tessaly"],
     "content": "Since January 2023, six rural clinic licenses were surrendered: four facilities closed and two were consolidated into regional health centers. As of June 30, 2026, no licensed walk-in clinic operates in Northfork, Pine Hollow or Tessaly counties."},
    {"record_key": "DEMO-RC-2026-058", "title": "Roll Call DEMO-RC-2026-058: DEMO-HB-40 final passage (Senate)", "organization": "State X Senate Clerk",
     "source_type": "primary_record", "record_date": date(2026, 5, 12), "entities": ["Rural Clinic Stabilization Fund", "DEMO-HB-40", "State X Legislature"],
     "content": "On May 12, 2026 the State X Senate passed DEMO-HB-40, appropriating $12 million to the Rural Clinic Stabilization Fund, 33 yeas to 17 nays. The House had passed the bill on May 5, 2026. The Governor signed it on May 20, 2026."},
    {"record_key": "DEMO-CSMA-2026-H1", "title": "Corvan Strait Traffic Statistics, First Half 2026", "organization": "Corvan Strait Maritime Authority (fictional)",
     "source_type": "official_statistic", "record_date": date(2026, 7, 31), "entities": ["Corvan Strait"],
     "content": "Container transits through the Corvan Strait totaled 41,200 in the first half of 2026, down 18 percent from 50,250 in the first half of 2025."},
    {"record_key": "DEMO-PORT-AR-2025", "title": "Port of State X Annual Report 2025", "organization": "Port of State X Authority",
     "source_type": "primary_record", "record_date": date(2026, 3, 1), "entities": ["Port of State X"],
     "content": "The Port of State X handled 11.6 percent of the region's strait-bound container cargo in 2025, measured in twenty-foot equivalent units."},
    {"record_key": "DEMO-ACCORD-2009", "title": "Corvan Fisheries Accord (2009), Article 7", "organization": "Council of Nations Treaty Registry (fictional)",
     "source_type": "primary_record", "record_date": date(2009, 3, 2), "entities": ["Aster", "Valdoria", "Fisheries Accord"],
     "content": "Article 7. Disputes concerning catch quotas shall be referred to the joint commission and, failing agreement within 180 days, to binding arbitration. No arbitration finding regarding the 2026 complaint had been issued as of October 2026."},
    {"record_key": "DEMO-VAL-MFA-2026-09", "title": "Statement of the Valdorian Foreign Ministry, September 4, 2026", "organization": "Federation of Valdoria Ministry of Foreign Affairs (fictional)",
     "source_type": "official_transcript", "record_date": date(2026, 9, 4), "entities": ["Valdoria"],
     "content": "The Ministry rejects the accusation as baseless and provocative and remains ready to resume talks under the 2024 joint inspection framework."},
]

# Curated annotations: (substring of the claim sentence, evidence record_key, relationship, explanation)
ARTICLES = [
    {
        "slug": "state-x-jobless-rate-falls", "publisher": "riverside-daily-ledger", "article_type": "news",
        "title": "State X jobless rate falls as Governor calls recovery “historic”",
        "dek": "New labor figures show improvement, but some of the numbers cited at Tuesday's press conference need a closer look.",
        "author": "Staff reporter", "published_at": "2026-10-21T14:00:00Z", "primary_topic": "Economy & labor",
        "body": (
            "State X's unemployment rate fell to 3.9 percent in the third quarter of 2026, the Governor said on Tuesday. "
            "A year earlier, the rate stood at 4.6 percent.\n\n"
            "“This is a historic turnaround, and every family in State X is feeling it,” the Governor said.\n\n"
            "Manufacturing employment grew 40 percent, according to the Governor's office. "
            "The state also ended the fiscal year with a $1.2 billion budget surplus.\n\n"
            "Experts say the recovery is the best in the nation. "
            "Median rent in the capital region rose 9 percent between 2024 and 2026, according to the State X Housing Finance Agency. "
            "The Governor's office did not respond to a request for comment about wage growth."
        ),
        "annotations": [
            ("unemployment rate fell to 3.9 percent", "DEMO-DOL-2026-Q3", "partially_supports",
             "The record shows a third-quarter average of 4.1 percent. The 3.9 percent figure matches the September monthly estimate, not the quarterly rate the sentence describes."),
            ("A year earlier, the rate stood at 4.6 percent", "DEMO-DOL-2026-Q3", "supports",
             "The record lists a 4.6 percent quarterly average for the third quarter of 2025."),
            ("This is a historic turnaround", "DEMO-GOV-PR-2026-10-20", "supports",
             "The quotation appears verbatim in the official transcript. This verifies that the words were said, not that the description is accurate."),
            ("Manufacturing employment grew 40 percent", "DEMO-DOL-CES-2026-09", "contradicts",
             "The employment survey shows a 4.0 percent annual increase, not 40 percent. The Governor's office later clarified the figure (see transcript record)."),
            ("Manufacturing employment grew 40 percent", "DEMO-GOV-PR-2026-10-20", "provides_context",
             "The transcript shows the 40 percent figure was stated at the press conference and clarified the next day as 4.0 percent."),
            ("$1.2 billion budget surplus", "DEMO-COMP-FY2026", "partially_supports",
             "The Comptroller reports a $1.2 billion surplus, but labels it projected and unaudited, and notes about $700 million is one-time revenue."),
            ("Median rent in the capital region rose 9 percent", "DEMO-HFA-RENT-2026", "supports",
             "The survey reports a 9.0 percent rise in median asking rent from 2024 to 2026. It also reports 5.1 percent wage growth, which the article does not mention."),
        ],
    },
    {
        "slug": "river-restoration-act-clears-senate", "publisher": "metro-signal", "article_type": "news",
        "title": "River Restoration Act clears State X Senate after heated debate",
        "dek": "The $85 million bill now heads to the House. Both sides made claims about pollution and spending.",
        "author": "Legislative correspondent", "published_at": "2026-04-15T12:30:00Z", "primary_topic": "Environment",
        "body": (
            "The State X Senate passed the River Restoration Act, DEMO-SB-12, by a vote of 31 to 19 on April 14, 2026. "
            "The bill authorizes $85 million over five years for wetland restoration and wastewater upgrades along the Calder River.\n\n"
            "“This bill is a lifeline for every family on the river,” said Candidate A, who co-sponsored the measure. "
            "Candidate B called the bill “a reckless spending spree that taxpayers cannot afford.”\n\n"
            "Phosphorus pollution in the river has doubled, supporters said. "
            "Opponents said the state's Clean Water Fund already spent $40 million on similar projects in 2025.\n\n"
            "Environmental groups praised the vote as a historic win. "
            "The bill now goes to the State X House, where its prospects are uncertain."
        ),
        "annotations": [
            ("by a vote of 31 to 19", "DEMO-RC-2026-041", "supports", "The roll-call record shows passage 31–19 on April 14, 2026."),
            ("authorizes $85 million over five years", "DEMO-SB-12-TEXT", "supports",
             "Section 3 authorizes $85 million over fiscal years 2027–2031: $60 million for wastewater and $25 million for wetlands."),
            ("This bill is a lifeline", "DEMO-SEN-TR-2026-04-14", "supports", "The quotation appears verbatim in the floor transcript."),
            ("reckless spending spree", "DEMO-SEN-TR-2026-04-14", "supports",
             "The quotation appears verbatim in the floor transcript. The transcript also records Candidate B saying “I support cleaner water,” which the article omits."),
            ("has doubled", "DEMO-DEQ-PHOS-2025", "partially_supports",
             "Phosphorus rose 30–110% at 3 of 7 stations from 2016 to 2025, with no significant change at the other 4. “Doubled” fits only some stations."),
            ("Clean Water Fund already spent $40 million", "DEMO-CWF-2025", "partially_supports",
             "The fund spent $40 million in FY2025, but $9 million went to drinking water and none went to wetland restoration, so not all of it was spent on “similar projects.”"),
        ],
    },
    {
        "slug": "rural-clinic-closures", "publisher": "civic-wire-cooperative", "article_type": "news",
        "title": "Rural clinic closures leave three counties without walk-in care",
        "dek": "Advocates and state records give different counts of how many clinics have shut down.",
        "author": "Health reporter", "published_at": "2026-07-08T09:00:00Z", "primary_topic": "Healthcare",
        "body": (
            "Six rural clinics in State X have closed since January 2023, according to the State X Rural Health Alliance, an advocacy group. "
            "Three counties, Northfork, Pine Hollow and Tessaly, now have no walk-in clinic.\n\n"
            "The State X Legislature approved $12 million for the Rural Clinic Stabilization Fund in May 2026. "
            "Patients in Northfork County now travel an average of 48 miles to reach care, a local nurse said.\n\n"
            "Hospital administrators say the closures are a dire threat to public health. "
            "“We should not have to choose between groceries and gas money to see a doctor,” said one Northfork resident.\n\n"
            "The Department of Health is expected to publish an access study by December 2026."
        ),
        "annotations": [
            ("Six rural clinics in State X have closed", "DEMO-DOH-LIC-2026", "partially_supports",
             "Six licenses were surrendered, but the registry records four closures and two consolidations into regional centers."),
            ("now have no walk-in clinic", "DEMO-DOH-LIC-2026", "supports",
             "The registry lists no licensed walk-in clinic in the three counties as of June 30, 2026."),
            ("approved $12 million for the Rural Clinic Stabilization Fund", "DEMO-RC-2026-058", "supports",
             "The Senate passed DEMO-HB-40 on May 12, 2026 after House passage on May 5; it was signed May 20."),
        ],
    },
    {
        "slug": "opinion-housing-crunch", "publisher": "riverside-daily-ledger", "article_type": "opinion",
        "title": "Opinion: Our housing crunch is a crisis we chose",
        "dek": "A guest columnist argues for permit reform.",
        "author": "Guest columnist", "published_at": "2026-09-02T11:00:00Z", "primary_topic": "Economy & labor",
        "body": (
            "State X has a housing crisis, and it is a crisis of our own making. "
            "Permit rules written decades ago make it absurdly hard to build homes.\n\n"
            "Lawmakers should pass the Housing Permit Streamlining Act without delay. "
            "Every year we wait, young families are priced out. Clearly, the old rules have failed.\n\n"
            "I believe bold reform is the only responsible path. "
            "The next legislature will decide whether State X remains a place where teachers and nurses can afford to live."
        ),
        "annotations": [],
    },
    {
        "slug": "corvan-strait-talks-stall", "publisher": "metro-signal", "article_type": "news",
        "title": "Shipping talks stall over Corvan Strait dispute, clouding Port of State X outlook",
        "dek": "Traffic through the strait has fallen as the Republic of Aster and the Federation of Valdoria trade accusations.",
        "author": "Trade correspondent", "published_at": "2026-09-05T16:45:00Z", "primary_topic": "Foreign affairs",
        "body": (
            "Talks on a regional shipping agreement between the Republic of Aster and the Federation of Valdoria were suspended on September 3, 2026. "
            "Container transits through the Corvan Strait fell 18 percent in the first half of 2026 compared with the same period in 2025.\n\n"
            "The Port of State X handles about 12 percent of the region's strait-bound cargo. "
            "Officials from Aster said Valdoria had violated the 2009 Fisheries Accord. "
            "Valdoria's foreign ministry called the accusation “baseless and provocative.”\n\n"
            "Analysts say a prolonged dispute could cost the port thousands of jobs."
        ),
        "annotations": [
            ("fell 18 percent", "DEMO-CSMA-2026-H1", "supports", "Transits fell from 50,250 to 41,200, an 18 percent decline."),
            ("about 12 percent", "DEMO-PORT-AR-2025", "supports", "The port's annual report gives 11.6 percent for 2025, consistent with “about 12 percent.”"),
            ("violated the 2009 Fisheries Accord", "DEMO-ACCORD-2009", "provides_context",
             "The Accord sends disputes to a joint commission and then arbitration. No finding had been issued, so the alleged violation is neither established nor refuted."),
            ("baseless and provocative", "DEMO-VAL-MFA-2026-09", "supports", "The quoted words appear in the ministry's published statement."),
        ],
    },
]

CANDIDATES = [
    {"slug": "candidate-a", "name": "Candidate A", "office_sought": "Governor of State X",
     "office_held": "State Senator, District 4 (State X)", "jurisdiction": "State X", "party": "Harbor Party",
     "biography": "Fictional candidate. Two-term state senator; previously a municipal water-utility engineer."},
    {"slug": "candidate-b", "name": "Candidate B", "office_sought": "Governor of State X",
     "office_held": "State Senator, District 11 (State X)", "jurisdiction": "State X", "party": "Summit Party",
     "biography": "Fictional candidate. Three-term state senator; previously a small-business owner and county budget officer."},
    {"slug": "candidate-c", "name": "Candidate C", "office_sought": "Governor of State X",
     "office_held": None, "jurisdiction": "State X", "party": "Independent",
     "biography": "Fictional candidate. Former county administrator; has not held legislative office, so has no roll-call voting record."},
]

BILLS = [
    {"bill_number": "DEMO-SB-12", "title": "River Restoration Act", "topic": "Environment", "status": "Passed Senate; pending in House",
     "introduced_date": date(2026, 1, 20), "summary": "Authorizes $85 million over five years for wastewater upgrades and wetland restoration along the Calder River.",
     "roll_calls": [
         {"roll_call_id": "DEMO-RC-2026-039", "vote_date": date(2026, 4, 14), "question": "Motion to table Amendment 3", "is_procedural": True, "result": "Agreed to", "yeas": 27, "nays": 23,
          "positions": {"candidate-a": "yea", "candidate-b": "nay"}},
         {"roll_call_id": "DEMO-RC-2026-041", "vote_date": date(2026, 4, 14), "question": "On final passage", "is_procedural": False, "result": "Passed", "yeas": 31, "nays": 19,
          "positions": {"candidate-a": "yea", "candidate-b": "nay"}},
     ]},
    {"bill_number": "DEMO-HB-40", "title": "Rural Clinic Stabilization Fund Act", "topic": "Healthcare", "status": "Signed into law",
     "introduced_date": date(2026, 2, 3), "summary": "Appropriates $12 million to stabilize rural clinics, funded by a one-time transfer from the highway reserve.",
     "roll_calls": [
         {"roll_call_id": "DEMO-RC-2026-058", "vote_date": date(2026, 5, 12), "question": "On final passage", "is_procedural": False, "result": "Passed", "yeas": 33, "nays": 17,
          "positions": {"candidate-a": "yea", "candidate-b": "nay"}},
     ]},
    {"bill_number": "DEMO-SB-7", "title": "Budget Reserve Act", "topic": "Fiscal policy", "status": "Signed into law",
     "introduced_date": date(2026, 1, 9), "summary": "Raises the rainy-day fund target to 10% of general-fund spending; offsets part of the cost with reduced rural Medicaid clinic reimbursement rates.",
     "roll_calls": [
         {"roll_call_id": "DEMO-RC-2026-022", "vote_date": date(2026, 3, 3), "question": "On final passage", "is_procedural": False, "result": "Passed", "yeas": 28, "nays": 22,
          "positions": {"candidate-a": "nay", "candidate-b": "yea"}},
     ]},
    {"bill_number": "DEMO-SB-19", "title": "Housing Permit Streamlining Act", "topic": "Economy & labor", "status": "Passed Senate; pending in House",
     "introduced_date": date(2026, 2, 17), "summary": "Sets 60-day deadlines for residential permits and exempts projects under 20 units from local wetland-permit review.",
     "roll_calls": [
         {"roll_call_id": "DEMO-RC-2026-066", "vote_date": date(2026, 5, 27), "question": "On final passage", "is_procedural": False, "result": "Passed", "yeas": 26, "nays": 24,
          "positions": {"candidate-a": "nay", "candidate-b": "yea"}},
     ]},
    {"bill_number": "DEMO-SB-22", "title": "Port Security and Trade Continuity Act", "topic": "Foreign affairs", "status": "Signed into law",
     "introduced_date": date(2026, 3, 2), "summary": "Funds cargo-screening equipment and creates a contingency plan for strait shipping disruptions.",
     "roll_calls": [
         {"roll_call_id": "DEMO-RC-2026-071", "vote_date": date(2026, 6, 9), "question": "On final passage", "is_procedural": False, "result": "Passed", "yeas": 44, "nays": 6,
          "positions": {"candidate-a": "yea", "candidate-b": "yea"}},
     ]},
]

# (key, candidate, quote, date, venue, topic, links: [(roll_call_id, classification, rationale)])
STATEMENTS = [
    ("a1", "candidate-a", "I will always fight to clean up our rivers.", date(2025, 9, 14), "Campaign launch speech", "Environment",
     [("DEMO-RC-2026-041", "consistent", "Voted yea on final passage of a river-cleanup bill."),
      ("DEMO-RC-2026-039", "not_directly_comparable", "A procedural vote to table an amendment; its relationship to the statement cannot be established from the record. Excluded from the index.")]),
    ("a2", "candidate-a", "Rural families should not have to drive an hour to see a doctor.", date(2026, 1, 28), "Town hall, Northfork County", "Healthcare",
     [("DEMO-RC-2026-058", "consistent", "Voted yea on a bill funding rural clinics.")]),
    ("a3", "candidate-a", "We cannot balance the budget on the backs of rural patients.", date(2026, 2, 26), "State X Senate floor remarks", "Fiscal policy",
     [("DEMO-RC-2026-022", "consistent", "Voted nay on a reserve bill that reduced rural clinic reimbursement rates — the provision the statement addresses.")]),
    ("a4", "candidate-a", "I support cutting red tape so working families can build homes.", date(2026, 3, 18), "Builders association forum", "Economy & labor",
     [("DEMO-RC-2026-066", "potentially_inconsistent", "Voted nay on a permit-streamlining bill. Floor remarks cited the bill's wetland-review exemption. The record cannot show whether the position is conditional.")]),
    ("a5", "candidate-a", "Our ports have to stay open for business no matter what happens overseas.", date(2026, 5, 30), "Port of State X visit", "Foreign affairs",
     [("DEMO-RC-2026-071", "consistent", "Voted yea on a port trade-continuity bill.")]),
    ("b1", "candidate-b", "Every taxpayer dollar must be accounted for, and this state needs a real rainy-day fund.", date(2025, 10, 2), "Campaign launch speech", "Fiscal policy",
     [("DEMO-RC-2026-022", "consistent", "Voted yea on a bill raising the rainy-day fund target."),
      ("DEMO-RC-2026-041", "not_directly_comparable", "A general statement on accountability; the river bill vote does not test it directly. Excluded from the index.")]),
    ("b2", "candidate-b", "I want the Calder River to be clean for the next generation.", date(2026, 3, 30), "Editorial board interview", "Environment",
     [("DEMO-RC-2026-041", "mixed", "Voted nay on the river bill; floor transcript records support for “cleaner water” and objection to cost and duplication. Supporting a goal while opposing a specific bill is a conditional position.")]),
    ("b3", "candidate-b", "Rural clinics are the backbone of our communities.", date(2026, 4, 22), "Rural health summit", "Healthcare",
     [("DEMO-RC-2026-058", "potentially_inconsistent", "Voted nay on a clinic-funding bill. Stated objection (floor transcript) was the highway-reserve transfer; the statement does not address funding sources.")]),
    ("b4", "candidate-b", "Government should get out of the way of people who want to build housing.", date(2026, 5, 6), "Chamber of commerce luncheon", "Economy & labor",
     [("DEMO-RC-2026-066", "consistent", "Voted yea on a permit-streamlining bill.")]),
    ("b5", "candidate-b", "Secure ports mean secure jobs.", date(2026, 6, 1), "Port workers' union hall", "Foreign affairs",
     [("DEMO-RC-2026-071", "consistent", "Voted yea on a port security and trade-continuity bill.")]),
    ("c1", "candidate-c", "I would sign a river cleanup bill, but only one with an independent audit.", date(2026, 4, 20), "Candidate forum", "Environment", []),
    ("c2", "candidate-c", "Healthcare access in rural counties is the first thing I would fix.", date(2026, 6, 15), "Radio interview", "Healthcare", []),
    ("c3", "candidate-c", "The budget surplus should go back to taxpayers or into the reserve, not new programs.", date(2026, 9, 9), "Candidate forum", "Fiscal policy", []),
]

COMMITTEES = [
    {"committee_code": "DEMO-C-A01", "name": "Candidate A for Governor", "committee_type": "principal_campaign", "candidate": "candidate-a"},
    {"committee_code": "DEMO-C-B01", "name": "Candidate B for State X", "committee_type": "principal_campaign", "candidate": "candidate-b"},
    {"committee_code": "DEMO-C-C01", "name": "Committee to Elect Candidate C", "committee_type": "principal_campaign", "candidate": "candidate-c"},
    {"committee_code": "DEMO-P-01", "name": "Riverkeepers Action PAC", "committee_type": "pac", "candidate": None},
    {"committee_code": "DEMO-P-02", "name": "State X Builders Association PAC", "committee_type": "pac", "candidate": None},
    {"committee_code": "DEMO-P-03", "name": "Northfield Capital Group Employee PAC", "committee_type": "pac", "candidate": None},
    {"committee_code": "DEMO-PTY-H", "name": "Harbor Party State Committee", "committee_type": "party", "candidate": None},
    {"committee_code": "DEMO-PTY-S", "name": "Summit Party State Committee", "committee_type": "party", "candidate": None},
    {"committee_code": "DEMO-IE-01", "name": "Forward State X", "committee_type": "ie_only", "candidate": None},
    {"committee_code": "DEMO-IE-02", "name": "Citizens for Fiscal Integrity", "committee_type": "ie_only", "candidate": None},
]

PERIODS = {"2026-Q1": date(2026, 3, 31), "2026-Q2": date(2026, 6, 30), "2026-Q3": date(2026, 9, 30)}

# Receipts recorded on the recipient committee: (recipient, category, counterparty, {period: dollars})
RECEIPTS = [
    ("DEMO-C-A01", "individual_itemized", "Itemized individual contributors (aggregate)", {"2026-Q1": 420000, "2026-Q2": 510000, "2026-Q3": 640000}),
    ("DEMO-C-A01", "individual_unitemized", "Unitemized individual contributions (under $200)", {"2026-Q1": 180000, "2026-Q2": 230000, "2026-Q3": 260000}),
    ("DEMO-C-A01", "pac", "Riverkeepers Action PAC", {"2026-Q1": 5000, "2026-Q2": 5000, "2026-Q3": 5000}),
    ("DEMO-C-A01", "pac", "Northfield Capital Group Employee PAC", {"2026-Q2": 7500}),
    ("DEMO-C-B01", "individual_itemized", "Itemized individual contributors (aggregate)", {"2026-Q1": 390000, "2026-Q2": 560000, "2026-Q3": 600000}),
    ("DEMO-C-B01", "individual_unitemized", "Unitemized individual contributions (under $200)", {"2026-Q1": 150000, "2026-Q2": 190000, "2026-Q3": 240000}),
    ("DEMO-C-B01", "pac", "State X Builders Association PAC", {"2026-Q1": 5000, "2026-Q2": 5000, "2026-Q3": 5000}),
    ("DEMO-C-B01", "pac", "Northfield Capital Group Employee PAC", {"2026-Q2": 7500}),
    ("DEMO-C-C01", "candidate_self", "Candidate C (personal funds)", {"2026-Q1": 250000}),
    ("DEMO-C-C01", "individual_itemized", "Itemized individual contributors (aggregate)", {"2026-Q1": 120000, "2026-Q2": 160000, "2026-Q3": 210000}),
    ("DEMO-C-C01", "individual_unitemized", "Unitemized individual contributions (under $200)", {"2026-Q1": 60000, "2026-Q2": 90000, "2026-Q3": 140000}),
]
# Committee-to-committee transfers: (recipient, counterparty, {period: dollars})
TRANSFERS = [
    ("DEMO-C-A01", "Harbor Party State Committee", {"2026-Q3": 50000}),
    ("DEMO-C-B01", "Summit Party State Committee", {"2026-Q3": 50000}),
]
# Independent expenditures: (spender, target, support|oppose, vendor, {period: dollars})
IES = [
    ("DEMO-IE-01", "candidate-a", "support", "Bright Signal Media (television ads)", {"2026-Q2": 150000, "2026-Q3": 420000}),
    ("DEMO-IE-01", "candidate-b", "oppose", "Bright Signal Media (digital ads)", {"2026-Q3": 180000}),
    ("DEMO-IE-02", "candidate-b", "support", "Keystone Mail Works (direct mail)", {"2026-Q2": 120000, "2026-Q3": 380000}),
    ("DEMO-IE-02", "candidate-a", "oppose", "Keystone Mail Works (digital ads)", {"2026-Q3": 210000}),
    ("DEMO-P-01", "candidate-a", "support", "Canvass Collective (door-to-door outreach)", {"2026-Q3": 35000}),
]

CONFLICTS = [
    {
        "slug": "corvan-strait", "name": "Corvan Strait Shipping and Fisheries Dispute", "region": "Corvan Strait (fictional)",
        "summary": "A long-running dispute between the Republic of Aster and the Federation of Valdoria over navigation rights, fishing quotas and inspection authority in a strait that carries much of the region's container traffic. All entities and records are fictional.",
        "actors": ["Republic of Aster (fictional)", "Federation of Valdoria (fictional)", "Council of Nations (fictional)", "Corvan Strait Maritime Authority (fictional)"],
        "limitations": "Casualty-free dispute; humanitarian figures concern displacement of fishing communities. Estimates from government and NGO sources use different definitions and are shown separately, never summed.",
        "events": [
            (date(1994, 6, 12), "Treaty of Lumen signed", "Establishes shared navigation rights and a joint maritime authority.", "agreement", "documented_record", "Treaty of Lumen, Articles 1–4"),
            (date(2009, 3, 2), "Corvan Fisheries Accord", "Sets catch quotas and a dispute process (joint commission, then arbitration).", "agreement", "documented_record", "Corvan Fisheries Accord, Article 7"),
            (date(2017, 8, 19), "Aster expands declared fishing zone", "Aster publishes new zone coordinates; Valdoria files a formal objection.", "diplomacy", "documented_record", "Aster Gazette notice DEMO-AG-2017-118"),
            (date(2019, 11, 4), "Vessel collision near the median line", "A Valdorian patrol vessel and an Aster trawler collide. The two governments give conflicting accounts of which vessel caused the collision; no independent finding exists.", "escalation", "contested_interpretation", "Maritime Authority incident log DEMO-IL-2019-44"),
            (date(2021, 2, 15), "Council of Nations Resolution CN-DEMO-14", "Calls on both parties to resume negotiations within 12 months.", "resolution", "documented_record", "Council of Nations Resolution CN-DEMO-14"),
            (date(2024, 5, 30), "Joint inspection framework agreed", "Both parties agree to joint boarding inspections of fishing vessels.", "agreement", "documented_record", "Joint Inspection Framework text"),
            (date(2026, 3, 10), "Aster suspends joint inspections", "Aster suspends participation, citing quota violations. Valdoria disputes the allegation.", "escalation", "documented_record", "Aster Foreign Ministry notice DEMO-AFM-2026-07"),
            (date(2026, 9, 3), "Regional shipping talks suspended", "Talks on a shipping agreement are suspended without a date to resume.", "diplomacy", "documented_record", "Council of Nations secretariat statement DEMO-CN-2026-31"),
        ],
        "metrics": [
            {"metric_group": "humanitarian", "label": "Displaced fishing-community residents — government estimate", "value": 4200, "unit": "people",
             "period": "2026-06", "scope": "Aster coastal districts only", "methodology": "Registered relocation-assistance applicants.", "source_label": "Aster Interior Ministry bulletin DEMO-AIM-2026-06"},
            {"metric_group": "humanitarian", "label": "Displaced fishing-community residents — NGO estimate", "value": 7950, "value_low": 6800, "value_high": 9100, "unit": "people",
             "period": "2026-06", "scope": "Both coasts of the strait", "methodology": "Household survey extrapolated from 38 villages; includes people who moved without applying for assistance.", "source_label": "Strait Relief Network field survey DEMO-SRN-2026"},
            {"metric_group": "humanitarian", "label": "Households receiving fisheries hardship assistance", "value": 2300, "unit": "households",
             "period": "2026-Q2", "scope": "Valdorian coastal provinces", "methodology": "Administrative payment records.", "source_label": "Valdoria Ministry of Fisheries DEMO-VMF-2026-Q2"},
            {"metric_group": "economic", "label": "Container transits through the strait", "value": 41200, "unit": "transits",
             "period": "2026-H1", "scope": "All flagged vessels", "methodology": "Maritime Authority transit log.", "source_label": "Corvan Strait Maritime Authority DEMO-CSMA-2026-H1",
             "series": [{"period": "2024-H1", "value": 49800}, {"period": "2024-H2", "value": 51100}, {"period": "2025-H1", "value": 50250}, {"period": "2025-H2", "value": 47900}, {"period": "2026-H1", "value": 41200}]},
            {"metric_group": "economic", "label": "Change in regional fishery landings value", "value": -22, "unit": "percent",
             "period": "2025 vs 2026 (Jan–Jun)", "scope": "Both national fleets", "methodology": "Port landing declarations, nominal values.", "source_label": "Joint commission statistical note DEMO-JC-2026-02"},
            {"metric_group": "economic", "label": "Change in average cargo insurance premium", "value": 35, "unit": "percent",
             "period": "2026-Q3 vs 2025-Q3", "scope": "Strait-transiting container vessels", "methodology": "Survey of five regional underwriters; small sample.", "source_label": "Regional Marine Underwriters survey DEMO-RMU-2026"},
        ],
        "arguments": [
            ("Multilateral mediation (Council of Nations)", "for", "empirical", "Recorded vessel incidents fell from 14 to 3 in the year after the 2024 joint inspection framework began.", "Maritime Authority incident logs (demonstration record)."),
            ("Multilateral mediation (Council of Nations)", "for", "normative", "Shared waters should be governed jointly by the states that depend on them.", "A value judgement; not testable with data."),
            ("Multilateral mediation (Council of Nations)", "against", "empirical", "Negotiations did not begin until three years after Resolution CN-DEMO-14 called for them within 12 months.", "Council of Nations records (demonstration record)."),
            ("Multilateral mediation (Council of Nations)", "against", "normative", "Mediation can lend legitimacy to territorial claims that one party considers unlawful.", "A value judgement; not testable with data."),
            ("National enforcement of declared zones", "for", "empirical", "Aster reports fewer illegal-catch reports in its declared zone after patrols increased in 2018.", "Aster government data only; not independently verified."),
            ("National enforcement of declared zones", "for", "normative", "Governments have a duty to protect the livelihoods of their fishing communities.", "A value judgement; not testable with data."),
            ("National enforcement of declared zones", "against", "empirical", "Recorded incidents rose in the two years after the 2017 zone expansion.", "Maritime Authority incident logs (demonstration record)."),
            ("National enforcement of declared zones", "against", "normative", "Unilateral enforcement risks escalation that harms civilians on both coasts.", "A value judgement; not testable with data."),
        ],
    },
    {
        "slug": "highland-basin", "name": "Highland Basin Water Allocation Dispute", "region": "Highland Basin (fictional)",
        "summary": "An upstream–downstream disagreement between the Province of Merel and the Commonwealth of Osterly over dam releases on a shared river during drought years. All entities and records are fictional.",
        "actors": ["Province of Merel (fictional)", "Commonwealth of Osterly (fictional)", "Highland Basin Commission (fictional)"],
        "limitations": "Flow data come from a single upstream gauge network; downstream irrigation losses are self-reported by farm cooperatives.",
        "events": [
            (date(2002, 4, 1), "Highland Basin Water Compact", "Allocates 55% of dry-season flow downstream.", "agreement", "documented_record", "Highland Basin Water Compact, Schedule 2"),
            (date(2018, 7, 9), "Merel Dam completed", "New reservoir begins filling during a below-average rainfall year.", "diplomacy", "documented_record", "Highland Basin Commission notice DEMO-HBC-2018-03"),
            (date(2023, 8, 21), "Dry-season release dispute", "Osterly says releases fell below the compact share; Merel says the gauge data are unreliable. The Commission has not ruled.", "escalation", "contested_interpretation", "Commission meeting minutes DEMO-HBC-2023-11"),
            (date(2025, 3, 14), "Interim drought protocol", "Both parties agree to a temporary release schedule for 2025–2027.", "agreement", "documented_record", "Interim Drought Protocol text"),
        ],
        "metrics": [
            {"metric_group": "economic", "label": "Downstream irrigated area left fallow", "value": 18, "unit": "percent", "period": "2023 season", "scope": "Osterly lower valley",
             "methodology": "Self-reported by farm cooperatives.", "source_label": "Osterly Farm Cooperative Federation DEMO-OFCF-2023"},
            {"metric_group": "economic", "label": "Dry-season downstream flow share", "value": 47, "unit": "percent of total", "period": "2023 dry season", "scope": "Main stem at border gauge",
             "methodology": "Daily gauge readings averaged.", "source_label": "Highland Basin Commission gauge report DEMO-HBC-G-2023",
             "series": [{"period": "2019", "value": 56}, {"period": "2020", "value": 54}, {"period": "2021", "value": 52}, {"period": "2022", "value": 50}, {"period": "2023", "value": 47}, {"period": "2024", "value": 53}, {"period": "2025", "value": 55}]},
        ],
        "arguments": [
            ("Binding commission arbitration", "for", "empirical", "Flow share returned to the compact level in the first year of the interim protocol.", "Commission gauge report (demonstration record)."),
            ("Binding commission arbitration", "against", "normative", "Upstream communities should keep control over infrastructure they financed.", "A value judgement; not testable with data."),
            ("Bilateral renegotiation of the compact", "for", "normative", "Allocation rules written before the dam existed should be updated by the parties themselves.", "A value judgement; not testable with data."),
            ("Bilateral renegotiation of the compact", "against", "empirical", "Two previous bilateral rounds (2019, 2021) ended without agreement.", "Commission minutes (demonstration record)."),
        ],
    },
]
