# Table Scorecards Public API and Python SDK Documentation Handoff

This file is the public-docs and Python-SDK handoff for table scorecards. It has been validated against the current backend implementation in:

```txt
backend/app/api/routes/public_api/smart_tables/table_sheet_scorecard.py
backend/app/api/routes/public_api/smart_tables/table_sheet_score.py
backend/app/api/routes/dashboard_api/smart_tables/scorecard.py
backend/app/services/smart_tables/scorecard/
```

Use public wording in docs: **tables**, **sheets**, **table scorecards**, and **scorecards**. Avoid using **Smart Table** in public docs except if referencing an existing endpoint section title that has not yet been renamed.

---

## 1. Current backend source of truth

Base path:

```http
/api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard
```

Authentication is the same as other public table endpoints.


| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/scorecard` | Get the active scorecard and latest/display calculation |
| `PATCH` | `/scorecard` | Create or update the active scorecard |
| `DELETE` | `/scorecard` | Soft-delete the active scorecard |
| `POST` | `/scorecard/migrate-legacy-score` | Convert legacy sheet scoring into scorecard criteria |
| `POST` | `/scorecard/recalculate` | Queue scorecard recalculation |
| `POST` | `/scorecard/cancel` | Cancel active scorecard work |
| `GET` | `/scorecard/calculations/{calculation_id}` | Get calculation details |
| `GET` | `/scorecard/rows` | List row-level scorecard summaries |
| `GET` | `/scorecard/rows/{row_index}` | Get a row-level scorecard breakdown |

### Important SDK alignment note

The backend canonical configure endpoint is:

```http
PATCH /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard
```

If the Python SDK PR currently sends `PUT` from `configure_scorecard(...)`, update the SDK to send `PATCH`. Do **not** document `PUT` unless the backend is changed to accept `PUT`.

---

## 2. Public terminology updates

Use this wording in public docs and SDK docs:

| Avoid | Use instead |
|---|---|
| Smart Table | table |
| Smart Table sheet | sheet |
| Smart Table Scorecard | table scorecard / scorecard |
| Smart Table scoring | table scoring |

Release notes should say **table scorecard APIs**, not **Smart Table Scorecard APIs**.

Suggested release note:

```txt
Added first-class public table scorecard APIs under /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard.

Existing /score APIs remain supported. When no legacy score configuration exists, GET /score can return scorecard-compatible results and POST /score can queue scorecard recalculation.

