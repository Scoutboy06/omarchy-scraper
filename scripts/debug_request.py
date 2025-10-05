#!/usr/bin/env python3
"""
Debug script to test different request methods and headers.
"""

import asyncio
import aiohttp
from config import BASE_URL, QUERY_PARAM, USER_AGENT


async def test_request_variants():
    """Test different request configurations to find what works."""
    url = f"{BASE_URL}{QUERY_PARAM}"
    
    print(f"🔍 Testing URL: {url}")
    print()
    
    # Test 1: Basic request
    print("1️⃣ Testing basic request...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"   Status: {response.status} {response.reason}")
                if response.status == 200:
                    content = await response.text()
                    print(f"   Content length: {len(content)}")
                else:
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 2: With basic headers
    print("2️⃣ Testing with browser-like headers...")
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                print(f"   Status: {response.status} {response.reason}")
                if response.status == 200:
                    content = await response.text()
                    print(f"   Content length: {len(content)}")
                else:
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 3: Simplified headers
    print("3️⃣ Testing with minimal headers...")
    headers = {
        'User-Agent': 'curl/7.68.0',
        'Accept': '*/*',
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                print(f"   Status: {response.status} {response.reason}")
                if response.status == 200:
                    content = await response.text()
                    print(f"   Content length: {len(content)}")
                else:
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 4: With referer
    print("4️⃣ Testing with referer...")
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://learn.omacom.io/',
        'Connection': 'keep-alive',
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                print(f"   Status: {response.status} {response.reason}")
                if response.status == 200:
                    content = await response.text()
                    print(f"   Content length: {len(content)}")
                    print("   ✅ Success! This configuration works.")
                else:
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test 5: Try different User-Agents
    user_agents = [
        'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    ]
    
    for i, ua in enumerate(user_agents, 5):
        print(f"{i}️⃣ Testing with different User-Agent ({ua[:50]}...)...")
        headers = {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    print(f"   Status: {response.status} {response.reason}")
                    if response.status == 200:
                        content = await response.text()
                        print(f"   Content length: {len(content)}")
                        print("   ✅ Success! This User-Agent works.")
                        break
                    else:
                        error_text = await response.text()
                        print(f"   Error: {error_text[:100]}...")
        except Exception as e:
            print(f"   Exception: {e}")
        
        print()


if __name__ == "__main__":
    asyncio.run(test_request_variants())