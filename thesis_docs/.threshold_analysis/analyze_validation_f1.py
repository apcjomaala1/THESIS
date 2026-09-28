"""Compare final F0.5/F1/F2 cutoffs using saved validation scores and fixed models.

No model inference, model fitting, feature changes, test-data access, or active
threshold replacement occurs. Only aggregate results are exported.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import fbeta_score

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / 'grooming-detector/grooming-detector-trajectory-pipeline'
RUNS = PIPELINE / 'revised_runs'
sys.path.insert(0, str(PIPELINE))
from revised_pipeline.metrics import conversation_metrics, select_f05_threshold


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_fbeta(labels, scores, beta):
    """Same candidate thresholds/tie-breaks as the original selector, with configurable beta."""
    order = np.argsort(-scores, kind='stable')
    s, y = scores[order], labels[order]
    ends = np.flatnonzero(np.r_[s[:-1] != s[1:], True])
    thresholds = s[ends]
    tp = np.cumsum(y == 1)[ends].astype(float)
    fp = np.cumsum(y == 0)[ends].astype(float)
    positives = int((y == 1).sum())
    precision = tp / (tp + fp)
    recall = tp / positives
    b2 = beta**2
    denominator = b2*precision+recall
    f1 = np.divide((1+b2)*precision*recall, denominator,
                   out=np.zeros_like(precision), where=denominator>0)
    i = max(range(len(thresholds)), key=lambda i: (float(f1[i]), float(recall[i]), float(precision[i]), float(thresholds[i])))
    threshold = float(thresholds[i])
    metrics = conversation_metrics(labels, scores, threshold)
    metrics['f2'] = float(fbeta_score(labels, scores>=threshold, beta=2, zero_division=0))
    # Independently check optimality by counting predictions at every candidate.
    brute = max((1+b2)*int(np.sum((scores>=t)&(labels==1))) /
                (int(np.sum(scores>=t))+b2*positives) for t in np.unique(scores))
    assert abs(float(fbeta_score(labels, scores>=threshold, beta=beta))-brute) < 1e-12
    return threshold, metrics


def main():
    inputs = set()
    specs = []
    for title, search in [('Primary LSTM','lstm_search_trajectory7'),('Enhanced LSTM','lstm_search_enhanced775')]:
        selection_path = RUNS/search/'selection.json'
        selection = json.loads(selection_path.read_text())
        run = (RUNS/search/selection['selected_run']).resolve()
        assert run.is_relative_to((RUNS/search).resolve())
        threshold_path = run/'selected_threshold.json'
        record = json.loads(threshold_path.read_text())
        assert record['selection_partition'] == 'validation'
        assert record['objective'] == 'maximum F0.5'
        inputs.update([selection_path, threshold_path, run/'run_summary.json'])
        specs.append((title, run/'validation_predictions.csv', 'score', 'prediction', record['threshold']))
    comp_path = RUNS/'comparators/run_summary.json'
    comp = json.loads(comp_path.read_text())
    inputs.add(comp_path)
    comp_csv = RUNS/'comparators/validation_predictions.csv'
    specs.extend([
        ('Maximum Layer 1',comp_csv,'raw_layer1_score','raw_layer1_prediction',comp['raw_layer1']['threshold']),
        ('Weighted scorer',comp_csv,'weighted_score','weighted_prediction',comp['weighted']['threshold']),
        ('Keyword rule',RUNS/'keyword/validation_predictions.csv','score','prediction',0.5)
    ])
    inputs.update(s[1] for s in specs)
    before = {str(p.relative_to(ROOT)): digest(p) for p in inputs}
    results = []
    first_labels = None
    for name, csv, score_column, pred_column, threshold in specs:
        frame = pd.read_csv(csv, dtype={'conversation_id':str}, float_precision='round_trip')
        assert not frame['conversation_id'].duplicated().any()
        labels = frame['label'].to_numpy(dtype=np.int8)
        scores = frame[score_column].to_numpy(dtype=float)
        assert len(labels) == 1827 and int(labels.sum()) == 49
        assert set(labels.tolist()) == {0,1} and np.isfinite(scores).all()
        mapping = dict(zip(frame['conversation_id'], frame['label']))
        if first_labels is None: first_labels = mapping
        assert mapping == first_labels, 'Validation populations differ'
        original = conversation_metrics(labels, scores, float(threshold))
        original['f2'] = float(fbeta_score(labels, scores>=threshold, beta=2, zero_division=0))
        assert np.array_equal(scores>=threshold, frame[pred_column].to_numpy().astype(bool)), name
        if name != 'Keyword rule':
            check_threshold, check_metrics = select_f05_threshold(labels, scores)
            assert check_threshold == threshold, (name, check_threshold, threshold)
            assert abs(check_metrics['f0_5']-original['f0_5']) < 1e-12
        selected, proposed = select_fbeta(labels, scores, 1)
        selected_f2, proposed_f2 = select_fbeta(labels, scores, 2)
        assert proposed_f2['f2'] + 1e-12 >= max(original['f2'], proposed['f2'])
        assert proposed_f2['pr_auc'] == original['pr_auc']
        assert proposed_f2['roc_auc'] == original['roc_auc']
        assert proposed['pr_auc'] == original['pr_auc']
        assert proposed['roc_auc'] == original['roc_auc']
        changed = (scores>=threshold) != (scores>=selected)
        results.append({'method':name, 'existing_threshold':float(threshold), 'f1_selected_threshold':selected,
                        'existing_policy':original, 'f1_policy':proposed,
                        'f2_selected_threshold':selected_f2, 'f2_policy':proposed_f2,
                        'f2_validation_decisions_changed':int(((scores>=threshold)!=(scores>=selected_f2)).sum()),
                        'validation_decisions_changed':int(changed.sum()),
                        'new_flags':int(((scores>=selected)&(scores<threshold)).sum()),
                        'removed_flags':int(((scores<selected)&(scores>=threshold)).sum()),
                        'score_source':str(csv.relative_to(ROOT)),
                        'status':'fixed-model validation comparison'})
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in inputs}
    payload = {'created_utc':datetime.now(timezone.utc).isoformat(), 'validation_conversations':1827,
               'validation_positive':49, 'selection_objectives':['maximum validation F1','maximum validation F2'],
               'tie_breaks':['higher recall','higher precision','higher threshold'],
               'results':results,'input_hashes':before,'input_files_unchanged':True,
               'training_performed':False,'model_inference_performed':False,'test_data_read':False,
               'active_thresholds_replaced':False,
               'interpretation':'Selection-set comparison on existing validation scores, not a new held-out performance estimate.',
               'scope':'Final conversation decision cutoff only. Existing feature thresholds, weighted-scorer coefficients, checkpoint selection and learned weights remain fixed.'}
    directory = Path(__file__).resolve().parent
    receipt = directory/'validation_f1_comparison.json'
    receipt.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    lines = ['# F0.5, F1, and F2 Threshold Analysis on Saved Validation Scores','',
             '**Updated:** September 19, 2026',
             '**Population:** 1,827 validation conversations, including 49 positive conversations.','',
             'This analysis selects final conversation cutoffs by F1 and F2 using the already selected models and saved validation scores. It changes no learned weights, feature thresholds, weighted-scorer coefficients, checkpoint choices, active thresholds, or final-test artifacts. Existing cutoffs maximize F0.5 except the fixed binary keyword rule.','',
             '| Method | Policy | Threshold | Precision | Recall | F1 | F0.5 | F2 | TP | FP | FN |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for result in results:
        for policy, key in [('Existing','existing_policy'),('F1-selected','f1_policy'),('F2-selected','f2_policy')]:
            m = result[key]
            lines.append(f"| {result['method']} | {policy} | {m['threshold']:.9f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {m['f0_5']:.4f} | {m['f2']:.4f} | {m['tp']} | {m['fp']} | {m['fn']} |")
    primary = results[0]
    old, new = primary['existing_policy'], primary['f1_policy']
    f2 = primary['f2_policy']
    lines.extend(['','## Primary LSTM result','',
                  f"F1 selects a cutoff of {new['threshold']:.9f}, compared with the existing {old['threshold']:.9f}. This changes {primary['validation_decisions_changed']} validation decisions: {primary['new_flags']} new flags and {primary['removed_flags']} removed flags.",
                  f"Validation true positives change from {old['tp']} to {new['tp']}, false positives from {old['fp']} to {new['fp']}, and false negatives from {old['fn']} to {new['fn']}. No training or model inference was necessary.",'',
                  f"F2 selects {f2['threshold']:.9f}: TP {f2['tp']}, FP {f2['fp']}, FN {f2['fn']}; precision {f2['precision']:.4f}, recall {f2['recall']:.4f}, F2 {f2['f2']:.4f}.",'',
                  '## Interpretation and scope','',
                  '- F2 gives recall greater weight than precision; compare additional detections against additional false alerts.',
                  '- These are validation results used to select the cutoff. They do not establish an improvement on unseen data.',
                  '- PR-AUC and ROC-AUC remain identical because the scores and labels are unchanged.',
                  '- The existing keyword rule is binary with a fixed 0.5 cutoff. Equivalent binary decisions can have different numerical cutoffs.',
                  '- The weighted scorer remains fitted using its original procedure. Its row compares cutoff choices on fixed scores; it is not a globally F1- or F2-refitted comparator.',
                  '- Existing Layer 1 and feature-construction uses of F0.5 remain unchanged. This is not a replacement of every F0.5 selection rule in the pipeline.',
                  '- No final-test data were accessed and no primary manuscript results were replaced. A later analysis on an already-examined test set must be identified accordingly.','',
                  '## Reproduction','',
                  '`python thesis_docs/.threshold_analysis/analyze_validation_f1.py`','',
                  'The JSON receipt records input hashes, aggregate results and verification. The selector checks both F1 and F2 optima against independent exhaustive threshold calculations and sklearn. Saved F0.5 decisions are reproduced before comparison, and all methods use the same validation conversation labels. Existing filenames are retained to keep this comparison in one report.',''])
    report = ROOT/'thesis_docs/F1_THRESHOLD_VALIDATION_ANALYSIS.md'
    report.write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'report':str(report), 'results':results},indent=2))

if __name__ == '__main__':
    main()