Legacy score migration now preserves the old score configuration by default. Set delete_legacy_score: true only after all consumers have moved to scorecard APIs.
```

---

## 3. Concepts for public docs

### Scorecard

A scorecard is a structured evaluation configuration for a table sheet. It contains criteria and aggregation rules for producing row-level and sheet-level scores.


### Criterion / step

A criterion is one scorecard step. Criteria can compare columns, check text, run assertions, summarize columns, and contribute to the aggregate score.



### Calculation

A calculation is one scorecard run. It stores aggregate score, verdict, criterion summaries, row-level results, drift metadata, status, and errors.

### Row result

A row result contains the scorecard outcome for one row, including per-criterion `step_results`.




### Drift and stale state

Drift compares current results to a previous completed calculation when available. Stale state indicates results may need recalculation after inputs or scorecard configuration changed.


---

## 4. Backend enums and public values

These are the current backend values. The Python SDK should align to these values for table scorecards.


### Scorecard status

```txt
needs_setup
ready
queued
running
completed
stale
failed
```

If the SDK currently defines scorecard status as:

```python
Literal["active", "draft", "disabled", "deleted"]
```

that is not aligned with this backend scorecard API. Update the SDK type for table scorecards or introduce a separate type if those values belong to another SDK concept.

### Scorecard calculation status

```txt
queued
running
completed
failed
cancelled
```

### Verdicts

```txt
pass
warn
fail
error
skipped
```

### Criterion primitive types

```txt
COLUMN_AGGREGATE
CONTAINS
REGEX
ASSERT_VALID
COMPARE
LLM_ASSERTION
TOOL_EVALUATOR
CODE_EXECUTION
STRUCTURE
MAX_TOOL_CALLS
NO_INVALID_TOOL_CALLS
```

If the SDK currently defines scorecard primitive types as:

```python
Literal["boolean", "number", "categorical", "text", "json"]
```

that does not match the current backend criterion primitives for this endpoint. Update the table scorecard SDK type or separate the concepts.

Public docs and screenshots should use evaluators that appear in the product add-evaluator UI (Quality evaluators such as `CONTAINS`, `COMPARE`, `LLM_ASSERTION`, `CODE_EXECUTION`, `REGEX`, and `ASSERT_VALID`). Do **not** document or screenshot hidden agent-behavior primitives (`MAX_TOOL_CALLS`, `NO_INVALID_TOOL_CALLS`, `TOOL_EVALUATOR`, `STRUCTURE`) until they are exposed in the UI.

---

## 5. Public API endpoint reference

### 5.1 Get scorecard

```http
GET /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard
```

Returns the active scorecard for a sheet, if one exists.


#### Response when no scorecard exists

```json
{
  "success": true,
  "scorecard": null,
  "latest_calculation": null
}
```

#### Response when a scorecard exists

```json
{
  "success": true,
  "scorecard": {
    "id": "scorecard-id",
    "workspace_id": 123,
    "smart_table_id": "table-id",
    "sheet_id": "sheet-id",
    "name": "Quality Scorecard",
    "evaluated_column_ids": [],
    "aggregation": {
      "method": "weighted_mean",
      "required_step_failure_behavior": "fail",
      "pass_threshold": 0.8,
      "warn_threshold": 0.6
    },
    "display_config": null,
    "baseline_config": null,
    "status": "completed",
    "stale_state": {
      "is_stale": false,
      "reasons": []
    },
    "latest_calculation_id": "calculation-id",
    "config_hash": "hash",
    "steps": [],
    "created_at": "2026-07-09T12:00:00+00:00",
    "updated_at": "2026-07-09T12:00:00+00:00"
  },
  "latest_calculation": {
    "id": "calculation-id",
    "scorecard_id": "scorecard-id",
    "workspace_id": 123,
    "sheet_id": "sheet-id",
    "sheet_revision": "12",
    "status": "completed",
    "aggregate_score": 0.87,
    "aggregate_verdict": "pass",
    "criterion_summaries": {},
    "drift_summary": null,
    "config_hash": "hash",
    "started_at": "2026-07-09T12:00:00+00:00",
    "completed_at": "2026-07-09T12:01:00+00:00",
    "error_summary": null
  },
  "display_calculation": {
    "id": "calculation-id",
    "scorecard_id": "scorecard-id",
    "workspace_id": 123,
    "sheet_id": "sheet-id",
    "sheet_revision": "12",
    "status": "completed",
    "aggregate_score": 0.87,
    "aggregate_verdict": "pass",
    "criterion_summaries": {},
    "drift_summary": null,
    "config_hash": "hash",
    "started_at": "2026-07-09T12:00:00+00:00",
    "completed_at": "2026-07-09T12:01:00+00:00",
    "error_summary": null
  },
  "criterion_summaries": {},
  "drift_summary": null
}
```

Notes:

- The raw backend response currently includes `smart_table_id`. Public docs may describe this as the table identifier, but SDK types should either expose the raw response field or intentionally alias it with clear documentation.
- `display_calculation` may differ from `latest_calculation`. If the latest calculation is completed, `display_calculation` is that completed calculation. If the latest calculation is queued, running, or failed, `display_calculation` may be the previous completed calculation. If there is no completed calculation to display, it is `null`.

---

### 5.2 Configure scorecard

```http
PATCH /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard
```

Creates or updates the active scorecard for a sheet.


#### Request

```json
{
  "name": "Quality Scorecard",
  "evaluated_column_ids": [],
  "aggregation": {
    "method": "weighted_mean",
    "required_step_failure_behavior": "fail",
    "pass_threshold": 0.8,
    "warn_threshold": 0.6
  },
  "steps": [
    {
      "title": "Output matches expected",
      "primitive_type": "COMPARE",
      "source_column_ids": ["output-column-id", "expected-column-id"],
      "weight": 1,
      "required": false,
      "thresholds": {
        "pass": 0.8,
        "warn": 0.6
      },
      "primitive_config": {
        "sources": ["output-column-id", "expected-column-id"]
      },
      "score_adapter": null
    }
  ]
}
```

#### Backend request schema

The current backend Pydantic body is:

```python
class ConfigurePublicScorecardBody(BaseModel):
    name: str
    evaluated_column_ids: list[str] = Field(default_factory=list)
    steps: list[dict[str, Any]] = Field(default_factory=list)
    aggregation: dict[str, Any]
    display_config: dict[str, Any] | None = None
    baseline_config: dict[str, Any] | None = None
