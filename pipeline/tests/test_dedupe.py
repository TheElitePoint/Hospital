#!/usr/bin/env python3
import pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from hp import db
from hp.dedupe import audit

with tempfile.TemporaryDirectory() as td:
    con=db.init(str(pathlib.Path(td)/'d.db'))
    for pid,name,url,title in [
      ('P1','Jane Smith','https://www.linkedin.com/in/jane-smith/','Director of Telemetry'),
      ('P2','Jane Smith','https://linkedin.com/in/jane-smith?trk=public','Telemetry Director'),
    ]:
        con.execute("INSERT INTO people(person_id,account_id,full_name,current_title,linkedin_profile_url,person_status,duplicate_status) VALUES (?,?,?,?,?,'PERSON_PASS','UNIQUE')",
                    (pid,'A1',name,title,url))
    con.commit()
    result=audit(con)
    assert result['confirmed_duplicates']==1
    assert con.execute("SELECT duplicate_status FROM people WHERE person_id='P2'").fetchone()[0]=='DUPLICATE'
    assert con.execute("SELECT COUNT(*) FROM duplicate_candidates WHERE key_type='LINKEDIN'").fetchone()[0]==1
    print('dedupe: 3/3')
