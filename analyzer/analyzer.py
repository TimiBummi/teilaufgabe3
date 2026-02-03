from typing import Tuple, Dict

import numpy as np
import pandas as pd

from analyzer.types import RISK, GAIN


# ---------------------------
# Analyzer
# ---------------------------

class Analyzer:
    def __init__(self, df: pd.DataFrame):
        self.order_df = df.copy()
        self.client_dict: Dict[str, Dict] = {}
        self.bad_orders = None

        self._prepare_columns()

    # -----------------------
    # Preparation
    # -----------------------

    def _prepare_columns(self):
        """
        Add derived columns used throughout the analysis.
        """
        df = self.order_df

        if "contribution_margin" not in df.columns:
            df["contribution_margin"] = df["profit"] - df["costs"]

        if "margin_per_hour" not in df.columns:
            df["margin_per_hour"] = df["contribution_margin"] / df["processing_time_hr"]

    # -----------------------
    # Margin Drivers
    # -----------------------

    def analyze_margin(self):
        """
        Which characteristics drive contribution margin per hour?
        """
        features = [
            "processing_time_hr",
            "costs",
            "profit",
            "risk (in percent)",
        ]

        corr = (
            self.order_df[features + ["margin_per_hour"]]
            .corr()["margin_per_hour"]
            .sort_values(ascending=False)
        )

        return corr

    def print_characteristics(self):
        """
        Print correlation-based characteristics driving margin per hour,
        with short explanations.
        """
        corr = self.analyze_margin()

        print("\n=== Characteristics influencing contribution margin per hour ===\n")

        for feature, value in corr.items():
            if feature == "margin_per_hour":
                continue

            direction = "increases" if value > 0 else "decreases"
            strength = abs(value)

            if strength >= 0.7:
                strength_txt = "strong"
            elif strength >= 0.4:
                strength_txt = "moderate"
            elif strength >= 0.2:
                strength_txt = "weak"
            else:
                strength_txt = "very weak"

            print(
                f"- {feature}: "
                f"{strength_txt} {direction} relationship "
                f"(corr = {value:.2f})"
            )

            # Context-aware explanations
            if feature == "processing_time_hr":
                print(
                    "  → Longer processing time lowers margin per hour "
                    "by construction (time is in the denominator)."
                )

            elif feature == "costs":
                print(
                    "  → Higher costs directly reduce contribution margin."
                )

            elif feature == "profit":
                print(
                    "  → Profit is mechanically linked to margin per hour, "
                    "so correlation is expected."
                )

            elif "risk" in feature.lower():
                print(
                    "  → Risk correlation captures whether risky orders tend "
                    "to pay off in practice."
                )

        print(
            "Note:\n"
            "- Correlation shows association, not causation.\n"
            "- Structural relationships (time, profit) inflate correlations.\n"
            "- Use this as exploratory guidance, not decision logic.\n"
        )

    # -----------------------
    # Risk & Gain
    # -----------------------

    @staticmethod
    def _calculate_risk(client_df: pd.DataFrame) -> Tuple[RISK, float]:
        """
        Expected risk and variance based on 'risk (in percent)' column (percent).
        """
        expected_risk = client_df["risk (in percent)"].mean()
        variance = client_df["risk (in percent)"].var(ddof=0)

        # Map expected risk (0–100%) → 1–10
        score = 1 + 9 * (1 - np.exp(-expected_risk / 20))
        risk_score = int(np.clip(round(score), 1, 10))

        return RISK(risk_score), variance

    @staticmethod
    def _calculate_gain(client_df: pd.DataFrame) -> GAIN:
        """
        Gain driven by average contribution margin per hour.
        """
        avg_mph = client_df["margin_per_hour"].mean()

        # Robust scaling using percentiles
        p10, p90 = np.percentile(client_df["margin_per_hour"], [10, 90])

        if p90 == p10:
            gain_score = 5
        else:
            scaled = (avg_mph - p10) / (p90 - p10)
            gain_score = int(np.clip(np.round(scaled * 9 + 1), 1, 10))

        return GAIN(gain_score)

    # -----------------------
    # Client Analysis
    # -----------------------

    def analyze_client(self):
        """
        Compute risk and gain per client.
        """
        for client_id, client_df in self.order_df.groupby("customer_id"):
            risk, variance = self._calculate_risk(client_df)
            gain = self._calculate_gain(client_df)

            self.client_dict[str(client_id)] = {
                "risk": risk,
                "risk_variance": variance,
                "gain": gain,
                "avg_margin_per_hour": client_df["margin_per_hour"].mean(),
            }

    def print_client_risk_and_gain(self):
        """
        Print client diagnostics with blunt classification.
        """
        for client_id, data in self.client_dict.items():
            gain = data["gain"].value
            risk = data["risk"].value
            variance = data['risk_variance']

            print(
                f"Client {client_id}: "
                f"Gain={gain}, Average risk={risk}, "
                f"Risk variance={variance:.2f}, "
                f"Average margin per hour={data['avg_margin_per_hour']:.2f}"
            )

            if gain >= 6 and (risk >= 6 or variance >= 60):
                print(" → Profitable but risky")
            elif gain <= 4 and risk <= 4 and variance <= 40:
                print(" → Unprofitable but stable")
            elif gain >= 6:
                print(" → Strong client")
            elif risk >= 6 or variance >= 60:
                print(" → Risk exposure")
            else:
                print(" → Neutral")

            print("-" * 50)

    # -----------------------
    # Order Analysis
    # -----------------------

    def analyze_orders(self):
        """
        Identify bad candidates for a bottleneck machine.
        Heuristic:
        - Long processing time
        - Low margin per hour
        - High risk
        """
        df = self.order_df

        self.bad_orders = df[
            (df["processing_time_hr"] > df["processing_time_hr"].quantile(0.75))
            & (df["margin_per_hour"] < df["margin_per_hour"].quantile(0.25))
            & (df["risk (in percent)"] > 15)
        ]

        self.bad_orders = self.bad_orders.sort_values("margin_per_hour")

    def print_bad_orders(self):
        """
        Print orders that are bad candidates for a bottleneck machine,
        with concise explanations.
        """
        if not hasattr(self, "bad_orders") or self.bad_orders.empty:
            print("No bad bottleneck candidates identified.")
            return

        print("\n=== Orders unsuited for bottleneck machines ===\n")

        print(
            "Selection heuristic:\n"
            "- Processing time in the top 25%\n"
            "- Margin per hour in the bottom 25%\n"
            "- Risk above 50%\n"
        )

        print(
            "Interpretation:\n"
            "- These orders block scarce capacity for a long time\n"
            "- They generate little value per hour\n"
            "- They carry elevated execution or financial risk\n"
            "→ They should be deprioritized, rerouted, or renegotiated\n"
        )

        print(f"Number of problematic orders: {len(self.bad_orders)}\n")

        cols = [
            "customer_id",
            "order_id",
            "processing_time_hr",
            "margin_per_hour",
            "risk (in percent)",
        ]

        print(self.bad_orders[cols].to_string(index=False))

        print(
            "\nNotes:\n"
            "- This is a heuristic, not an optimizer.\n"
            "- Thresholds (25%, 50%) are policy choices.\n"
            "- Some orders may still be strategic or contractual.\n"
        )

