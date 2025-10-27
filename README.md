## Barber Service Crew (CrewAI + Azure OpenAI + Cal.com)

- Install dependencies:
  
  ```bash
  pip install -r requirements.txt
  ```

- Copy `.env.example` to `.env` and fill in:
  - `AZURE_API_BASE`, `AZURE_API_KEY`, `AZURE_API_VERSION`, `AZURE_DEPLOYMENT_NAME`
  - `CAL_API_BASE`, `CAL_API_KEY`, `CAL_EVENT_TYPE_ID`, `CAL_ORGANIZER_USERNAME`
  - `DEFAULT_TIMEZONE`

- Run:
  
  ```bash
  python main.py
  ```

### Notes
- Memory is persisted to `data/memory.json` and includes timestamped exchanges per `DEFAULT_TIMEZONE`.
- Cal.com API endpoints used: `GET /event-types/{id}/availability` and `POST /bookings`.
- If your Cal plan or version differs, adjust `tools/cal_api.py` accordingly.