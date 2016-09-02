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

    JOB_GENERAL = frozenset(["job", "employee","member","worker"])
    JOB_TITLE = frozenset(["manager", "executive", "engineer", "analyst", \
        "developer", "accountant", "therapist", "director", "officer", "clerk",\
         "assistant", "consultant", "president","administrator","specialist","supervisor","chairman","founder"])
    JOB_PREP = frozenset(["of", "at","by","in"])
    JOB_VERB = frozenset(["work", "employ","hire"])

    NO_JOB = frozenset(["retire","leave","resign","fire"])

    MAX_DIST = 10

    # find the intermediate region
    min_end_idx = min(p_end, e_end)
    max_start_idx = max(p_begin, e_begin)
    max_end_idx = max(p_end,e_end)
    intermediate_lemmas = lemmas[min_end_idx+1:max_start_idx]
    intermediate_ner_tags = ner_tags[min_end_idx+1:max_start_idx]
    head_lemmas = lemmas[:e_begin]
    #tail_lemmas = lemmas[max_end_idx+1:]


    employment = employmentLabel(p_id=p_id, e_id=e_id, label=None, type=None)

    # too far way
    if len(intermediate_lemmas) > MAX_DIST:
        yield employment._replace(label=-1, type='neg:far_apart')

    if 'ORGANIZATION' in intermediate_ner_tags:
        yield employment._replace(label=-1, type='neg:third_org_between')


    # PERSON  work at|employ by ORGANIZATION
    if len(JOB_VERB.intersection(intermediate_lemmas)) > 0 and len(JOB_PREP.intersection(intermediate_lemmas)) > 0:
        yield employment._replace(label=1, type='pos:employ_verb')

    # JOB_TITLE JOB_PREP ORGANIZATION: executive of google
    if len(JOB_TITLE.intersection(head_lemmas)) > 0 and len(JOB_PREP.intersection(head_lemmas)) > 0:
        yield employment._replace(label=1, type='pos:employ_noun_before_org')

    if (len(JOB_TITLE.intersection(intermediate_lemmas)) > 0 or len(JOB_GENERAL.intersection(intermediate_lemmas))) and len(JOB_PREP.intersection(head_lemmas)) > 0:
        yield employment._replace(label=1, type='pos:employ_noun_in_between')

    if len(NO_JOB.intersection(intermediate_lemmas)) > 0:
        yield employment._replace(label=-1, type='neg:leave organization')






