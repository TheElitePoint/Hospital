#!/usr/bin/env python3
"""Contract tests for SOP2/3 without paid provider calls."""
import pathlib, sys, tempfile
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from hp import db, sop2, sop3

with tempfile.TemporaryDirectory() as td:
    con = db.init(str(pathlib.Path(td) / "t.db"))
    con.execute("""INSERT INTO accounts(account_id,canonical_account_name,parent_system_name,state,city,
      primary_use_case,priority_class,account_archetype,current_signal,qualification_status,handoff_ready,
      linkedin_company_url,linkedin_sector_status,stage_status)
      VALUES ('A1','Mercy Regional Hospital','NOT_APPLICABLE','TX','Austin',
      'U1_DIGITAL_RHYTHM_WORKFLOW','A_PRIORITY','COMMUNITY_ACUTE','PRESENT','PASS',1,
      'https://www.linkedin.com/company/mercy-regional','SECTOR_PASS','PASS')""")
    con.commit()
    employees = [
      {"profileUrl":"https://linkedin.com/in/jane-owner","name":"Jane Owner",
       "jobTitle":"Director of Telemetry","location":"Austin, Texas","companyName":"Mercy Regional Hospital",
       "companyUrl":"https://www.linkedin.com/company/mercy-regional","source":"voyager"},
      {"profileUrl":"https://linkedin.com/in/india-person","name":"India Person",
       "jobTitle":"Director of Telemetry","location":"Bengaluru, India","companyName":"Mercy Regional Hospital",
       "companyUrl":"https://www.linkedin.com/company/mercy-regional"},
    ]
    with patch("hp.sop2.run_actor", return_value=employees):
        result = sop2.discover_batch(con, [dict(con.execute("SELECT * FROM accounts").fetchone())], object(), 20)
    assert result["pass"] == 1 and result["review"] == 1
    assert con.execute("SELECT COUNT(*) FROM people WHERE person_status='PERSON_PASS'").fetchone()[0] == 1

    person = dict(con.execute("SELECT * FROM people WHERE person_status='PERSON_PASS'").fetchone())
    profile = {"profileUrl": person["linkedin_profile_url"], "location":"Austin, Texas",
               "experience":[{"title":"Director of Telemetry","companyName":"Mercy Regional Hospital",
                              "isCurrent":True}], "scrapedAt":"2026-09-15"}
    with patch("hp.sop3.run_actor", return_value=[profile]), patch("hp.sop3._disproof", return_value=[]):
        result = sop3.validate_batch(con, [person], object(), object())
    assert result["pass"] == 1
    val = dict(con.execute("SELECT * FROM validations WHERE person_id=?", (person["person_id"],)).fetchone())
    assert val["validation_status"] == "VALIDATED_PASS" and val["handoff_ready"] == 1
    assert val["employment_status"] == "CURRENT_CONFIRMED"
    assert val["validated_role_family"] == "TELEMETRY_CARDIAC_MONITORING"

    # 6. departure check: current-role news must not count, real exits must
    from hp.sop3 import departure_signal as dep
    cases = [
      ("Tomislav Mihaljevic, MD, Named Cleveland Clinic CEO, President Dr. Mihaljevic, 53, joined Cleveland Clinic in 2004", "Tomislav Mihaljevic, M.D.", "CLEVELAND CLINIC", False),
      ("Bruce D. White, President and CEO | Knox Community Hospital Bruce joined the KCH team in July of 1996 and, in addition to his current role as CEO", "Bruce White", "Knox Community Hospital", False),
      ("Join us for the next Career Mountaineers, presented in partnership with Baylor University Medical", "Jeshahnton V. Essex, FACHE", "BAYLOR UNIVERSITY MEDICAL CENTER", False),
      ("Jane Smith joined St Luke's Hospital as chief nursing officer in 2022.", "Jane Smith", "ST LUKES HOSPITAL", False),
      ("Marlena Gainey ## Activity - Excited to share that I've joined Hendricks Regional Health as the Childbirth Center Director.", "Marlena Gainey", "INDIANA UNIVERSITY HEALTH", True),
      ("Dr. Alan Brooks left Mercy Hospital in March to lead a system in Texas.", "Alan Brooks", "MERCY HOSPITAL", True),
      ("Dana Whitfield, former Chief Nursing Officer at St Luke's, retired last year.", "Dana Whitfield", "ST LUKES HOSPITAL", True),
      ("Jane Smith joined Methodist Hospital as chief nursing officer.", "Jane Smith", "ST LUKES HOSPITAL", True),
      ("Christopher Alvarez was appointed CFO of Melissa Memorial Hospital in Holyoke, Colo.", "Melissa E.", "PARKVIEW HOSPITAL", True),
    ]
    for text, name, acct, expected in cases:
        assert dep(text, name, acct) is expected, (name, expected)
    print("sop2/3: 6/6")

    # 7. full-name matching: a shared surname or a hospital acronym must not flag a person
    more = [
      ("Joey Preast was named CEO. Mosaic Health, a venture with private equity firm Clayton, Dubilier & Rice.", "Lisa Clayton", "EVERGREEN MEDICAL CENTER", False),
      ("David Rollins was named CFO of Grande Ronde Hospital in La Grande, Ore.", "Tom Rollins", "EVERGREEN MEDICAL CENTER", False),
      ("Mr. Scarboro joins SDCH and Prime Healthcare after serving as Chief Operating Officer. Parrish Scarboro joins SDCH.", "Parrish Scarboro", "SAN DIMAS COMMUNITY HOSPITAL", False),
      ("Tom Rollins left Evergreen Medical Center in May to lead a hospital in Ohio.", "Tom Rollins", "EVERGREEN MEDICAL CENTER", True),
      ("Rollins, Tom retired from the hospital last year.", "Tom Rollins", "ST LUKES HOSPITAL", True),
    ]
    for text, name, acct, expected in more:
        assert dep(text, name, acct) is expected, (name, expected)
    print("sop2/3 full-name: ok")
