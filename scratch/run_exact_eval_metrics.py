import sys
import os

sys.path.insert(0, ".")
from evaluation.injection_eval import run_evaluation

res = run_evaluation()
print("Run evaluation finished.")
iv = res["incremental_value"]
print("Incremental Value:")
for k, v in iv.items():
    if isinstance(v, dict):
        print(f"  {k}: rec={v['recall']:.2f}%, sil_rec={v['silent_recall']:.2f}%, nonsil_rec={v['nonsilent_recall']:.2f}%, fp={v['fp_count']}, fpr={v['fpr']:.2f}%, prec={v['precision']:.2f}%, f1={v['f1']:.2f}%")
    else:
        print(f"  {k}: {v}")

print("Spoofed count:", len(res["flight_df"][res["flight_df"]["is_spoofed_gt"] == True]))
print("Clean count:", len(res["flight_df"][res["flight_df"]["is_clean_control"] == True]))
sp_df = res["flight_df"][res["flight_df"]["is_spoofed_gt"] == True]
print("Silent count:", (sp_df["is_silent"] == True).sum())
print("Non-silent count:", (sp_df["is_silent"] == False).sum())
