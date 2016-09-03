#!/usr/bin/env python
from deepdive import *
import ddlib
import os

@tsv_extractor
@returns(lambda
        p_id   = "text",
        e_id   = "text",
        feature = "text",
    :[])
def extract(
        p_id          = "text",
        e_id          = "text",
        p_begin_index = "int",
        p_end_index   = "int",
        e_begin_index = "int",
        e_end_index   = "int",
        doc_id         = "text",
        sent_index     = "int",
        tokens         = "text[]",
        lemmas         = "text[]",
        pos_tags       = "text[]",
        ner_tags       = "text[]",
        dep_types      = "text[]",
        dep_parents    = "int[]",
    ):
    """
    Uses DDLIB to generate features for the spouse relation.
    """
    ddlib.load_dictionary(os.path.abspath("../../../job_employ_keyword.txt"), dict_id="has_employment");
    ddlib.load_dictionary(os.path.abspath("../../../job_no_employ_keyword.txt"),dict_id="no_employment");
    # Create a DDLIB sentence object, which is just a list of DDLIB Word objects
    sent = []
    for i,t in enumerate(tokens):
        sent.append(ddlib.Word(
            begin_char_offset=None,
            end_char_offset=None,
            word=t,
            lemma=lemmas[i],
            pos=pos_tags[i],
            ner=ner_tags[i],
            dep_par=dep_parents[i] - 1,  # Note that as stored from CoreNLP 0 is ROOT, but for DDLIB -1 is ROOT
            dep_label=dep_types[i]))

    # Create DDLIB Spans for the two mentions
    p_span = ddlib.Span(begin_word_id=p_begin_index, length=(p_end_index-p_begin_index+1))
    e_span = ddlib.Span(begin_word_id=e_begin_index, length=(e_end_index-e_begin_index+1))

    # Generate the generic features using DDLIB
    for feature in ddlib.get_generic_features_relation(sent, p_span, e_span):
        yield [p_id, e_id, feature]
