"""Planning-only bandwidth, queue and BOM arithmetic. No robot-performance claims."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def capacity(nodes, fps, image_bytes, link_mbps, service_ms, reserved=0.2, meta_bytes=512):
    if nodes < 1 or fps <= 0 or image_bytes <= 0 or link_mbps <= 0 or service_ms <= 0:
        raise ValueError("All size/rate/service values must be positive")
    if not 0 <= reserved < 1 or meta_bytes < 0:
        raise ValueError("Invalid reservation/metadata")
    payload = image_bytes + meta_bytes
    usable = link_mbps * 1e6 * (1 - reserved)
    offered = nodes * fps * payload * 8
    arrivals = nodes * fps
    service = service_ms / 1000
    rho = arrivals * service
    stable = offered < usable and rho < 1
    # M/D/1 applies only to an assumed Poisson input and deterministic server;
    # this is host-queue sensitivity, not a wireless/robotic deadline guarantee.
    host_wq = rho * service / (2 * (1 - rho)) if rho < 1 else None
    return dict(nodes=nodes, fps_per_node=fps, image_bytes=image_bytes, metadata_bytes=meta_bytes,
                link_mbps=link_mbps, media_budget_mbps=usable/1e6,
                offered_mbps=offered/1e6, link_load=offered/usable,
                service_ms=service_ms, host_load=rho,
                max_fps_link=usable/(8*payload*nodes),
                max_fps_host=1/(service*nodes),
                host_wq_ms=None if host_wq is None else host_wq*1000,
                stable_under_assumptions=stable)

def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def main():
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    inputs = {"status":"ASSUMPTIONS_NOT_MEASUREMENTS","image_bytes":28000,
              "historical_context":"AstraPlusCar PHONE_API mentions about 28 KB preview JPEG; this project must remeasure",
              "metadata_bytes":512,"reserved_link_fraction":0.2,
              "aggregate_link_mbps":[2,8,20],"host_service_ms":[10,30,50],
              "nodes":[1,3,6,10],"fps_per_node":[1,2,5,10],
              "queue_assumption":"M/D/1 Poisson arrivals; not a bursty Wi-Fi model"}
    (out/"capacity_assumptions.json").write_text(json.dumps(inputs,ensure_ascii=False,indent=2))
    rows = [capacity(n, f, 28000, b, s) for n in inputs["nodes"]
            for f in inputs["fps_per_node"] for b in inputs["aggregate_link_mbps"]
            for s in inputs["host_service_ms"]]
    write_csv(out/"capacity_sweep.csv", rows)
    budget = json.loads((ROOT/"planning/budget_inputs.json").read_text())
    low = sum(x["low"] for x in budget["node_items"])
    high = sum(x["high"] for x in budget["node_items"])
    budgets=[]
    for n in budget["scales"]:
        spares=math.ceil(n*budget["spare_fraction"])
        for host in ["reuse","new"]:
            lo=(n+spares)*low+budget["shared_low"]+(budget["host_reuse"] if host=="reuse" else budget["host_new_low"])
            hi=(n+spares)*high+budget["shared_high"]+(budget["host_reuse"] if host=="reuse" else budget["host_new_high"])
            budgets.append(dict(active_nodes=n,spare_nodes=spares,host=host,unit_low=low,unit_high=high,
                                subtotal_low=lo,subtotal_high=hi,
                                total_low=math.ceil(lo*(1+budget["cash_contingency"])),
                                total_high=math.ceil(hi*(1+budget["cash_contingency"])),
                                kind="planning estimate, not quotation"))
    write_csv(out/"budget_scenarios.csv",budgets)
    print(json.dumps({"capacity_rows":len(rows),"node_cost_low":low,"node_cost_high":high,
                      "example_10_nodes_5fps_8Mbps_30ms":capacity(10,5,28000,8,30),
                      "budgets":budgets},ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
