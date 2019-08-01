#!/usr/bin/env python3
"""

OVERVIEW:


The code in this module recognizes time expressions in a sentence and returns
a JSON result with information on each time expression that it finds. The
supported time formats are listed next, using the abbreviations:

    hh is zero-padded 00-24
    mm is zero-padded 00-59
    ss is zero-padded 00-60 (60 means leap second)

    am_pm is OPTIONAL and can be any of these variants:

        'am', 'pm', 'AM', 'PM', 'a.m.', 'p.m.', 'A.M.', 'P.M.', 'am.', 'pm.'
                   
1.  ISO8601 Formats

    Any of these formats:

        <time>Z
        <time>+-hh:mm
        <time>+-hhmm
        <time>+-hh

    Where <time> means any of these:

        hh
        hh:mm or hhmm
        hh:mm:ss or hhmmss
        hh:mm:ss.\d+  or hhmmss.\d+ (any number of fractional digits)


REDO THIS

2.  Hour only with AM or PM designator:

          h am_pm
         hh am_pm

          examples: 4 am, 5PM, 10a.m., 9 pm., et.

3.  Hours and minutes, with optional AM/PM designator:

          h:mm am_pm
         hh:mm am_pm
        thh:mm am_pm
        Thh:mm am_pm

4.  Hours, minutes, and seconds:

         hh:mm:ss
        thh:mm:ss
        Thh:mm:ss

5.  Hours, minutes, seconds, and fractional seconds:

         

        08:11:40:123456, 08:11:40.123456



    _regex_h24ms_with_gmt_delta, # 3
    _regex_h24ms_with_timezone,  # 4
    _regex_h24ms_no_colon,       # 5
    _regex_h24m_no_colon,        # 6
    _regex_h12msf_am_pm,         # 7
    _regex_h12ms_am_pm,          # 8
    _regex_h12m_am_pm,           # 9
    _regex_h12_am_pm,            # 10
    _regex_h24msf,               # 11
    _regex_h24ms,                # 12
    _regex_h24m,                 # 13
    _regex_h12m,                 # 14


    


OUTPUT:



The set of JSON fields in the output for each time expression includes:

    text                matching text
    start               starting character offset of the matching text
    end                 final character offset of the matching text + 1
    hours               integer hours
    minutes             integer minutes
    seconds             integer seconds
    fractional_seconds  string, contains digits after decimal point
                        including any leading zeros
    am_pm               string, either STR_AM or STR_PM (see values below)
    timezone            string
    gmt_delta_sign      sign of the UTC offset, either '+' or '-'
    gmt_delta_hours     integer, UTC hour offset
    gmt_delta_minutes   integer, UTC minute offset

Any missing fields will have the value EMPTY_FIELD. All JSON results will
contain an identical number of fields.

All time expression recognition is case-insensitive.

JSON results are written to stdout.


USAGE:


To use this code as an imported module, add the following lines to the
import list in the importing module:

        import json
        import time_finder as tf

To find time expressions in a sentence and capture the JSON result:

        json_string = tf.run(sentence)

To unpack the JSON results:

        json_data = json.loads(json_string)
        time_results = [df.TimeValue(**m) for m in json_data]

        for t in time_results:
            print(t.text)
            print(t.start)
            print(t.end)
            if tf.EMPTY_FIELD != t.hours:
                print(t.hours)
            etc.

References: 

    PHP Time Formats:
        http://php.net/manual/en/datetime.formats.time.php

    World time zones:
        https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations

    ISO8601 formats:
        https://en.wikipedia.org/wiki/ISO_8601

"""

import re
import os
import sys
import json
from collections import namedtuple


# This module returns JSON containing a 'TimeValue' object for each time
# expression that it finds.

# default value for all fields
EMPTY_FIELD = None

