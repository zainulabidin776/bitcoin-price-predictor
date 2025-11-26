# Transform Data Column Name Fix

## Problem

The `transform_data` task was failing with `KeyError: 'date'` because:
- **CryptoCompare extractor** saves data with columns: `timestamp`, `close`, `open`, `high`, `low`, `volume`, `volume_usd`
- **Transform code** was expecting columns: `date`, `priceUsd`

## Solution

Updated `src/data/transform.py` to handle both column name formats:

1. **Date column handling:**
   - Accepts both `timestamp` (CryptoCompare) and `date` (legacy format)
   - Normalizes to `date` column for internal use

2. **Price column handling:**
   - Accepts both `close` (CryptoCompare) and `priceUsd` (legacy format)
   - Normalizes to `priceUsd` column for feature engineering

## Code Changes

### Before:
```python
df['date'] = pd.to_datetime(df['date'])  # ❌ Fails if column is 'timestamp'
df['priceUsd'] = pd.to_numeric(df['priceUsd'], errors='coerce')  # ❌ Fails if column is 'close'
```

### After:
```python
# Handle timestamp/date
if 'timestamp' in df.columns and 'date' not in df.columns:
    df['date'] = pd.to_datetime(df['timestamp'])
elif 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

# Handle close/priceUsd
if 'close' in df.columns and 'priceUsd' not in df.columns:
    df['priceUsd'] = pd.to_numeric(df['close'], errors='coerce')
```

## Testing

After this fix, the transform task should:
1. ✅ Load CryptoCompare data (with `timestamp` and `close` columns)
2. ✅ Normalize column names internally
3. ✅ Create all 36 features successfully
4. ✅ Generate profiling report
5. ✅ Save processed data

## Verification

Run the DAG again and check:
- `extract_data` task: ✅ Should complete
- `quality_check` task: ✅ Should complete
- `transform_data` task: ✅ Should now complete (was failing before)
- `train_model` task: ✅ Should complete

## Related Files

- `src/data/extract.py` - CryptoCompare extractor (uses `timestamp`, `close`)
- `src/data/transform.py` - Feature engineering (now handles both formats)
- `airflow/dags/crypto_pipeline_dag.py` - DAG definition

