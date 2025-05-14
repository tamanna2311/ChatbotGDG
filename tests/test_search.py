"""
File Name: test_search.py
Purpose: Contains basic unit tests to ensure our recommendation engine works.
Why it exists: In professional environments, code isn't deployed until we prove it works automatically.
This script provides simple validation that given a query, we actually get results.
What it imports: unittest (built-in testing framework), src.recommender.Recommender
Role in pipeline: Validation layer.
"""

import unittest
import os
from src.recommender import Recommender
from src.config import PROCESSED_DATA_DIR

class TestSearchFeature(unittest.TestCase):
    """
    Test suite for the Recommender class.
    Run via: python -m unittest tests/test_search.py
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Runs once before any tests start.
        We instantiate down here so if the models aren't built, the tests just skip/fail gracefully.
        """
        # Skip tests if data hasn't been generated
        if not os.path.exists(os.path.join(PROCESSED_DATA_DIR, "tfidf_matrix.pkl")):
             raise unittest.SkipTest("Models not built. Run indexer first.")
             
        cls.recommender = Recommender()

    def test_basic_search_returns_results(self):
        """
        Validates that querying for something standard returns at least one result.
        What it does: Calls the recommender and checks the array length.
        """
        results = self.recommender.recommend_by_similarity("math", top_k=2)
        
        # Assertions are the core of testing. If this is False, the test fails.
        self.assertTrue(len(results) > 0, "No results returned for 'math'")
        self.assertEqual(len(results), 2, "Did not return exactly 2 results")
        
        # Check dictionary structure
        first_result = results[0]
        self.assertIn('name', first_result)
        self.assertIn('similarity_score', first_result)

if __name__ == '__main__':
    unittest.main()