TIME_VALUE_FIELDS = [
    'text',
    'start',
    'end',
    'hours',
    'minutes',
    'seconds',
    'fractional_seconds',
    'am_pm',
    'timezone',
    'gmt_delta_sign',
    'gmt_delta_hours',
    'gmt_delta_minutes'
]
TimeValue = namedtuple('TimeValue', TIME_VALUE_FIELDS)

# set default value of all fields to EMPTY_FIELD
TimeValue.__new__.__Defaults__ = (EMPTY_FIELD,) * len(TimeValue._fields)

STR_AM = 'am'
STR_PM = 'pm'


###############################################################################


_VERSION_MAJOR = 0
_VERSION_MINOR = 2
_MODULE_NAME = 'time_finder.py'

# set to True to see debug output
_TRACE = False

# fractional seconds
_str_frac = r'[.:][0-9]+'

# hours, 12-hour clock
_str_h12 = r'(0?[1-9]|1[0-2])'

# hours, 24-hour clock
_str_h24 = r'([01][0-9]|2[0-4])'

# am or pm
_str_am_pm = r'[aApP]\.?[mM]\.?'

# minutes
_str_MM = r'[0-5][0-9]'

# world time zones (added 'Z' for Zulu == zero meridian)
_str_time_zone_abbrev = r'(ACDT|ACST|ACT|ACWST|ADT|AEDT|AEST|AFT|AKDT|'      +\
    'AKST|AMST|AMT|ART|AST|AWST|AZOST|AZOT|AZT|BDT|'      +\
    'BIOT|BIT|BOT|BRST|BRT|BST|BTT|CAT|CCT|CDT|CEST|'     +\
    'CET|CHADT|CHAST|CHOT|CHOST|CHST|CHUT|CIST|CIT|'      +\
    'CKT|CLST|CLT|COST|COT|CST|CT|CVT|CWST|CXT|DAVT|'     +\
    'DDUT|DFT|EASST|EAST|EAT|ECT|EDT|EEST|EET|EGST|'      +\
    'EGT|EIT|EST|FET|FJT|FKST|FKT|FNT|GALT|GAMT|GET|'     +\
    'GFT|GILT|GIT|GMT|GST|GYT|HDT|HAEC|HST|HKT|HMT|'      +\
    'HOVST|HOVT|ICT|IDLW|IDT|IOT|IRDT|IRKT|IRST|IST|'     +\
    'JST|KGT|KOST|KRAT|KST|LHST|LINT|MAGT|MART|MAWT|'     +\
    'MDT|MET|MEST|MHT|MIST|MIT|MMT|MSK|MST|MUT|MVT|'      +\
    'MYT|NCT|NDT|NFT|NPT|NST|NT|NUT|NZDT|NZST|OMST|'      +\
    'ORAT|PDT|PET|PETT|PGT|PHOT|PHT|PKT|PMDT|PMST|'       +\
    'PONT|PST|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|'      +\
    'SCT|SDT|SGT|SLST|SRET|SRT|SST|SYOT|THAT|THA|TFT|'    +\
    'TJT|TKT|TLT|TMT|TRT|TOT|TVT|ULAST|ULAT|USZ1|UTC|'    +\
    'UYST|UYT|UZT|VET|VLAT|VOLT|VOST|VUT|WAKT|WAST|'      +\
    'WAT|WEST|WET|WIT|WST|YAKT|YEKT|Z)'

# separator, colon only (not supporting '.' as a separator)
_str_sep = r'[:]'

# t or T, to indicate time
_str_t = r'\b[tT]?'


# 12 hour notation


# hour only, with am_pm:
#    4 am, 5PM, 10a.m., 9 pm.
_str_h12_am_pm = r'\b(?P<hours>' + _str_h12    + r')' + r'\s*'                +\
                 r'(?P<am_pm>'   + _str_am_pm  + r')'
_regex_h12_am_pm = re.compile(_str_h12_am_pm)

# hour and minutes:
#    4:08, 10:14
_str_h12m = r'\b(?P<hours>' + _str_h12 + r')'+ _str_sep                       +\
            r'(?P<minutes>' + _str_MM  + r'(?!\d))'