```

Therefore:

- `name` is required.
- `aggregation` is required.
- `evaluated_column_ids` may be omitted and defaults to `[]`.
- `steps` may be omitted and defaults to `[]`.

If the Python SDK currently marks `evaluated_column_ids` and `steps` as `Required[...]`, update the SDK types to make them optional for this endpoint, or document that the SDK requires fields that the backend does not require. Prefer aligning SDK with backend.

#### Response

```json
{
  "success": true,
  "scorecard": {
    "id": "scorecard-id",
    "name": "Quality Scorecard",
    "steps": [
      {
        "id": "criterion-step-id",
        "title": "Output matches expected",
        "primitive_type": "COMPARE",
        "source_column_ids": ["output-column-id", "expected-column-id"]
      }
    ]
  },
  "version": 13
}
```

Nested `scorecard` examples may be abbreviated for readability. The backend returns the full serialized scorecard.

---

### 5.3 Soft-delete scorecard

```http
DELETE /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard
```

Soft-deletes the active scorecard for the sheet.


#### Response

```json
{
  "success": true
}
```

Deleting a scorecard does not delete legacy score configuration. Legacy `/score` behavior may still exist if the sheet has a legacy score configuration.

---

### 5.4 Migrate legacy score to scorecard

```http
POST /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard/migrate-legacy-score
```

Converts an existing legacy sheet score configuration into scorecard criteria.


#### Request

```json
{
  "delete_legacy_score": false
}
```

`delete_legacy_score` defaults to `false`.

#### Response

```json
{
  "success": true,
  "scorecard": {
    "id": "scorecard-id",
    "name": "Scorecard",
    "steps": []
  },
  "converted_count": 2,
  "skipped": [],
  "legacy_score_deleted": false,
  "version": 14
}
```

Skipped migration example:

```json
{
  "success": true,
  "scorecard": {
    "id": "scorecard-id"
  },
  "converted_count": 0,
  "skipped": [
    {
      "reason": "Custom scoring code cannot be converted automatically.",
      "score_type": "custom"
    }
  ],
  "legacy_score_deleted": false,
  "version": 14
}
```

Some legacy score configurations cannot be converted automatically, including custom scoring code, missing score columns, and unsupported column types.

---

### 5.5 Recalculate scorecard

```http
POST /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard/recalculate
```

Queues scorecard recalculation.



#### Request

Full recalculation:

```json
{}
```

Scoped recalculation:

```json
{
  "row_indices": [0, 1, 2],
  "step_ids": ["22222222-2222-2222-2222-222222222222"]
}
```

#### Backend request schema

```python
class RecalculatePublicScorecardBody(BaseModel):
    row_indices: list[int] | None = None
    step_ids: list[UUID] | None = None
```

The backend does **not** currently accept `force` on `/scorecard/recalculate`.

If the Python SDK currently has:

```python
class RecalculateScorecardRequest(TypedDict, total=False):
    row_indices: List[int]
    force: bool
