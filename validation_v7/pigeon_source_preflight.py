#!/usr/bin/env python3
"""Outcome-blind source/schema preflight of public 5-Hz pigeon pair GPS archive.

This script does not inspect coordinate, movement, or prediction outcomes.
DOI 10.5061/dryad.53f4b, Zenodo record 5010830, CC0.
The complete original ZIP is downloaded into memory, checksum-gated and NOT saved or uploaded.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from hashlib import md5, sha256
import json
from pathlib import Path, PurePosixPath
import re
from urllib.request import Request, urlopen
from zipfile import ZipFile, BadZipFile
from io import BytesIO
import csv

SOURCE_URL = 'https://zenodo.org/api/records/5010830/files/GPS_tracks.zip/content'
EXPECTED_BYTES = 35052731
EXPECTED_MD5 = '8c8e95641182363ea7ad6d0a9a50a3b1'
MAX_MEMBERS = 10000
MAX_UNCOMPRESSED_BYTES = 1_000_000_000
PAIR_PHASE = '2_demonstrator_observer_paired_releases'
PAIR_PATTERN = re.compile(r'^([A-Za-z]\d{2})([A-Za-z]\d{2})_(\d+)\.csv$', re.I)
MIN_MATCHED_PAIR_EPISODES = 8


def verify(data: bytes) -> dict:
    if len(data) != EXPECTED_BYTES:
        raise ValueError('STOP_SOURCE_SIZE_CHANGED')
    if md5(data).hexdigest() != EXPECTED_MD5:
        raise ValueError('STOP_SOURCE_MD5_CHANGED')
    return {'source_bytes': len(data), 'md5_verified': True, 'md5': EXPECTED_MD5,
            'sha256': sha256(data).hexdigest()}


def get_data() -> bytes:
    req = Request(SOURCE_URL, headers={'User-Agent':'zuizui0223-boids-v7-structural-preflight/1.0'})
    with urlopen(req, timeout=180) as f:
        return f.read()


def inspect(data: bytes, *, require_source_verification=True) -> dict:
    integrity = verify(data) if require_source_verification else {'verified': False}
    with ZipFile(BytesIO(data)) as arc:
        members = [m for m in arc.infolist() if not m.is_dir()]
        if len(members) > MAX_MEMBERS or sum(m.file_size for m in members) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError('STOP_ZIP_VOLUME_EXCESS')
        csvs = [m for m in members if m.filename.lower().endswith('.csv')]
        phases = Counter()
        phase_headings = defaultdict(Counter)
        paired = defaultdict(list)
        invalid_names=[]
        header_examples={}
        for item in csvs:
            pp=PurePosixPath(item.filename)
            if '..' in pp.parts or pp.is_absolute():
                raise ValueError('STOP_UNSAFE_ZIP_PATH')
            phase = next((p for p in pp.parts if p.startswith(('1_', '2_', '3_'))), 'unknown')
            phases[phase] += 1
            # Only the CSV header is parsed; the 12k-byte buffer is searched
            # solely for CR/LF line endings (historical GPS files may use CR-only).
            with arc.open(item, 'r') as s:
                header_probe=s.read(12001)
            delimiters=[pos for marker in (b'\r',b'\n') if (pos := header_probe.find(marker))>=0]
            if delimiters:
                header_bytes=header_probe[:min(delimiters)]
            elif len(header_probe)>12000:
                raise ValueError(f'STOP_BAD_HEADER_NO_CR_LF_WITHIN_12000:{item.filename}')
            else:
                # A header-only file may end without a newline.
                header_bytes=header_probe
            cols=next(csv.reader([header_bytes.decode('utf-8-sig',errors='replace')]),[])
            normalized=tuple(c.strip() for c in cols)
            phase_headings[phase][normalized] += 1
            if phase not in header_examples:
                header_examples[phase] = list(normalized)
            if PAIR_PHASE in pp.parts:
                m=PAIR_PATTERN.fullmatch(pp.name)
                if m is None:
                    invalid_names.append(item.filename)
                else:
                    bird,other,release=m.group(1).upper(),m.group(2).upper(),int(m.group(3))
                    # Site from folder structure, not unknown biological response.
                    parent='/' .join(pp.parts[:pp.parts.index(PAIR_PHASE)])
                    key=(parent,*sorted((bird,other)),release)
                    paired[key].append({'tracked':bird,'mate':other,'file':item.filename})
        matched = sorted((key, vals) for key,vals in paired.items() if len(vals)==2 and {v['tracked'] for v in vals} == set(key[1:3]))
        notmatched=sorted((key,len(vals)) for key,vals in paired.items() if (key,vals) not in matched)
        status='PASS_HEADER_AND_PAIR_NAMES_ONLY' if len(matched)>=MIN_MATCHED_PAIR_EPISODES else 'STOP_INSUFFICIENT_MATCHED_PAIRED_FILES'
        return {'status':status, 'source':{'record_url':'https://zenodo.org/records/5010830','doi':'10.5061/dryad.53f4b','direct_url':SOURCE_URL,**integrity},
            'archive':{'non_directory_files':len(members), 'csv_files':len(csvs),
                       'phase_csv_counts':dict(sorted(phases.items())),
                       'phase_header_examples':header_examples,
                       'phase_header_variants':{k:len(v) for k,v in sorted(phase_headings.items())}},
            'paired_phase':{'phase_name':PAIR_PHASE,'filename_pattern':PAIR_PATTERN.pattern,
                           'matched_dual_tracker_episodes':len(matched),
                           'unique_site_pair_release_keys':len(paired),
                           'unmatched_group_count':len(notmatched),
                           'nonconforming_filename_count':len(invalid_names),
                           'sample_matching_public_filenames':[v[0]['file'] for _,v in matched[:3]],
                           'sample_nonconforming_public_filenames':invalid_names[:3]},
            'interpretation':'Structure only; no source coordinates, time-series statistics, fitted parameters, synthetic performance or biological result examined.',
            'reproduction_unit_note':'Matched episode is a distinct flight, but the same bird/pair may recur; future inference must use bird- or pairing-cluster splits where metadata permit.',
            'possible_leakage_note':'Two filenames identifying one paired flight are not two independent replicates.'}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,help='optional local source ZIP; still exact MD5/size validated')
    ap.add_argument('--out',type=Path,default=Path('validation_v7/results/pigeon_source_schema.json'))
    args=ap.parse_args()
    try:
        out=inspect(args.source.read_bytes() if args.source else get_data())
    except (ValueError,OSError,BadZipFile,UnicodeError,TimeoutError) as e:
        print(f'STOP_V7_SOURCE_PREFLIGHT {type(e).__name__}: {e}')
        return 2
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0 if out['status'].startswith('PASS') else 3

if __name__=='__main__':
    raise SystemExit(main())