_regex_h12m = re.compile(_str_h12m)

# hour and minutes, with am_pm:
#    5:09 am, 9:41 P.M., 10:02 AM
_str_h12m_am_pm = r'\b(?P<hours>' + _str_h12   + r')' + _str_sep              +\
                  r'(?P<minutes>' + _str_MM    + r')' + r'\s*'                +\
                  r'(?P<am_pm>'   + _str_am_pm + r'(?!\d))'
_regex_h12m_am_pm = re.compile(_str_h12m_am_pm)

# hour, minutes, and seconds, with am_pm:
#    6:10:37 am, 7:19:19P.M.
_str_h12ms_am_pm = r'\b(?P<hours>' + _str_h12   + r')' + _str_sep             +\
                   r'(?P<minutes>' + _str_MM    + r')' + _str_sep             +\
                   r'(?P<seconds>' + _str_MM    + r')' + r'\s*'               +\
                   r'(?P<am_pm>'   + _str_am_pm + r')'
_regex_h12ms_am_pm = re.compile(_str_h12ms_am_pm)

# hour, minutes, seconds, and fraction, with am_pm:
#    7:11:39:123123 am and 9:41:22.22334p.m.
_str_h12msf_am_pm = r'\b(?P<hours>' + _str_h12   + r')' + r':'                +\
                    r'(?P<minutes>' + _str_MM    + r')' + r':'                +\
                    r'(?P<seconds>' + _str_MM    + r')'                       +\
                    r'(?P<frac>'    + _str_frac  + r')' + r'\s*'              +\
                    r'(?P<am_pm>'   + _str_am_pm + r')'
_regex_h12msf_am_pm = re.compile(_str_h12msf_am_pm)


# 24 hour notation


# hour and minutes:
#    08:12, T23:43
_str_h24m = _str_t                                        +\
           r'(?P<hours>'   + _str_h24 + r')' + _str_sep   +\
           r'(?P<minutes>' + _str_MM  + r'(?!\d))'
_regex_h24m = re.compile(_str_h24m)

# hour and minutes, no colon
_str_h24m_no_colon = _str_t                              +\
                    r'(?P<hours>'   + _str_h24 + r')'    +\
                    r'(?P<minutes>' + _str_MM  + r'(?!\d))'
_regex_h24m_no_colon = re.compile(_str_h24m_no_colon)

# hour, minutes, and seconds
#    01:03:24, t14:15:16
_str_h24ms = _str_t                                       +\
            r'(?P<hours>'   + _str_h24 + r')' + _str_sep  +\
            r'(?P<minutes>' + _str_MM  + r')' + _str_sep  +\
            r'(?P<seconds>' + _str_MM  + r'(?!\d))'
_regex_h24ms = re.compile(_str_h24ms)

# hour, minutes, and seconds, no colon
_str_h24ms_no_colon = _str_t                             +\
                     r'(?P<hours>'   + _str_h24 + r')'   +\
                     r'(?P<minutes>' + _str_MM  + r')'   +\
                     r'(?P<seconds>' + _str_MM  + r'(?!\d))'
_regex_h24ms_no_colon = re.compile(_str_h24ms_no_colon)

# hour, minutes, seconds, and timezone
#    040837EST, 112345 HOVST, T093000 Z
_str_h24ms_with_timezone = _str_t                                             +\
                          r'(?P<hours>'    + _str_h24 + r')'                  +\
                          r'(?P<minutes>'  + _str_MM  + r')'                  +\
                          r'(?P<seconds>'  + _str_MM  + r')'       + r'\s*'   +\
                          r'(?P<timezone>' + _str_time_zone_abbrev + r')'
_regex_h24ms_with_timezone = re.compile(_str_h24ms_with_timezone, re.IGNORECASE)

