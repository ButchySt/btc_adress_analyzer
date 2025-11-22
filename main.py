import argparse
import networkx as nx
from datetime import datetime
from src.analyzer import BitcoinAnalyzer
from src.visualizer import visualize_graph

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")

def main():
    parser = argparse.ArgumentParser(description="Analyze Bitcoin address transactions.")
    parser.add_argument('addresses', metavar='ADDR', type=str, nargs='+',
                        help='Bitcoin addresses to analyze')
    parser.add_argument('--level', type=int, default=1,
                        help='Depth of analysis (default: 1)')
    parser.add_argument('--output', type=str, default='graph.png',
                        help='Output image file (default: graph.png)')
    parser.add_argument('--save-data', action='store_true',
                        help='Save full and filtered graph data to JSON')
    parser.add_argument('--start-date', type=parse_date, default=None,
                        help='Start date for Level 0 addresses (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=parse_date, default=None,
                        help='End date for Level 0 addresses (YYYY-MM-DD)')

    args = parser.parse_args()

    print(f"Analyzing addresses: {args.addresses}")
    print(f"Level: {args.level}")
    if args.start_date:
        print(f"Start Date: {args.start_date.strftime('%Y-%m-%d')}")
    if args.end_date:
        print(f"End Date: {args.end_date.strftime('%Y-%m-%d')}")

    analyzer = BitcoinAnalyzer(
        args.addresses, 
        max_level=args.level,
        start_date=args.start_date,
        end_date=args.end_date
    )
    
    # 1. Analyze (Fetch Data)
    full_graph = analyzer.analyze()
    print(f"Full graph: {len(full_graph.nodes)} nodes, {len(full_graph.edges)} edges.")

    # 2. Save Full Data
    if args.save_data:
        analyzer.save_data("analysis_result")
        print("Full data saved to analysis_result_*.json")

    # 3. Filter Relevant Data
    filtered_graph = analyzer.filter_relevant_graph()
    print(f"Filtered graph: {len(filtered_graph.nodes)} nodes, {len(filtered_graph.edges)} edges.")
    
    # 4. Visualize Filtered Data
    if len(filtered_graph.nodes) > 0:
        visualize_graph(filtered_graph, args.addresses, output_file=args.output)
    else:
        print("No relevant transactions found between the provided addresses.")

if __name__ == "__main__":
    main()