```

update it to include `step_ids` and remove or ignore `force` unless the backend adds support for `force`.

#### Response

```json
{
  "success": true,
  "calculation_id": "calculation-id",
  "status": "queued",
  "version": 15
}
```

Status code: `202 Accepted`.

---

### 5.6 Cancel scorecard calculation

```http
POST /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard/cancel
```

Cancels active queued/running scorecard work when possible.


#### Request

```json
{
  "row_indices": [0, 1],
  "step_ids": ["22222222-2222-2222-2222-222222222222"]
}
```

All fields are optional.

#### Backend request schema

```python
class CancelPublicScorecardBody(BaseModel):
    row_indices: list[int] | None = None
    step_ids: list[UUID] | None = None
```

The backend does **not** currently accept `calculation_id` on `/scorecard/cancel`. It cancels the active latest queued/running calculation for the scorecard.

If the Python SDK currently has:

```python
class CancelScorecardRequest(TypedDict, total=False):
    calculation_id: str
```

update it to match the backend request body or update the backend if cancellation by calculation ID is desired.

#### Response

```json
{
  "success": true,
  "message": "Scorecard run stopped",
  "scorecard": {
    "id": "scorecard-id"
  },
  "cancelled_count": 3,
  "execution_ids": ["execution-id"],
  "calculation_id": "calculation-id"
}
```

If nothing was cancellable:

```json
{
  "success": true,
  "message": "Scorecard run stopped",
  "scorecard": {
    "id": "scorecard-id"
  },
  "cancelled_count": 0,
  "execution_ids": [],
  "calculation_id": null
}
```

---

### 5.7 Get calculation details

```http
GET /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard/calculations/{calculation_id}
```


#### Response

```json
{
  "success": true,
  "calculation": {
    "id": "calculation-id",
    "scorecard_id": "scorecard-id",
    "workspace_id": 123,
    "sheet_id": "sheet-id",
    "sheet_revision": "15",
    "status": "completed",
    "aggregate_score": 0.87,
    "aggregate_verdict": "pass",
    "criterion_summaries": {},
    "drift_summary": null,
    "config_hash": "hash",
    "started_at": "2026-07-09T12:00:00+00:00",
    "completed_at": "2026-07-09T12:01:00+00:00",
    "error_summary": null
  },
  "criterion_summaries": {},
  "drift_summary": null
}
```

---

### 5.8 List row summaries

```http
GET /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard/rows
```


#### Query parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `calculation_id` | UUID | No | Calculation to read from. Defaults to latest scorecard calculation. |
| `verdict` | string | No | Filter by row verdict: `pass`, `warn`, `fail`, `error`, `skipped`. |
| `cursor` | integer | No | Row-index cursor. The backend returns rows where `row_index > cursor`. |
| `limit` | integer | No | Number of rows to return. Default `50`, maximum `100`. |

#### Response

```json
{
  "success": true,
  "calculation_id": "calculation-id",
  "rows": [
    {
      "row_index": 0,
      "aggregate_score": 0.42,
      "aggregate_verdict": "fail",
      "drift_summary": null,
      "stale_state": null,
      "error_summary": null
    }
  ],
  "next_cursor": null,
  "verdict_counts": {
    "fail": 1
  }
}
```

The current backend uses `cursor` / `next_cursor`, not `offset` / `next_offset`. The list response also includes `calculation_id` and `verdict_counts` at the top level.

If the Python SDK currently has:

```python
class ListScorecardRowsOptions(TypedDict, total=False):
    calculation_id: str
    verdict: ScoreVerdict
    stale_state: ScorecardStaleState
    limit: int
    offset: int