# hour, minutes, seconds with GMT delta
_str_gmt_delta = r'(GMT|UTC)?[-+]' + _str_h24 + r':?' + r'(' + _str_MM + r')?'
_str_h24ms_with_gmt_delta = _str_t                                            +\
                           r'(?P<hours>'   + _str_h24 + r')'                  +\
                           r'(?P<minutes>' + _str_MM  + r')'                  +\
                           r'(?P<seconds>' + _str_MM  + r')'  + r'\s*'        +\
                           r'(?P<gmt_delta>' + _str_gmt_delta + r')'

# decipher the gmt_delta components
_str_gmt = r'(GMT|UTC)?(?P<gmt_sign>'+ r'[-+]' + r')'          +\
           r'(?P<gmt_hours>' + _str_h24 + r')'  + r':?'        +\
           r'(' + r'(?P<gmt_minutes>' + _str_MM + r')' + r')?'
_regex_gmt = re.compile(_str_gmt)

_regex_h24ms_with_gmt_delta = re.compile(_str_h24ms_with_gmt_delta, re.IGNORECASE)

# hour, minutes, seconds, and fraction
_str_h24msf = _str_t                                           +\
             r'(?P<hours>'   + _str_h24  + r')' + _str_sep     +\
             r'(?P<minutes>' + _str_MM   + r')' + _str_sep     +\
             r'(?P<seconds>' + _str_MM   + r')'                +\
             r'(?P<frac>'    + _str_frac + r')'
_regex_h24msf = re.compile(_str_h24msf)


# ISO8601 formats:
#
# hh is zero-padded 00-24
# mm is zero-padded 00-59
# ss is zero-padded 00-60 (60 means leap second)

# <time>
#     hh
#     hh:mm or hhmm
#     hh:mm:ss or hhmmss
#     hh:mm:ss.\d+  or hhmmss.\d+ (any number of fractional digits)

# time zone designators
# <time>Z
# <time>+-hh:mm
# <time>+-hhmm
# <time>+-hh

_str_iso_hh = r'([01][0-9]|2[0-4])'
_str_iso_mm = r'[0-5][0-9]'
_str_iso_ss = r'([0-5][0-9]|60)'

_str_iso_zone_hm = r'(?P<gmt_hours>' + _str_iso_hh + r')'                    +\
                   r'(:?' + r'(?P<gmt_minutes>' + _str_iso_mm + r'))?'

_str_iso_zone = r'((?P<timezone>Z)|'                                         +\
                r'(?P<gmt_sign>[-+])' + _str_iso_zone_hm + r')'

# note the essential negative lookahead in these
_str_iso_hh_only = r'\b(?P<hours>' + _str_iso_hh + r'(?!\d))'     +\
                   r'((?P<gmt_delta>' + _str_iso_zone + r'))?'

_str_iso_hhmm_only = r'\b(?P<hours>' + _str_iso_hh + r')'         +\
                     r'(?P<minutes>' + _str_iso_mm + r'(?!\d))'   +\
                     r'((?P<gmt_delta>' + _str_iso_zone + r'))?'

_str_iso_hms = r'\b(?P<hours>'  + _str_iso_hh + r'):?'                       +\
               r'((?P<minutes>' + _str_iso_mm + r')):?'                      +\
               r'((?P<seconds>' + _str_iso_ss + r'))'                        +\
               r'((?P<frac>'    + r'\.\d+'   + r'))?'

_str_iso_time = _str_iso_hms + r'((?P<gmt_delta>' + _str_iso_zone + r'))?'

_regex_iso_hh   = re.compile(_str_iso_hh_only)
_regex_iso_hhmm = re.compile(_str_iso_hhmm_only)
_regex_iso_time = re.compile(_str_iso_time)

