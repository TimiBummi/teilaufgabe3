from analyzer.analyzer import Analyzer
from file_reader import FileReader


def main():
    # Read 'dataset' and store in a DataFrame
    order_df = FileReader.read_ods("C:/Users/Tim/Desktop/orders.ods")

    # Initialize the analyzer
    analyzer = Analyzer(order_df)

    # Welche Merkmale treiben den Deckungsbeitrag pro Stunde am stärksten?
    analyzer.analyze_margin()
    analyzer.print_characteristics()

    # Welche Kunden sind:
    #   profitabel, aber riskant?
    #   stabil, aber wenig profitabel?
    analyzer.analyze_client()
    analyzer.print_client_risk_and_gain()

    # Welche Aufträge sind systematisch schlechte Kandidaten für einen Engpass?
    analyzer.analyze_orders()
    analyzer.print_bad_orders()

if __name__ == "__main__":
    main()