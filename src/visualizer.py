import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph(graph, initial_addresses, output_file="transaction_graph.png"):
    if not graph.nodes:
        print("Graph is empty. Nothing to visualize.")
        return

    plt.figure(figsize=(12, 8))
    
    # Use a layout that handles disconnected components better if needed
    # spring_layout is generally good
    pos = nx.spring_layout(graph, k=0.5, iterations=50)
    
    # Identify initial addresses in the graph
    initial_in_graph = [node for node in initial_addresses if node in graph]
    other_nodes = [node for node in graph.nodes if node not in initial_addresses]
    
    # Draw other nodes
    nx.draw_networkx_nodes(graph, pos, nodelist=other_nodes, node_size=300, node_color='lightblue', alpha=0.6)
    
    # Highlight initial addresses
    nx.draw_networkx_nodes(graph, pos, nodelist=initial_in_graph, node_size=500, node_color='red', alpha=0.9)
    
    # Draw edges
    nx.draw_networkx_edges(graph, pos, width=1.0, alpha=0.5, arrowstyle='->', arrowsize=10)
    
    # Draw labels
    # If graph is small, label everything
    if len(graph.nodes) < 50:
        nx.draw_networkx_labels(graph, pos, font_size=8)
    else:
        # Only label initial addresses if graph is large
        labels = {node: node for node in initial_in_graph}
        nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, font_color='black')

    plt.title(f"Bitcoin Transaction Analysis ({len(graph.nodes)} nodes)")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Graph saved to {output_file}")
    # plt.show() # Commented out to avoid blocking execution in some environments