```

update it to match the backend (`cursor` / `next_cursor`) unless the SDK intentionally provides an abstraction layer. The backend does **not** currently support `offset` or `stale_state` query parameters on this endpoint.

---

### 5.9 Get row breakdown

```http
GET /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard/rows/{row_index}
```


#### Query parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `calculation_id` | UUID | No | Calculation to read from. Defaults to latest scorecard calculation. |

#### Response

```json
{
  "success": true,
  "id": "row-result-id",
  "calculation_id": "calculation-id",
  "scorecard_id": "scorecard-id",
  "sheet_id": "sheet-id",
  "row_index": 0,
  "aggregate_score": 0.42,
  "aggregate_verdict": "fail",
  "step_results": {
    "criterion-step-id": {
      "score": 0,
      "verdict": "fail",
      "evidence": "Expected value was not found.",
      "raw_value": false,
      "computed_at": "2026-07-09T12:01:00+00:00",
      "config_hash": "hash",
      "input_hash": "hash"
    }
  },
  "drift_summary": null,
  "stale_state": null,
  "error_summary": null,
  "config_hash": "hash",
  "input_hash": "hash",
  "computed_at": "2026-07-09T12:01:00+00:00"
}
```

---

## 6. Existing `/score` compatibility behavior

Existing public table scoring endpoints remain supported:

```http
/api/public/v2/tables/{table_id}/sheets/{sheet_id}/score
```



### GET `/score`

If a legacy score configuration exists, this endpoint returns legacy score data as before.

If no legacy score configuration exists and the sheet has an active scorecard with a completed latest calculation and non-null aggregate score, `GET /score` can return a scorecard-compatible payload:

```json
{
  "success": true,
  "score_type": "scorecard",
  "scoring_type": "scorecard",
  "overall_score": 0.87,
  "aggregate_score": 0.87,
  "score_configuration": null,
  "details": {
    "columns": [],
    "aggregate_result": {
      "scorecard_id": "scorecard-id",
      "scorecard_calculation_id": "calculation-id",
      "aggregate_verdict": "pass",
      "criterion_summaries": {},
      "drift_summary": null
    }
  },
  "aggregate": {
    "type": "scorecard",
    "value": 0.87,
    "result": {
      "scorecard_id": "scorecard-id",
      "scorecard_calculation_id": "calculation-id"
    }
  },
  "per_column": {}
}
```

If both a legacy score configuration and a scorecard exist, `/score` returns legacy behavior. Use `/scorecard` for scorecard-specific state and results.

### POST `/score`

If a legacy score configuration exists, this endpoint queues legacy score recalculation.

If no legacy score configuration exists but an active scorecard exists, this endpoint queues scorecard recalculation:

```json
{
  "success": true,
  "score_source": "scorecard",
  "calculation_id": "calculation-id",
  "status": "queued",
  "version": 15
}
```

---

## 7. Safe migration guide


Recommended migration path:

1. Inspect current legacy score behavior:

   ```http
   GET /api/public/v2/tables/{table_id}/sheets/{sheet_id}/score
   ```

2. Convert the legacy score configuration into a scorecard:

   ```http
   POST /api/public/v2/tables/{table_id}/sheets/{sheet_id}/scorecard/migrate-legacy-score
   ```

   ```json
   {
     "delete_legacy_score": false
   }
   ```

3. Inspect `converted_count`, `skipped`, and `scorecard.steps`.
4. Recalculate via `POST /scorecard/recalculate`.
5. Poll with `GET /scorecard/calculations/{calculation_id}`.
6. Move consumers from `/score` to `/scorecard`.
7. Only after all consumers have migrated, optionally delete the legacy score configuration by using:

   ```json
   {
     "delete_legacy_score": true
   }
   ```

Do not set `delete_legacy_score: true` until every consumer that depends on `/score` has been migrated or verified to support the scorecard fallback response shape.

---

## 8. Criterion examples



### Empty scorecard

```json
{
  "name": "Quality Scorecard",
  "evaluated_column_ids": [],
  "aggregation": {
    "method": "weighted_mean",
    "required_step_failure_behavior": "fail",
    "pass_threshold": 0.8,
    "warn_threshold": 0.6
  },
  "steps": []
}
```

### Compare criterion

```json
{
  "title": "Output matches expected",
  "primitive_type": "COMPARE",
  "source_column_ids": ["output-column-id", "expected-column-id"],
  "weight": 1,
  "required": false,
  "thresholds": {
    "pass": 0.8,
    "warn": 0.6
  },
  "primitive_config": {
    "sources": ["output-column-id", "expected-column-id"]
  }
}
```

### Contains criterion

```json
{
  "title": "Output contains required text",
  "primitive_type": "CONTAINS",
  "source_column_ids": ["output-column-id", "expected-column-id"],
  "weight": 1,
  "required": false,
  "thresholds": {
    "pass": 0.8,
    "warn": 0.6
  },
  "primitive_config": {
    "source": "output-column-id",
    "value_source": "expected-column-id"
  }
}
```

### Column aggregate criterion

```json
{
  "title": "Average quality",
  "primitive_type": "COLUMN_AGGREGATE",
  "source_column_ids": ["quality-column-id"],
  "weight": 1,
  "required": false,
  "thresholds": {
    "pass": 0.8,
    "warn": 0.6
  },
  "primitive_config": {
    "source": "quality-column-id",
    "aggregation_type": "average_value",
    "score_mode": "score",
    "score_max": 1
  }
}
```

Supported `COLUMN_AGGREGATE` `aggregation_type` values:

```txt
average_value
most_frequent_value
min_value
max_value
```

---

## 9. Python SDK docs

Current Python SDK namespace:

```python
client.tables.sheets.scorecards
```

Use snake_case methods in Python SDK docs.


### Get scorecard

```python
response = client.tables.sheets.scorecards.get(table_id, sheet_id)
scorecard = response["scorecard"]
```

### Configure scorecard

```python
response = client.tables.sheets.scorecards.configure_scorecard(
    table_id,
    sheet_id,
    {
        "name": "Quality Scorecard",
        "evaluated_column_ids": [],
        "aggregation": {
            "method": "weighted_mean",
            "required_step_failure_behavior": "fail",
            "pass_threshold": 0.8,
            "warn_threshold": 0.6,
        },
        "steps": [
            {
                "title": "Output matches expected",
                "primitive_type": "COMPARE",
                "source_column_ids": ["output-column-id", "expected-column-id"],
                "weight": 1,
                "required": False,
                "thresholds": {
                    "pass": 0.8,
                    "warn": 0.6,
                },
                "primitive_config": {
                    "sources": ["output-column-id", "expected-column-id"],
                },
            }
        ],
    },
)
```

SDK implementation note: `configure_scorecard(...)` must call backend `PATCH /scorecard`, not `PUT /scorecard`, unless the backend is changed to accept `PUT`.

### Migrate legacy score

```python
migration = client.tables.sheets.scorecards.migrate_legacy_score(
    table_id,
    sheet_id,
    {"delete_legacy_score": False},
)
```

### Recalculate scorecard

```python
run = client.tables.sheets.scorecards.recalculate(table_id, sheet_id)
```

Scoped recalculation:

```python
run = client.tables.sheets.scorecards.recalculate(
    table_id,
    sheet_id,
    {
        "row_indices": [0, 1, 2],
        "step_ids": ["22222222-2222-2222-2222-222222222222"],
    },
)
```

### Get calculation

```python
calculation_response = client.tables.sheets.scorecards.get_calculation(
    table_id,
    sheet_id,
    run["calculation_id"],
)
calculation = calculation_response["calculation"]
```

### List rows

```python
rows_response = client.tables.sheets.scorecards.list_rows(
    table_id,
    sheet_id,
    {
        "calculation_id": run["calculation_id"],
        "verdict": "fail",
        "limit": 50,
    },
)
rows = rows_response["rows"]
```

### Get row

```python
row = client.tables.sheets.scorecards.get_row(
    table_id,
    sheet_id,
    0,
    {"calculation_id": run["calculation_id"]},
)
```

### Cancel

```python
client.tables.sheets.scorecards.cancel(table_id, sheet_id)
```

Scoped cancel:

```python
client.tables.sheets.scorecards.cancel(
    table_id,
    sheet_id,
    {
        "row_indices": [0, 1],
        "step_ids": ["22222222-2222-2222-2222-222222222222"],
    },
)
```

### Delete scorecard

```python
client.tables.sheets.scorecards.delete(table_id, sheet_id)
```

---

## 10. Python SDK type alignment checklist

Update the Python SDK scorecard types to match backend behavior.

### ConfigureScorecardRequest

Backend allows `evaluated_column_ids` and `steps` to be omitted.

Recommended SDK type:

```python
class ConfigureScorecardRequest(TypedDict, total=False):
    name: Required[str]
    evaluated_column_ids: List[str]
    aggregation: Required[ScorecardAggregationConfig]
    steps: List[ScorecardStep]
    display_config: Dict[str, object]
    baseline_config: Dict[str, object]
