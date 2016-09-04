#!/usr/bin/env python
from deepdive import *
import random
from collections import namedtuple

employmentLabel = namedtuple('employmentLabel', 'p_id, e_id, label, type')

@tsv_extractor
@returns(lambda
        p_id   = "text",
        e_id   = "text",
        label   = "int",
        rule_id = "text",
    :[])
def supervise(
        p_id="text", p_text= "text",p_begin="int", p_end="int",
        e_id="text", e_text= "text",e_begin="int", e_end="int",
        doc_id="text", sentence_index="int",
        tokens="text[]", lemmas="text[]", pos_tags="text[]", ner_tags="text[]",
    ):
    
    # RATIO_THRESHOLD = 80;

    # employment = employmentLabel(p_id=p_id, e_id=e_id, label=None, type=None)

    # #compare two organization name 
    # p_ratio = fuzz.ratio(p_text.lower(),p_db_name.lower())
    # e_ratio = fuzz.partial_ratio(e_text.lower(),e_db_name.lower())

    # # check fuzzy ratio of name and organization
    # if (p_ratio >= RATIO_THRESHOLD) and (e_ratio >= RATIO_THRESHOLD):
    #     yield employment._replace(label=1,type='from_dbpedia')

    JOB_TITLE = frozenset(["job", "employee","member","worker","manager", "executive", "engineer", "analyst", \
        "developer", "accountant", "therapist", "director", "officer", "clerk",\
         "assistant", "consultant", "president","administrator","specialist","supervisor","chairman","founder"])
    
    JOB_VERB = frozenset(["work", "employ","hire","lead"])

    NO_JOB = frozenset(["retire","resign","fire","discharge","layoff","dismiss"])
    #NO_JOB_ADJ = frozenset(["former","retire"])
    CONJUNCT = frozenset(["with","and"])

    FAR_DIST = 10
    MAX_P_E_DIST = 4

    # find the intermediate region
    min_end_idx = min(p_end, e_end)
    max_start_idx = max(p_begin, e_begin)
    max_end_idx = max(p_end,e_end)
    intermediate_lemmas = lemmas[min_end_idx+1:max_start_idx]
    intermediate_ner_tags = ner_tags[min_end_idx+1:max_start_idx]
    intermediate_pos_tags = pos_tags[min_end_idx+1:max_start_idx]
    e_head_lemmas = lemmas[:e_begin]
    e_head_nertags = ner_tags[:e_begin]
    e_head_postags = pos_tags[:e_begin]
    e_tail_nertags = ner_tags[e_end+1:]

    

    #tail_lemmas = lemmas[max_end_idx+1:]


    employment = employmentLabel(p_id=p_id, e_id=e_id, label=None, type=None)


    # too far way
    if len(intermediate_lemmas) > FAR_DIST:
        yield employment._replace(label=-1, type='neg:far_apart')
    else:
        # should not be any other organization between
        if 'ORGANIZATION' in intermediate_ner_tags:
            yield employment._replace(label=-1, type='neg:third_org_between')
        
        if 'PERSON' in intermediate_ner_tags:
            yield employment._replace(label=-1, type='neg:third_person_between')


        # PERSON, and|with JOB_TITLE ORGANIZATION, PERSON
        if len(CONJUNCT.intersection(intermediate_lemmas)) > 0  and e_begin > p_begin and len(JOB_TITLE.intersection(intermediate_lemmas)) > 0 and 'PERSON' in e_tail_nertags  :
            yield employment._replace(label=-1, type='neg:person_before_employment' )

        # words that indicates previous employment
        if len(NO_JOB.intersection(intermediate_lemmas)) > 0:
            yield employment._replace(label=1, type='pos:employment_before')

        # PERSON of the ORGANIZATION without JOB TITILE
        if len(JOB_TITLE.intersection(intermediate_lemmas)) == 0 and len(intermediate_lemmas) < MAX_P_E_DIST and 'IN' in intermediate_pos_tags and e_begin > p_begin:
            yield employment._replace(label=1, type='pos:employ_person_of_org')
        
        # PERSON, JOB_TITLE of the ORGANIZATION 
        if len(JOB_TITLE.intersection(intermediate_lemmas)) > 0 and 'IN' in intermediate_pos_tags and e_begin > p_begin:
            yield employment._replace(label=1, type='pos:employ_title_after_person')

        # JOB_TITLE of the ORGANIZATION, PERSON
        if len(JOB_TITLE.intersection(e_head_lemmas)) > 0 and 'IN' in e_head_postags and e_begin < p_begin:
            yield employment._replace(label=1, type='pos:employ_title_before_person')

        # PERSON  work at|employ by ORGANIZATION
        if len(JOB_VERB.intersection(intermediate_lemmas)) > 0 and 'IN' in intermediate_pos_tags:
            yield employment._replace(label=1, type='pos:employ_verb')

        # No preposition, ORGANIZATION JOB_TITLE, PERSON
        if len(JOB_TITLE.intersection(intermediate_lemmas)) > 0 and 'IN' not in intermediate_pos_tags and len(intermediate_lemmas) < MAX_P_E_DIST :
            yield employment._replace(label=1, type='pos:employ_person_org')





