# VIDEO PUBLISHER MASTER PLAN

## PROJECT VISION
Sistema 100% gratuito que:
1. Detecta formato video (16:9 vs 9:16)
2. Enruta videos a plataformas apropiadas
3. Usa API oficial para YouTube
4. Usa automatización stealth para TikTok/Instagram
5. Ofrece 3 interfaces: CLI, Web API, Python library

## ARCHITECTURE PRINCIPLES
- Modular Design
- Dual Interface: Python lib + Web API + CLI
- Safety First: Anti-ban measures
- 100% Free

## TECH STACK
- Python 3.10+
- moviepy/opencv-python
- undetected-chromedriver (stealth)
- google-api-python-client (YouTube)
- Flask (Web API)
- click/typer (CLI)
- Docker

## PHASED IMPLEMENTATION
Phase 1: Core Engine + YouTube
Phase 2: Web Automation (TikTok, Instagram)
Phase 3: Multi-Interface (CLI, Web, Library)
Phase 4: Safety & Monitoring

## SAFETY CONSTRAINTS
- TikTok: 3 videos/hour
- Instagram: 5 videos/hour
- YouTube: 10 videos/hour
- Emergency stop on CAPTCHA