```

### RecalculateScorecardRequest

Backend accepts `row_indices` and `step_ids`; it does not accept `force`.

```python
class RecalculateScorecardRequest(TypedDict, total=False):
    row_indices: List[int]
    step_ids: List[str]
```

### CancelScorecardRequest

Backend accepts `row_indices` and `step_ids`; it does not accept `calculation_id`.

```python
class CancelScorecardRequest(TypedDict, total=False):
    row_indices: List[int]
    step_ids: List[str]
```

### ListScorecardRowsOptions

Backend accepts `cursor` and returns `next_cursor`; it does not accept `offset`, `next_offset`, or `stale_state`. The response includes top-level `calculation_id` and `verdict_counts`.

```python
class ListScorecardRowsOptions(TypedDict, total=False):
    calculation_id: str
    verdict: ScoreVerdict
    cursor: int
    limit: int
```

```python
class ListScorecardRowsResponse(TypedDict):
    success: bool
    calculation_id: str
    rows: List[ScorecardRowSummary]
    next_cursor: int | None
    verdict_counts: Dict[str, int]
```

### Existing `/score` SDK response types

Existing score response types should allow scorecard fallback fields:

```python
score_type: Literal["scorecard"]
scoring_type: Literal["scorecard"]
score_configuration: None
```

Existing score recalculation response type should allow this union case:

```python
class ScorecardPiggybackRecalculationResponse(TypedDict):
    success: bool
    score_source: Literal["scorecard"]
    calculation_id: str
    status: str
    version: int
