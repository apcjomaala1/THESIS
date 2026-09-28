"""Apply preselected validation-F2 thresholds to original saved test scores.

This is a revised-policy analysis of an already evaluated partition. It does not
train, infer, search thresholds on test, modify the final gate, or replace any
pipeline artifact. Outputs remain in this manuscript-analysis directory.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import fbeta_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIPELINE = ROOT / "grooming-detector/grooming-detector-trajectory-pipeline"
RUNS = PIPELINE / "revised_runs"
sys.path.insert(0, str(PIPELINE))
from revised_pipeline.metrics import conversation_metrics
from analyze_validation_f1 import select_fbeta

SPECS = [
    ("keyword", "Keyword rule"),
    ("raw_layer1", "Maximum Layer 1"),
    ("weighted", "Weighted scorer"),
    ("lstm_trajectory7", "Primary LSTM"),
    ("lstm_enhanced775", "Enhanced LSTM"),
]
TRACKED = ["precision", "recall", "specificity", "f1", "f0_5", "f2"]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rates(counts):
    tp, fp, fn, tn = np.moveaxis(counts.astype(float), -1, 0)
    def divide(a, b):
        return np.divide(a, b, out=np.zeros_like(a), where=b != 0)
    return dict(precision=divide(tp,tp+fp), recall=divide(tp,tp+fn),
                specificity=divide(tn,tn+fp), f1=divide(2*tp,2*tp+fp+fn),
                f0_5=divide(1.25*tp,1.25*tp+fp+.25*fn),
                f2=divide(5*tp,5*tp+fp+4*fn))

def interval(values):
    return dict(lower=float(np.quantile(values,.025)),
                upper=float(np.quantile(values,.975)), valid_replicates=len(values))

def main():
    validation_path = HERE / "validation_f1_comparison.json"
    selection = json.loads(validation_path.read_text(encoding="utf-8"))
    assert selection["test_data_read"] is False
    validation = {r["method"]:r for r in selection["results"]}
    # Verify thresholds from validation BEFORE reading saved test outcomes.
    for relative, expected in selection["input_hashes"].items():
        assert digest(ROOT / relative) == expected, relative
    column = {"Maximum Layer 1":"raw_layer1_score","Weighted scorer":"weighted_score"}
    validation_ids = None
    for key, name in SPECS:
        v = validation[name]
        frame = pd.read_csv(ROOT/v["score_source"], dtype={"conversation_id":str},
                            float_precision="round_trip")
        ids = set(frame.conversation_id)
        assert len(ids) == len(frame) == 1827
        if validation_ids is None: validation_ids = ids
        assert ids == validation_ids
        t, m = select_fbeta(frame.label.to_numpy(),
                            frame[column.get(name,"score")].to_numpy(), 2)
        assert t == v["f2_selected_threshold"]
        for metric in TRACKED:
            assert abs(m[metric]-v["f2_policy"][metric]) < 1e-12
    pred_path = RUNS/"final_results/per_conversation_predictions.csv"
    original_path = RUNS/"final_results/final_evaluation.json"
    index_path = RUNS/"final_cache/final_test/index.csv"
    protected = [validation_path, pred_path, original_path, index_path,
                 RUNS/"frozen_protocol.json",
                 *[ROOT/p for p in selection["input_hashes"]]]
    before = {str(p.relative_to(ROOT)):digest(p) for p in protected}
    original = json.loads(original_path.read_text(encoding="utf-8"))
    assert digest(pred_path) == original["predictions_sha256"]
    data = pd.read_csv(pred_path, dtype={"conversation_id":str,"component_id":str},
                       float_precision="round_trip")
    assert len(data) == data.conversation_id.nunique() == 1862
    assert not (set(data.conversation_id) & validation_ids)
    y = data.label.to_numpy(dtype=np.int8)
    assert set(y) == {0,1} and int(y.sum()) == 44
    components, group = np.unique(data.component_id, return_inverse=True)
    assert len(components) == 1800
    results, counts = {}, np.zeros((len(components),len(SPECS),4),dtype=np.int64)
    old_counts = np.zeros_like(counts)
    predictions = {}
    for j, (key,name) in enumerate(SPECS):
        s = data[key+"_score"].to_numpy()
        old = original["metrics"][key]["point_estimate"]
        reproduced = conversation_metrics(y,s,old["threshold"])
        for metric,value in old.items():
            assert np.isclose(reproduced[metric],value,rtol=0,atol=1e-12), (key,metric)
        assert np.array_equal(s>=old["threshold"],data[key+"_prediction"].to_numpy())
        t = validation[name]["f2_selected_threshold"]
        m = conversation_metrics(y,s,t)
        m["f2"] = float(fbeta_score(y,s>=t,beta=2))
        assert m["pr_auc"] == old["pr_auc"] and m["roc_auc"] == old["roc_auc"]
        pred = predictions[key] = s>=t
        for target,p in [(counts,pred),(old_counts,s>=old["threshold"])]:
            cells = np.stack([p&(y==1),p&(y==0),(~p)&(y==1),(~p)&(y==0)],axis=1)
            np.add.at(target[:,j,:],group,cells)
        results[key] = dict(name=name, validation=validation[name]["f2_policy"],
                            test=m, original_test=old, confidence_intervals={})
    # Identical paired component draws for all methods; no row-wise resampling.
    rng = np.random.default_rng(42)
    boot = {k:np.empty((2000,len(SPECS))) for k in TRACKED}
    old_boot = {k:np.empty((2000,len(SPECS))) for k in TRACKED}
    for b in range(2000):
        chosen = rng.choice(len(components), size=len(components), replace=True)
        for target,source in [(boot,counts),(old_boot,old_counts)]:
            for metric,values in rates(source[chosen].sum(axis=0)).items():
                target[metric][b] = values
        if b < 3:
            positions = np.concatenate([np.flatnonzero(group==c) for c in chosen])
            for j,(key,name) in enumerate(SPECS):
                direct = conversation_metrics(y[positions],data[key+"_score"].to_numpy()[positions],
                                               results[key]["test"]["threshold"])
                direct["f2"] = float(fbeta_score(y[positions],predictions[key][positions],beta=2))
                for metric in TRACKED:
                    assert np.isclose(direct[metric],boot[metric][b,j],atol=1e-12)
    for j,(key,name) in enumerate(SPECS):
        ci = results[key]["confidence_intervals"]
        for metric in TRACKED:
            ci[metric] = interval(boot[metric][:,j])
            if metric != "f2":
                old_ci = original["metrics"][key]["confidence_intervals"]["intervals"][metric]
                reproduced = interval(old_boot[metric][:,j])
                for bound in ["lower","upper"]:
                    assert abs(reproduced[bound]-old_ci[bound]) < 1e-12
        for metric in ["pr_auc","roc_auc"]:
            ci[metric] = original["metrics"][key]["confidence_intervals"]["intervals"][metric]
    paired = {}
    for j,(key,name) in enumerate(SPECS):
        if key == "lstm_trajectory7": continue
        d = {}
        for metric in TRACKED:
            d[metric] = interval(boot[metric][:,3]-boot[metric][:,j])
            d[metric]["point_difference"] = results["lstm_trajectory7"]["test"][metric]-results[key]["test"][metric]
        old_pair = original["paired_component_bootstrap_differences"]["lstm_trajectory7_minus_"+key]["differences"]
        for metric in ["pr_auc","roc_auc"]: d[metric] = old_pair[metric]
        paired[key] = d
    index = pd.read_csv(index_path, dtype={"conversation_id":str,"component_id":str})
    assert set(index.conversation_id) == set(data.conversation_id)
    metadata = index.groupby("conversation_id").agg(
        length=("row_id","size"),label=("conversation_label","first"),component=("component_id","first"))
    metadata = metadata.loc[data.conversation_id]
    assert np.array_equal(metadata.label,y)
    assert np.array_equal(metadata.component.to_numpy(),data.component_id.to_numpy())
    lengths = metadata.length.to_numpy()
    p = predictions["lstm_trajectory7"]
    errors = {}
    for name,mask in dict(false_negatives=(~p)&(y==1),false_positives=p&(y==0),true_positives=p&(y==1)).items():
        seq = lengths[mask]
        errors[name] = dict(count=int(mask.sum()), components=int(data.loc[mask,"component_id"].nunique()),
            lengths_sorted=sorted(seq.tolist()), median=float(np.median(seq)),mean=float(np.mean(seq)),
            first_quartile=float(np.quantile(seq,.25)),
            score_min=float(data.loc[mask,"lstm_trajectory7_score"].min()),
            score_max=float(data.loc[mask,"lstm_trajectory7_score"].max()))
    errors["missed_case_details"] = [
        dict(turns=int(lengths[i]),score=float(data.iloc[i]["lstm_trajectory7_score"]),
             detected_by=[key for key,_ in SPECS if predictions[key][i]])
        for i in np.flatnonzero((~p)&(y==1))]
    assert before == {str(p.relative_to(ROOT)):digest(p) for p in protected}
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        status="REVISED_F2_POLICY_ON_PREVIOUSLY_EVALUATED_TEST_SCORES",
        validation_conversations=1827,validation_positive=49,test_conversations=1862,test_positive=44,
        bootstrap=dict(replicates=2000,seed=42,components=1800,level=.95,
                       original_intervals_reproduced=True,
                       scope="Fixed-model fixed-threshold component bootstrap; selection uncertainty not included.",
                       auc_intervals="Reused unchanged original intervals after reproducing scores and metrics."),
        results=results,paired_differences=paired,primary_errors=errors,
        validation_selection_verified_before_test_read=True,test_threshold_search=False,
        training_performed=False,model_inference_performed=False,active_thresholds_replaced=False,
        original_inputs_unchanged=True,input_hashes=before)
    output = HERE/"f2_test_reanalysis.json"
    output.write_text(json.dumps(receipt,indent=2),encoding="utf-8")
    print(json.dumps({k:v["test"] for k,v in results.items()},indent=2))
    print("PAIRED",json.dumps(paired,indent=2))
    print("ERRORS",json.dumps(errors,indent=2))
    print("Receipt:",output)

if __name__ == "__main__":
    main()
