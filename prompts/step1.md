As a Senior DevOps Engineer, create the foundation for a video publishing automation system.

## CONTEXT: Refer to Masterplan.md
Create the foundation for a multi-interface video publisher.

Generate ONLY infrastructure:
1. Project tree supporting three interfaces
2. pyproject.toml with:
   - Entry points for CLI
   - Package metadata for library
   - Flask as optional dependency
3. Docker setup (Dockerfile + docker-compose)
4. .env.example with all config variables
5. README.md explaining all usage methods

File structure must include:
- src/video_publisher/ (library core)
- cli/ (CLI interface)
- api/ (Flask web interface)
- tests/

Do NOT implement business logic yet.