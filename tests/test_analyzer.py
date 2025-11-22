import unittest
from unittest.mock import patch, MagicMock
from src.analyzer import BitcoinAnalyzer

class TestBitcoinAnalyzer(unittest.TestCase):
    @patch('src.analyzer.requests.get')
    def test_analyze_simple(self, mock_get):
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'txs': [
                {
                    'hash': 'tx1',
                    'inputs': [{'prev_out': {'addr': 'addr1'}}],
                    'out': [{'addr': 'addr2'}]
                }
            ]
        }
        mock_get.return_value = mock_response

        analyzer = BitcoinAnalyzer(['addr1'], max_level=1)
        graph = analyzer.analyze()

        self.assertTrue(graph.has_edge('addr1', 'addr2'))
        self.assertEqual(len(graph.nodes), 2)

if __name__ == '__main__':
    unittest.main()
