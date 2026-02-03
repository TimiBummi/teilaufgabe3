**Project Structure**
analyzer/
    analyzer.py       # Analyzer class
    types.py          # RISK, GAIN value objects
file_reader.py        # FileReader.read_ods
main.py               # Run analysis
requirements.txt      # Dependencies

**Setup**
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

**Usage**
python main.py

Computes contribution_margin = profit - costs and margin_per_hour = contribution_margin / processing_time_hr

Computes client risk & gain

Prints client summaries, bad orders, and margin correlations

Select orders for a shift using greedy heuristic:

Orders sorted by margin per hour, added until total processing time ≤ 800h.

Print the selected shift orders and relevant metrics.

**Keynotes / Assumptions**

RISK and GAIN values: 1–10 (dataclass(frozen=True))

_calculate_risk: exponential mapping saturates early (~40–50% risk → 10)

_calculate_gain: scaled relative to client-local percentiles, not global

analyze_margin(): Pearson correlation → linear association only, not causation

print_client_risk_and_gain(): thresholds (risk ≥ 6, variance ≥ 60, gain ≥ 6) are heuristic

analyze_orders(): risk threshold >15% in code, printed explanation uses 50% (conceptual)

margin_per_hour assumes processing_time_hr > 0

bad_orders must be computed before print_bad_orders()

best_orders must be computed before print_best_orders()

This tool is exploratory; treat thresholds and correlations as guidance, not prescriptions.