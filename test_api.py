#!/usr/bin/env python3
"""
Simple test script for the EUREKA GPT Assistant Suite API
"""

import requests
import json

# Base URL - change this to your Hugging Face Space URL
BASE_URL = "https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_gpt_selection():
    """Test GPT selection"""
    try:
        data = {"gpt_type": "offer_clarifier"}
        response = requests.post(f"{BASE_URL}/api/select-gpt", json=data)
        print(f"✅ GPT selection: {response.status_code}")
        result = response.json()
        print(f"Session ID: {result.get('session_id')}")
        print(f"GPT Type: {result.get('gpt_type')}")
        return result.get('session_id')
    except Exception as e:
        print(f"❌ GPT selection failed: {e}")
        return None

def test_chat(session_id):
    """Test chat functionality"""
    if not session_id:
        print("❌ No session ID available")
        return False
    
    try:
        data = {
            "session_id": session_id,
            "message": "My product is a coaching program for freelancers",
            "gpt_type": "offer_clarifier"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=data)
        print(f"✅ Chat test: {response.status_code}")
        result = response.json()
        print(f"Reply: {result.get('reply', '')[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing EUREKA GPT Assistant Suite API")
    print("=" * 50)
    
    # Test health
    if not test_health():
        return
    
    print()
    
    # Test GPT selection
    session_id = test_gpt_selection()
    
    print()
    
    # Test chat
    if session_id:
        test_chat(session_id)
    
    print()
    print("🎉 Testing complete!")

if __name__ == "__main__":
    main()
