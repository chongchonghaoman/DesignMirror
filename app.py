#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DesignMirror - AI Design System Analyzer"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import os
import time
from pathlib import Path
from flask import Flask, send_from_directory, request, jsonify
import requests

app = Flask(__name__, static_folder='.')
CONFIG_PATH = Path(__file__).parent / "config.json"
HISTORY_PATH = Path(__file__).parent / "history.json"
MAX_HISTORY = 50

def load_config():
    """Load API key from config"""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    return {}

def load_history():
    """Load analysis history"""
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding='utf-8'))
        except:
            return []
    return []

def save_history(history):
    """Save analysis history"""
    HISTORY_PATH.write_text(json.dumps(history[-MAX_HISTORY:], indent=2, ensure_ascii=False), encoding='utf-8')

def add_to_history(url, analysis, success=True):
    """Add entry to history"""
    history = load_history()
    entry = {
        "id": int(time.time() * 1000),
        "url": url,
        "analysis": analysis,
        "success": success,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    history.append(entry)
    save_history(history)
    return entry

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get analysis history"""
    history = load_history()
    # Return without full analysis text for list view
    return jsonify({
        'history': [
            {k: v for k, v in item.items() if k != 'analysis'}
            for item in reversed(history)
        ]
    })

@app.route('/api/history/<int:entry_id>', methods=['GET'])
def get_history_entry(entry_id):
    """Get a specific history entry with full analysis"""
    history = load_history()
    for item in history:
        if item['id'] == entry_id:
            return jsonify({'status': 'success', 'entry': item})
    return jsonify({'status': 'error', 'message': 'Entry not found'}), 404

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze a website's design system"""
    data = request.json
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'status': 'error', 'message': 'URL is required'}), 400

    # Fetch the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        html_content = resp.text[:50000]
    except requests.RequestException as e:
        return jsonify({'status': 'error', 'message': f'Failed to fetch URL: {str(e)}'}), 500

    # Get API key and call AI
    config = load_config()
    api_key = config.get('minimax_api_key', '')
    base_url = config.get('minimax_base_url', 'https://api.minimaxi.com/anthropic')
    model = config.get('minimax_model', 'MiniMax-M2.7')

    if not api_key:
        return jsonify({'status': 'error', 'message': 'API key not configured. Please add your API key to config.json'}), 500

    # Build prompt
    prompt = f"""Role: You are a senior UI design expert specializing in design system analysis.

Task:
1. Analyze the provided HTML from a website
2. Extract design tokens: colors, fonts, spacing, radius, shadows
3. Identify design patterns and techniques
4. Generate copy-ready CSS code

Output your analysis in this exact Markdown format:

## Design Tokens

### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Primary | #XXX | Main brand color |
| Secondary | #XXX | Supporting color |
| Accent | #XXX | Call-to-action, highlights |
| Background | #XXX | Page background |
| Surface | #XXX | Cards, elevated surfaces |
| Text Primary | #XXX | Main text color |
| Text Secondary | #XXX | Muted, secondary text |
| Border | #XXX | Dividers, outlines |

### Typography
| Element | Font | Size/Weight |
|---------|------|-------------|
| Display | Family Name | XXpx / bold |
| Heading | Family Name | XXpx / semibold |
| Body | Family Name | XXpx / normal |
| Caption | Family Name | XXpx / normal |

### Spacing
| Name | Value | Usage |
|------|-------|-------|
| xs | Xpx | Tight spacing |
| sm | Xpx | Small gaps |
| md | Xpx | Default spacing |
| lg | Xpx | Section gaps |
| xl | Xpx | Large sections |

### Border Radius
| Name | Value | Usage |
|------|-------|-------|
| sm | Xpx | Buttons, inputs |
| md | Xpx | Cards |
| lg | Xpx | Modals, large containers |

---

## Design Insights

### Design Language
(Describe the overall style: minimalist, modern, playful, etc.)

### Key Techniques
1. (Technique 1)
2. (Technique 2)
3. (Technique 3)

### Worth Adopting
- (What you should use in your own projects)

### Avoid
- (Anti-patterns or overused elements)

---

## CSS Variables (Copy-Ready)

```css
:root {{
  /* Colors */
  --color-primary: #XXX;
  --color-secondary: #XXX;
  --color-accent: #XXX;
  --color-background: #XXX;
  --color-surface: #XXX;
  --color-text-primary: #XXX;
  --color-text-secondary: #XXX;
  --color-border: #XXX;

  /* Typography */
  --font-family: 'Font Name', system-ui, sans-serif;
  --font-size-base: XXpx;
  --font-weight-normal: 400;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Spacing */
  --space-xs: Xpx;
  --space-sm: Xpx;
  --space-md: Xpx;
  --space-lg: Xpx;
  --space-xl: Xpx;

  /* Border Radius */
  --radius-sm: Xpx;
  --radius-md: Xpx;
  --radius-lg: Xpx;
}}
```

---
*Analysis complete*"""

    os.environ["ANTHROPIC_BASE_URL"] = base_url
    os.environ["ANTHROPIC_API_KEY"] = api_key

    # Retry logic for timeouts
    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key, base_url=base_url, timeout=120)

            response = client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": f"Website URL: {url}\n\nHTML Content:\n{html_content}\n\n{prompt}"}
                ]
            )

            text = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, 'text'):
                        text += block.text

            if not text:
                return jsonify({'status': 'error', 'message': 'Empty response from AI'}), 500

            # Save to history
            entry = add_to_history(url, text.strip(), success=True)

            return jsonify({
                'status': 'success',
                'analysis': text.strip(),
                'url': url,
                'id': entry['id'],
                'timestamp': entry['timestamp']
            })

        except ImportError:
            return jsonify({'status': 'error', 'message': 'anthropic package not installed. Run: pip install anthropic'}), 500
        except Exception as e:
            last_error = str(e)
            error_str = str(e).lower()
            is_timeout = 'timeout' in error_str or 'timed out' in error_str or 'interrupted' in error_str

            if is_timeout and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                time.sleep(wait_time)
                continue

            # Save failed attempt to history
            add_to_history(url, f"Analysis failed: {last_error}", success=False)

            return jsonify({
                'status': 'error',
                'message': f'AI analysis failed: {last_error}',
                'retryable': is_timeout
            }), 500

    return jsonify({'status': 'error', 'message': f'AI analysis failed after {max_retries} attempts: {last_error}'}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current config (without exposing API key)"""
    config = load_config()
    return jsonify({
        'has_api_key': bool(config.get('minimax_api_key')),
        'model': config.get('minimax_model', 'MiniMax-M2.7')
    })

@app.route('/api/config', methods=['POST'])
def save_config():
    """Save API key to config"""
    try:
        data = request.json
        api_key = data.get('minimax_api_key', '').strip()

        if not api_key:
            return jsonify({'status': 'error', 'message': 'API key is required'}), 400

        config = {
            'minimax_api_key': api_key,
            'minimax_base_url': data.get('minimax_base_url', 'https://api.minimaxi.com/anthropic'),
            'minimax_model': data.get('minimax_model', 'MiniMax-M2.7')
        }

        CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   DesignMirror - AI Design System Analyzer                 ║
    ║                                                           ║
    ║   Running on: http://localhost:5002                       ║
    ║                                                           ║
    ║   Before using, add your API key to config.json:          ║
    ║   {{"minimax_api_key": "your-key-here"}}                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=False, port=5002)