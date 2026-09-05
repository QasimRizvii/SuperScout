# SuperScout REST API v1 Reference

All endpoints return standard JSON responses. Paginated endpoints use `PaginatedResponse[T]` format:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

---

## Endpoints Summary

| Method | Path | Description | Query Parameters |
|---|---|---|---|
| `GET` | `/api/v1/health` | Backend and Database Health | None |
| `GET` | `/api/v1/players` | List Players | `page`, `page_size`, `name`, `role`, `nationality`, `is_active` |
| `GET` | `/api/v1/players/{id}` | Get Player by ID | None |
| `GET` | `/api/v1/teams` | List Teams | `page`, `page_size`, `name`, `is_active` |
| `GET` | `/api/v1/teams/{id}` | Get Team by ID | None |
| `GET` | `/api/v1/venues` | List Venues | `page`, `page_size`, `city`, `country` |
| `GET` | `/api/v1/venues/{id}` | Get Venue by ID | None |
| `GET` | `/api/v1/matches` | List Matches | `page`, `page_size`, `season`, `team_id`, `venue_id`, `match_date` |
| `GET` | `/api/v1/matches/{id}` | Get Match by ID | None |
| `GET` | `/api/v1/auctions` | List Auctions | `page`, `page_size`, `season`, `auction_type` |
| `GET` | `/api/v1/auctions/{id}` | Get Auction by ID | None |