_regexes = [
    _regex_iso_hhmm,             # 0
    _regex_iso_hh,               # 1
    _regex_iso_time,             # 2
    _regex_h24ms_with_gmt_delta, # 3
    _regex_h24ms_with_timezone,  # 4
    _regex_h24ms_no_colon,       # 5
    _regex_h24m_no_colon,        # 6
    _regex_h12msf_am_pm,         # 7
    _regex_h12ms_am_pm,          # 8
    _regex_h12m_am_pm,           # 9
    _regex_h12_am_pm,            # 10
    _regex_h24msf,               # 11
    _regex_h24ms,                # 12
    _regex_h24m,                 # 13
    _regex_h12m,                 # 14
]

# match (), {}, and []
_str_brackets = r'[(){}\[\]]'
_regex_brackets = re.compile(_str_brackets)

_CANDIDATE_FIELDS = ['start', 'end', 'match_text', 'regex']
_Candidate = namedtuple('_Candidate', _CANDIDATE_FIELDS)


###############################################################################
def enable_debug():

    global _TRACE
    _TRACE = True


###############################################################################
def _has_overlap(a1, b1, a2, b2):
    """
    Determine if intervals [a1, b1) and [a2, b2) overlap at all.
    """

    assert a1 <= b1
    assert a2 <= b2
    
    if b2 <= a1:
        return False
    elif a2 >= b1:
        return False
    else:
        return True

###############################################################################
def _remove_overlap(candidates):
    """
    Given a set of match candidates, resolve into nonoverlapping matches.
    Take the longest match at any given position.

    ASSUMES that the candidate list has been sorted by matching text length,
    from longest to shortest.
    """

    if _TRACE:
        print('called _remove_overlap...')
    
    results = []
    overlaps = []
    indices = [i for i in range(len(candidates))]

    i = 0
    while i < len(indices):

        if _TRACE:
            print('\tstarting indices: {0}'.format(indices))

        index_i = indices[i]
        start_i = candidates[index_i].start
        end_i   = candidates[index_i].end
        len_i   = end_i - start_i

        overlaps.append(i)
        candidate_index = index_i

        j = i+1
        while j < len(indices):
            index_j = indices[j]
            start_j = candidates[index_j].start
            end_j   = candidates[index_j].end
            len_j   = end_j - start_j

            # does candidate[j] overlap candidate[i] at all
            if _has_overlap(start_i, end_i, start_j, end_j):
                if _TRACE:
                    print('\t\t{0} OVERLAPS {1}, lengths {2}, {3}'.
                          format(candidates[index_i].match_text,
                                 candidates[index_j].match_text,
                                 len_i, len_j))
                overlaps.append(j)
                # keep the longest match at any overlap region
                if len_j > len_i:
                    start_i = start_j
                    end_i   = end_j
                    len_i   = len_j
                    candidate_index = index_j
            j += 1

        if _TRACE:
            print('\t\t\twinner: {0}'.
                  format(candidates[candidate_index].match_text))
            print('\t\t\tappending {0} to results'.
                  format(candidates[candidate_index].match_text))
            
        results.append(candidates[candidate_index])

        if _TRACE:
            print('\t\toverlaps: {0}'.format(overlaps))
        
        # remove all overlaps
        new_indices = []
        for k in range(len(indices)):
            if k not in overlaps:
                new_indices.append(indices[k])
        indices = new_indices

        if _TRACE:
            print('\t\tindices after removing overlaps: {0}'.format(indices))
        
        if 0 == len(indices):
            break

        # start over
        i = 0
        overlaps = []

    return results


###############################################################################
def _clean_sentence(sentence):
    """
    Do some preliminary processing on the sentence.
    """

    # erase [], {}, or () from the sentence
    sentence = _regex_brackets.sub(' ', sentence)

    return sentence


