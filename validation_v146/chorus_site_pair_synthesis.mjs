#!/usr/bin/env node
// v146 POSTHOC DESCRIPTIVE audit; original v145 input is immutable. No raw animal data.
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const here=path.dirname(fileURLToPath(import.meta.url));
function synthesizeV146(source) {
  const all=source.all_screened_source_test_results;
  if(!Array.isArray(all)||all.length!==91||source.source_screened_family.total_related_tests!==91)throw Error("source 91-family gate failed");
  if(source.source_screened_family.same_hour_chorus_presence!==32)throw Error("source 32 presence gate failed");
  const rows=all.filter(x=>x.test_type==="same_hour_presence");
  if(rows.length!==32)throw Error("observed same-hour family count differs from source");
  const r6=x=>Math.round(x*1e6)/1e6;
  const median=xs=>{const z=[...xs].sort((a,b)=>a-b);return z.length%2===1?z[(z.length-1)/2]:(z[z.length/2-1]+z[z.length/2])/2};
  const by=new Map(),keys=new Set();
  for(const x of rows){
    if(!(x.expected_under_restricted_day_shift>0))throw Error("unsupported expected overlap");
    const pair=x.chorus_A+" × "+x.chorus_B, key=pair+"|"+x.site;
    if(keys.has(key))throw Error("duplicate source site-pair");keys.add(key);
    if(!by.has(pair))by.set(pair,[]);
    by.get(pair).push(x);
  }
  const pairs=[...by.entries()].sort((a,b)=>a[0].localeCompare(b[0],"en")).map(([pair,rr])=>{
    rr=[...rr].sort((a,b)=>a.site.localeCompare(b.site,"en"));
    const obs=rr.reduce((a,x)=>a+x.observed,0),exp=rr.reduce((a,x)=>a+x.expected_under_restricted_day_shift,0);
    const regionRows={};
    for(const x of rr){const region=x.site.slice(0,2);(regionRows[region]??=[]).push(x);}
    return {
      acoustic_type_pair:pair,
      site_count:rr.length,
      above_expected_sites:rr.filter(x=>x.observed_over_expected>1).length,
      below_expected_sites:rr.filter(x=>x.observed_over_expected<1).length,
      exactly_equal_sites:rr.filter(x=>x.observed_over_expected===1).length,
      median_site_observed_expected_ratio:r6(median(rr.map(x=>x.observed_over_expected))),
      total_observed_hours_descriptive:obs,
      total_expected_hours_descriptive:r6(exp),
      sum_observed_over_sum_expected_descriptive:r6(obs/exp),
      holm_flags_in_full_91_family_sites:rr.filter(x=>x.Holm_familywise_91_comparison_adjusted_p<=0.05).map(x=>x.site),
      sanctuary_prefix_descriptive:Object.fromEntries(Object.entries(regionRows).sort((a,b)=>a[0].localeCompare(b[0],"en")).map(([k,v])=>[k,{sites:v.length,above:v.filter(x=>x.observed_over_expected>1).length,below:v.filter(x=>x.observed_over_expected<1).length}])),
      site_details:rr.map(x=>({site:x.site,ratio:r6(x.observed_over_expected),observed:x.observed,expected:r6(x.expected_under_restricted_day_shift),holm_91_p:r6(x.Holm_familywise_91_comparison_adjusted_p)}))
    };
  });
  const pA=rows.filter(x=>x.chorus_A==="Bocaccio"&&x.chorus_B==="UF440");
  const pB=rows.filter(x=>x.chorus_A==="Bocaccio"&&x.chorus_B==="White Seabass");
  const matched=pA.flatMap(a=>{const b=pB.find(x=>x.site===a.site);return b?[{site:a.site,UF440_ratio:r6(a.observed_over_expected),WhiteSeabass_ratio:r6(b.observed_over_expected),paired_log_ratio_difference:r6(Math.log(a.observed_over_expected/b.observed_over_expected))}]:[]}).sort((a,b)=>a.site.localeCompare(b.site,"en"));
  return {
    analysis_id:"v146_frozen_v145_saved_source_pair_site_descriptive_audit",
    input_v145_source_json:"validation_v145/results/joint_91_constrained_null_family.json",
    source_workbooks_individual_sha256_matched:source.source_workbooks_individual_sha256_matched,
    comparison_family:{all_related_tests:all.length,same_hour_presence_tests:rows.length,full_family_holm_flags:all.filter(x=>x.Holm_familywise_91_comparison_adjusted_p<=0.05).length,holm_flag_unique_site_count:new Set(all.filter(x=>x.Holm_familywise_91_comparison_adjusted_p<=0.05).map(x=>x.site)).size,site_codes:[...new Set(all.map(x=>x.site))].sort()},
    all_pair_groups:pairs,
    exploratory_matched_site_bocaccio_uf440_vs_white_seabass:{
      n_shared_sites:matched.length,
      positive_relative_log_differences:matched.filter(x=>x.paired_log_ratio_difference>0).length,
      negative_relative_log_differences:matched.filter(x=>x.paired_log_ratio_difference<0).length,
      median_relative_log_difference:r6(median(matched.map(x=>x.paired_log_ratio_difference))),
      sites:matched
    },
    analysis_class:"POSTHOC_DESCRIPTION_NO_NEW_INFERENCE",
    biological_social_interaction:"NOT_IDENTIFIED",
    unique_tide_solar_biological_interaction:"NOT_IDENTIFIED",
    independent_coast_meta_effect:"NOT_ESTIMATED",
    cautions:["Chorus is an acoustic annotation, not fish identities or independent ecological behavior","Site codes are not independent sanctuary/coast replicates","Clock/season/day-shift controls do not remove shared tidal, thermal, upwelling or audibility confounding","Pair directions chosen for discussion after inspecting outcomes, no new p-values","Observed-over-expected ratios from different sites are not meta-effect sizes with standard errors"]
  };
}
const source=JSON.parse(fs.readFileSync(path.join(here,'../validation_v145/results/joint_91_constrained_null_family.json'),'utf8'));
const output=synthesizeV146(source);
const savedPath=path.join(here,'results/chorus_site_pair_directions_v146.json');
if (process.argv.includes('--check')) {
  const saved=JSON.parse(fs.readFileSync(savedPath,'utf8'));
  if(JSON.stringify(saved)!==JSON.stringify(output)) { console.error('SOURCE RESULT MISMATCH'); process.exit(1); }
  console.log('PASS: 91-family source, 32 presence rows, exact saved v146 output');
} else { console.log(JSON.stringify(output,null,2)); }
