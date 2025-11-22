import requests
import networkx as nx
import time
import json
from tqdm import tqdm
from datetime import datetime, timedelta

class BitcoinAnalyzer:
    def __init__(self, initial_addresses, max_level=1, start_date=None, end_date=None):
        self.initial_addresses = set(initial_addresses)
        self.max_level = max_level
        self.graph = nx.DiGraph()
        self.visited_addresses = set()
        self.all_transactions = []
        
        # Time constraints: addr -> list of (min_ts, max_ts)
        self.address_constraints = {}
        
        # Convert dates to timestamps
        # Default to full history if not specified
        start_ts = int(start_date.timestamp()) if start_date else 0
        end_ts = int(end_date.timestamp()) if end_date else 99999999999
        
        # Initialize constraints for Level 0
        for addr in self.initial_addresses:
            self.add_constraint(addr, start_ts, end_ts)

    def add_constraint(self, addr, min_ts, max_ts):
        if addr not in self.address_constraints:
            self.address_constraints[addr] = []
        self.address_constraints[addr].append((min_ts, max_ts))

    def is_tx_relevant(self, addr, tx_time):
        # If no constraints recorded for this address, it shouldn't be processed ideally,
        # but if it is, maybe default to False to be safe?
        # Actually, for Level 0, we initialized constraints.
        # For deeper levels, we only add to queue if we added constraints.
        if addr not in self.address_constraints:
            return False
        
        for (min_ts, max_ts) in self.address_constraints[addr]:
            if min_ts <= tx_time <= max_ts:
                return True
        return False

    def fetch_batch_transactions(self, addresses):
        if not addresses:
            return []
        
        # Join addresses with '|'
        addr_str = '|'.join(addresses)
        # Limit to 50 txs per batch to avoid huge payloads, 
        # since we might be fetching for many addresses.
        # If we need more history, we would need pagination, but for this tool's scope
        # and the "efficiency" requirement, let's stick to latest 50.
        # If the user provides a time range that is very old, this might miss data.
        # Ideally we would check the time of the last tx and paginate if needed.
        # But multiaddr doesn't support offset easily for mixed addresses.
        # Let's use n=100.
        url = f"https://blockchain.info/multiaddr?active={addr_str}&n=100" 
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get('txs', [])
            else:
                print(f"Error fetching batch data: {response.status_code}")
                return []
        except Exception as e:
            print(f"Exception fetching batch data: {e}")
            return []

    def analyze(self):
        # Ensure all initial addresses are in the graph, even if they have no transactions
        self.graph.add_nodes_from(self.initial_addresses)

        current_level_addresses = list(self.initial_addresses)
        self.visited_addresses.update(self.initial_addresses)

        for level in range(self.max_level + 1):
            print(f"Analyzing Level {level} ({len(current_level_addresses)} addresses)...")
            
            if not current_level_addresses:
                break

            next_level_addresses = set()
            
            # Batch processing
            batch_size = 20 
            batches = [current_level_addresses[i:i + batch_size] for i in range(0, len(current_level_addresses), batch_size)]
            
            for batch in tqdm(batches, desc=f"Fetching Level {level}"):
                txs = self.fetch_batch_transactions(batch)
                
                for tx in txs:
                    tx_time = tx.get('time', 0)
                    tx_hash = tx.get('hash')
                    
                    # Check if this transaction is relevant for ANY of the addresses in the batch
                    # that are involved in this transaction.
                    # A tx might involve multiple addresses from our batch.
                    
                    inputs = tx.get('inputs', [])
                    out = tx.get('out', [])
                    
                    # Identify participants
                    senders = set()
                    for inp in inputs:
                        prev_out = inp.get('prev_out')
                        if prev_out:
                            addr = prev_out.get('addr')
                            if addr:
                                senders.add(addr)
                    
                    receivers = set()
                    for o in out:
                        addr = o.get('addr')
                        if addr:
                            receivers.add(addr)
                    
                    # Check relevance
                    # A tx is relevant if it is within the time window of at least one 
                    # of the currently analyzed addresses involved in it.
                    is_relevant = False
                    involved_current_level = set()
                    
                    all_participants = senders.union(receivers)
                    
                    for addr in all_participants:
                        if addr in batch: # Only check constraints for addresses we are currently analyzing
                            if self.is_tx_relevant(addr, tx_time):
                                is_relevant = True
                                involved_current_level.add(addr)
                    
                    if not is_relevant:
                        continue

                    self.all_transactions.append(tx)

                    # Add edges and propagate constraints
                    # Logic:
                    # If we are at Level L, we found a relevant tx.
                    # We add edges between senders and receivers.
                    # For any NEW address (not visited), we add it to next level.
                    # AND we set its time constraint to [tx_time - 1 week, tx_time + 1 week].
                    
                    one_week = 7 * 24 * 3600
                    new_min_ts = tx_time - one_week
                    new_max_ts = tx_time + one_week
                    
                    for s in senders:
                        for r in receivers:
                            if s != r:
                                self.graph.add_edge(s, r, tx_hash=tx_hash, time=tx_time)
                                
                                if level < self.max_level:
                                    # Propagate to S if S is new
                                    if s not in self.visited_addresses and s not in current_level_addresses:
                                        next_level_addresses.add(s)
                                        self.add_constraint(s, new_min_ts, new_max_ts)
                                    
                                    # Propagate to R if R is new
                                    if r not in self.visited_addresses and r not in current_level_addresses:
                                        next_level_addresses.add(r)
                                        self.add_constraint(r, new_min_ts, new_max_ts)

                # Be nice to the API
                time.sleep(0.5)
            
            # Update visited and current level
            self.visited_addresses.update(next_level_addresses)
            current_level_addresses = list(next_level_addresses)

        return self.graph

    def filter_relevant_graph(self):
        """
        Filters the graph to keep only nodes that are part of a path between
        any two initial addresses.
        """
        print("Filtering graph for relevant connections...")
        relevant_nodes = set()
        relevant_nodes.update(self.initial_addresses)
        
        # Find all paths between pairs of initial addresses
        # This can be expensive for large graphs, so we might need to limit path length
        # or use a different approach.
        # Since we built the graph up to max_level, the paths shouldn't be longer than 2 * max_level roughly.
        
        initial_list = list(self.initial_addresses)
        
        # We only care about nodes in the graph
        initial_list = [addr for addr in initial_list if addr in self.graph]
        
        if len(initial_list) < 2:
            return self.graph.subgraph(initial_list).copy()

        # Check connectivity between all pairs
        # Using all_simple_paths is too slow for dense graphs.
        # Better:
        # For each initial address, do a BFS/DFS to find reachable other initial addresses.
        # Or, just keep the induced subgraph of all nodes that lie on ANY path between two initial nodes.
        
        # Optimization:
        # 1. Calculate all-pairs shortest paths (or reachability) between initial nodes?
        # 2. Or simply:
        #    For each pair (A, B) in initial_addresses:
        #       if has_path(A, B):
        #           add all nodes in shortest_path(A, B) to relevant?
        #           (User might want ALL paths, not just shortest)
        
        # Let's try a "bidirectional" reachability approach or just simple path finding with cutoff.
        # Given the graph size might be thousands, all_simple_paths is risky.
        # Let's stick to: Keep nodes that are in the Weakly Connected Component containing the initial addresses?
        # No, that includes dead ends.
        
        # Let's try:
        # Keep a node X if:
        # X is reachable from some Initial_A AND X can reach some Initial_B
        # (Where A could be same as B? No, distinct pairs usually, but A->...->A loops exist)
        
        # Actually, the user wants "relationships between them".
        # So: A -> ... -> B.
        # Node X is relevant if A -> ... -> X -> ... -> B.
        # i.e. X is a descendant of some Start and ancestor of some End.
        # Here Start and End are both from 'initial_addresses'.
        
        # So:
        # 1. Find all descendants of {initial_addresses} (set D)
        # 2. Find all ancestors of {initial_addresses} (set A)
        # 3. Intersection D & A?
        #    If X is in D, it comes from some Initial.
        #    If X is in A, it goes to some Initial.
        #    So X is on a path Initial -> X -> Initial.
        #    This seems correct and efficient!
        
        descendants = set()
        ancestors = set()
        
        # NetworkX has efficient algorithms for this
        # descendants = union of descendants of each initial node
        # ancestors = union of ancestors of each initial node
        
        for node in initial_list:
            try:
                d = nx.descendants(self.graph, node)
                descendants.update(d)
                descendants.add(node)
            except:
                pass
                
            try:
                a = nx.ancestors(self.graph, node)
                ancestors.update(a)
                ancestors.add(node)
            except:
                pass
        
        # Intersection
        keep_nodes = descendants.intersection(ancestors)
        
        # Also ensure all initial addresses are kept (they should be in the intersection if they are part of any cycle or path, but isolated ones might be lost?
        # Wait, if A is isolated, it has no descendants other than itself (if we consider reflexive).
        # nx.descendants does NOT include the node itself.
        # So we added `node` manually.
        # If A is isolated: descendants={A}, ancestors={A}. Intersection={A}. Correct.
        # If A -> B (B is not initial):
        # A: desc={A, B}, anc={A}
        # B: desc={B}, anc={A, B} (if we calculate for B? No, we only calculate for initial)
        
        # Wait.
        # We want paths between ANY pair of initial addresses.
        # Let S be the set of initial addresses.
        # We want nodes X such that there exists s1 in S, s2 in S, and path s1 -> ... -> X -> ... -> s2.
        # This is exactly: X is in descendants(S) AND X is in ancestors(S).
        # Proof:
        # If X in desc(S), exists s1 such that s1 -> ... -> X.
        # If X in anc(S), exists s2 such that X -> ... -> s2.
        # So s1 -> ... -> X -> ... -> s2.
        # This covers s1=s2 (cycles) and s1!=s2 (paths).
        
        return self.graph.subgraph(list(keep_nodes)).copy()

    def save_data(self, filename_prefix="data"):
        # Save graph
        data = nx.node_link_data(self.graph)
        with open(f"{filename_prefix}_full_graph.json", 'w') as f:
            json.dump(data, f)
            
        # Save raw transactions (optional, but requested)
        with open(f"{filename_prefix}_transactions.json", 'w') as f:
            json.dump(self.all_transactions, f)

