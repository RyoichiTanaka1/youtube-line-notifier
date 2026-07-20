You are working on a Python FastAPI project.

Requirements

- Never expose .env
- Never modify .env
- Never modify Docker ports
- Existing API behaviour must not change
- Refactor only
- Use small commits
- Build after each major change
- Run docker compose up -d --build
- Verify /health
- Verify WebSub GET
- Verify WebSub POST
- Existing containers must remain running

Goal

Split responsibilities into

app/
    main.py
    config.py
    database.py
    youtube.py
    line.py
    video_repository.py
    notification_service.py