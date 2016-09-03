deepdive sql eval "SELECT hsi.p_id
     , hsi.e_id
     , s.doc_id
     , s.sentence_index
     , hsi.label
     , hsi.expectation
     , s.tokens
     , pm1.mention_text AS p1_text
     , pm1.begin_index  AS p1_start
     , pm1.end_index    AS p1_end
     , pm2.mention_text AS p2_text
     , pm2.begin_index  AS p2_start
     , pm2.end_index    AS p2_end

  FROM is_employment_label_inference hsi
     , person_mention             pm1
     , organization_mention             pm2
     , sentences                  s

 WHERE hsi.p_id          = pm1.mention_id
   AND pm1.doc_id         = s.doc_id
   AND pm1.sentence_index = s.sentence_index
   AND hsi.e_id          = pm2.mention_id
   AND pm2.doc_id         = s.doc_id
   AND pm2.sentence_index = s.sentence_index
   AND       expectation >= 0.9

 ORDER BY random()
 LIMIT 200" format=csv header=1 >labeling/is_employment-precision/is_employment.csv
