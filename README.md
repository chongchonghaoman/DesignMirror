# DesignMirror

> AI-Powered Design System Analyzer

Paste any URL, get instant design token extraction with copy-ready CSS. Understand why something looks good and replicate it.

![DesignMirror Logo](logo.png)

## Demo Video

Watch the demo to see DesignMirror in action:

[![DesignMirror Demo](https://img.shields.io/badge/Download%20Demo-MOV-blue)](https://github.com/chongchonghaoman/DesignMirror/releases/download/v1.0.0/DesignMirror-demo.mov)

Or download directly: [DesignMirror-demo.mov](https://github.com/chongchonghaoman/DesignMirror/releases/download/v1.0.0/DesignMirror-demo.mov)

## Features

- **Design Token Extraction** - Colors, fonts, spacing, border radius
- **AI-Powered Analysis** - Deep analysis of design patterns and techniques
- **Copy-Ready CSS** - Generate CSS variables for your own projects
- **Analysis History** - View and revisit previous analyses
- **Design Insights** - Learn what techniques to adopt and avoid

## Quick Start

### 1. Install Dependencies

```bash
pip install flask requests anthropic
```

### 2. Configure API Key

```bash
cp config.json.example config.json
```

Edit `config.json` and add your API key:

```json
{
  "minimax_api_key": "your-api-key-here",
  "minimax_base_url": "https://api.minimaxi.com/anthropic",
  "minimax_model": "MiniMax-M2.7"
}
```

### 3. Run

```bash
python app.py
```

Open [http://localhost:5002](http://localhost:5002) in your browser.

## Usage

1. Enter a URL (e.g., `apple.com`, `stripe.com`, `linear.app`)
2. Click "Analyze"
3. View extracted design tokens (Colors, Typography, Spacing, Border Radius)
4. Copy CSS variables to your project

## Showcase

Example projects built with DesignMirror design tokens:

### [TikTok Brand Hub](./showcase/tiktok-brand.html)

A TikTok-inspired brand landing page demonstrating:

- Dark theme with warm golden accents (`#7AD1DD`, `#FF00A1`, `#FFC65D`)
- Poppins/Barlow Condensed/Inter typography
- Coverflow carousel showcase
- Glass morphism navigation
- Floating animations and micro-interactions
- Dark/Light mode toggle

Open `showcase/tiktok-brand.html` directly in a browser to preview.

## Tech Stack

- **Frontend**: Tailwind CSS + Vanilla JS
- **Backend**: Python Flask
- **AI**: MiniMax API (Anthropic-compatible)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/api/analyze` | POST | Analyze a URL |
| `/api/history` | GET | Get analysis history |
| `/api/history/<id>` | GET | Get specific history entry |
| `/api/config` | GET/POST | Get/save configuration |

## Design Language

Based on [Geist](https://vercel.com/geist) design system principles.

| Token | Value |
|-------|-------|
| Primary | `#171717` |
| Link | `#0070f3` |
| Cyan | `#50e3c2` |
| Violet | `#7928ca` |

## License

MIT