"""
Unit tests for QueryClassifier

Tests classification with mocked OpenAI responses and keyword fallback.
"""

import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.classifier import QueryClassifier


def test_keyword_classification_incentive():
    """Test keyword-based classification for incentive queries"""
    print("\n[TEST 1] Testing keyword classification for INCENTIVE...")
    
    classifier = QueryClassifier()
    
    test_queries = [
        "Quais são os incentivos disponíveis para inovação?",
        "Procuro apoios financeiros para a minha empresa",
        "Que fundos existem para digitalização?",
        "Candidatura a subsídios para exportação"
    ]
    
    for query in test_queries:
        result = classifier._classify_with_keywords(query)
        assert result == "INCENTIVE", f"Expected INCENTIVE for: {query}"
        print(f"  ✓ '{query[:50]}...' → {result}")
    
    print("✓ Keyword classification for INCENTIVE passed")


def test_keyword_classification_company():
    """Test keyword-based classification for company queries"""
    print("\n[TEST 2] Testing keyword classification for COMPANY...")
    
    classifier = QueryClassifier()
    
    test_queries = [
        "Informação sobre a empresa XYZ, Lda",
        "Quais empresas são elegíveis?",
        "Procuro dados sobre sociedades de construção",
        "Lista de companhias no setor tecnológico"
    ]
    
    for query in test_queries:
        result = classifier._classify_with_keywords(query)
        assert result == "COMPANY", f"Expected COMPANY for: {query}"
        print(f"  ✓ '{query[:50]}...' → {result}")
    
    print("✓ Keyword classification for COMPANY passed")


def test_gpt_classification_with_mock():
    """Test GPT classification with mocked OpenAI response"""
    print("\n[TEST 3] Testing GPT classification with mock...")
    
    classifier = QueryClassifier()
    
    # Mock OpenAI response for INCENTIVE
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"type": "INCENTIVE"}'
    
    with patch.object(classifier.client.chat.completions, 'create', return_value=mock_response):
        result = classifier._classify_with_gpt("Quais são os incentivos?")
        assert result == "INCENTIVE"
        print("  ✓ Mocked GPT response for INCENTIVE")
    
    # Mock OpenAI response for COMPANY
    mock_response.choices[0].message.content = '{"type": "COMPANY"}'
    
    with patch.object(classifier.client.chat.completions, 'create', return_value=mock_response):
        result = classifier._classify_with_gpt("Informação sobre empresas")
        assert result == "COMPANY"
        print("  ✓ Mocked GPT response for COMPANY")
    
    print("✓ GPT classification with mock passed")


def test_gpt_classification_with_explanation():
    """Test GPT classification when response includes explanation"""
    print("\n[TEST 4] Testing GPT classification with explanation text...")
    
    classifier = QueryClassifier()
    
    # Mock response with explanation before JSON
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = 'This is an incentive query. {"type": "INCENTIVE"}'
    
    with patch.object(classifier.client.chat.completions, 'create', return_value=mock_response):
        result = classifier._classify_with_gpt("Test query")
        assert result == "INCENTIVE"
        print("  ✓ Extracted JSON from response with explanation")
    
    print("✓ GPT classification with explanation passed")


def test_fallback_on_gpt_failure():
    """Test that classifier falls back to keywords when GPT fails"""
    print("\n[TEST 5] Testing fallback to keywords on GPT failure...")
    
    classifier = QueryClassifier()
    
    # Mock GPT to raise an exception
    with patch.object(classifier.client.chat.completions, 'create', side_effect=Exception("API Error")):
        result = classifier.classify("Quais são os incentivos disponíveis?")
        assert result == "INCENTIVE"
        print("  ✓ Fell back to keyword classification on GPT error")
    
    print("✓ Fallback mechanism passed")


def test_invalid_gpt_response():
    """Test handling of invalid GPT responses"""
    print("\n[TEST 6] Testing invalid GPT response handling...")
    
    classifier = QueryClassifier()
    
    # Mock invalid response (not JSON)
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = 'This is not JSON'
    
    with patch.object(classifier.client.chat.completions, 'create', return_value=mock_response):
        try:
            result = classifier._classify_with_gpt("Test query")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            print(f"  ✓ Raised ValueError for invalid response: {e}")
    
    print("✓ Invalid response handling passed")


def test_prompt_creation():
    """Test that prompt is created correctly"""
    print("\n[TEST 7] Testing prompt creation...")
    
    classifier = QueryClassifier()
    
    query = "Test query about incentivos"
    prompt = classifier._create_classification_prompt(query)
    
    assert "INCENTIVE" in prompt
    assert "COMPANY" in prompt
    assert query in prompt
    assert "JSON" in prompt
    
    print(f"  ✓ Prompt created with length: {len(prompt)} chars")
    print(f"  ✓ Prompt contains query and instructions")
    
    print("✓ Prompt creation passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("QUERY CLASSIFIER TESTS")
    print("=" * 70)
    
    try:
        test_keyword_classification_incentive()
        test_keyword_classification_company()
        test_gpt_classification_with_mock()
        test_gpt_classification_with_explanation()
        test_fallback_on_gpt_failure()
        test_invalid_gpt_response()
        test_prompt_creation()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
