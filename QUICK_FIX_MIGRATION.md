# Quick Fix for Migration Error

The error "no such table: Law_school_userprofile" occurs because migrations haven't been created yet.

## Steps to Fix:

1. **Create migrations directory** (if it doesn't exist):
   - Create: `Law_school\migrations\` directory
   - Create: `Law_school\migrations\__init__.py` file (empty file)

2. **Run makemigrations**:
   ```
   python manage.py makemigrations
   ```
   When prompted:
   - "Was download.opened renamed to download.downloaded?" → Type **y**
   - "Provide one-off default for Assignment_Name?" → Type **1** and then **"Unnamed Assignment"**
   - Answer any other prompts as needed

3. **Run migrate**:
   ```
   python manage.py migrate
   ```

4. **After migration**, follow the cleanup steps in `POST_MIGRATION_CLEANUP.txt`