###############################################################################
def run(sentence):
    """

    Find time expressions in the sentence by attempting to match all regexes.
    Avoid matching sub-expressions of already-matched strings. Returns a JSON
    array containing info on each date found.
    
    """    

    results    = [] # TimeValue namedtuple results
    candidates = [] # potential matches, need overlap resolution to confirm

    original_sentence = sentence
    sentence = _clean_sentence(sentence)

    if _TRACE:
        print('original: {0}'.format(original_sentence))
        print(' cleaned: {0}'.format(sentence))
        
    for regex_index, regex in enumerate(_regexes):
        iterator = regex.finditer(sentence)
        for match in iterator:
            match_text = match.group()
            if _TRACE:
                print('[{0:2}]: MATCH TEXT: ->{1}<-'.
                      format(regex_index, match_text))
            start = match.start()
            end   = match.end()
            candidates.append( _Candidate(start, end, match_text, regex))

    # sort the candidates in descending order of length, which is needed for
    # one-pass overlap resolution later on
    candidates = sorted(candidates, key=lambda x: x.end-x.start, reverse=True)

    if _TRACE:
        print('\tCandidate matches: ')
        index = 0
        for c in candidates:
            print('\t[{0:2}]\t[{1},{2}): {3}'.
                  format(index, c.start, c.end, c.match_text, c.regex))
            index += 1
        print()

    pruned_candidates = _remove_overlap(candidates)

    if _TRACE:
        print('\tcandidates count after overlap removal: {0}'.
              format(len(pruned_candidates)))
        print('Result matches: ')
        for c in pruned_candidates:
            print('\t\t[{0},{1}): {2}'.format(c.start, c.end, c.match_text))
        print()

    for pc in pruned_candidates:

        # used the saved regex to match the saved text again
        match = pc.regex.match(pc.match_text)
        assert match

        int_hours         = EMPTY_FIELD
        int_minutes       = EMPTY_FIELD
        int_seconds       = EMPTY_FIELD
        frac_seconds      = EMPTY_FIELD
        am_pm             = EMPTY_FIELD
        timezone          = EMPTY_FIELD
        gmt_delta         = EMPTY_FIELD
        gmt_delta_sign    = EMPTY_FIELD
        gmt_delta_hours   = EMPTY_FIELD
        gmt_delta_minutes = EMPTY_FIELD

        for k,v in match.groupdict().items():
            if v is None:
                continue
            if 'hours' == k:
                int_hours = int(v)
            elif 'minutes' == k:
                int_minutes = int(v)
            elif 'seconds' == k:
                int_seconds = int(v)
            elif 'frac' == k:
                # leave as a string; conversion needs to handle leading zeros
                frac_seconds = v[1:]
            elif 'am_pm' == k:
                if -1 != v.find('a') or -1 != v.find('A'):
                    am_pm = STR_AM
                else:
                    am_pm = STR_PM
            elif 'timezone' == k:
                timezone = v
                if 'Z' == timezone:
                    timezone = 'UTC'
            elif 'gmt_delta' == k:
                gmt_delta = v    
                match_gmt = _regex_gmt.search(v)
                if match_gmt:
                    for k2,v2 in match_gmt.groupdict().items():
                        if v2 is None:
                            continue
                        if 'gmt_sign' == k2:
                            gmt_delta_sign = v2
                        elif 'gmt_hours' == k2:
                            gmt_delta_hours = int(v2)
                        elif 'gmt_minutes' == k2:
                            gmt_delta_minutes = int(v2)

        meas = TimeValue(
            text = pc.match_text,
            start = pc.start,
            end = pc.end,
            hours = int_hours,
            minutes = int_minutes,
            seconds = int_seconds,
            fractional_seconds = frac_seconds,
            am_pm = am_pm,
            timezone = timezone,
            gmt_delta_sign = gmt_delta_sign,
            gmt_delta_hours = gmt_delta_hours,
            gmt_delta_minutes = gmt_delta_minutes
        )
        results.append(meas)

    # sort results to match order of occurrence in sentence
    results = sorted(results, key=lambda x: x.start)
    
    # convert to list of dicts to preserve field names in JSON output
    return json.dumps([r._asdict() for r in results], indent=4)


###############################################################################
def get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)