```

---

## 11. Public-ready quality bar

Final docs should:

- Use public wording: tables, sheets, table scorecards, scorecards.
- Avoid “Smart Table” except where legacy docs still require a transition note.
- Use Python SDK examples, not TypeScript examples.
- Use Python SDK snake_case method names.
- Document backend-canonical HTTP methods, especially `PATCH /scorecard` for configuration.
- Explain exactly when `/score` returns legacy behavior vs scorecard fallback behavior.
- Emphasize safe migration with `delete_legacy_score: false`.
- Include migration caveats and skipped conversion examples.
- Keep examples aligned with backend fields, including currently returned fields such as `smart_table_id`, `latest_calculation_id`, `aggregate_score`, `aggregate_verdict`, `criterion_summaries`, `step_results`, and `verdict_counts`.
- If the SDK chooses aliases such as `table_id` instead of raw `smart_table_id`, document that aliasing explicitly.

---

## Screenshot capture notes

Screenshots in `screenshots/` use only evaluators exposed in the product add-evaluator UI (Quality evaluators). Hidden agent-behavior primitives are excluded from demo data, screenshots, and public doc examples.

To regenerate:

```bash
cd /workspace/backend && uv run python scripts/seed_scorecard_demo.py
# with backend and frontend running:
cd /workspace/scripts && node capture-scorecard-docs-screenshots.mjs
```
