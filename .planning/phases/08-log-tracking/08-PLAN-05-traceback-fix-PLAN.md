---
wave: 5
depends_on: ["08-PLAN-01-database-signals.md", "08-PLAN-04-celery-signals-fix.md"]
files_modified:
  - server/app/domains/sys_worker/celery_signals.py
requirements:
  - LOG-01
autonomous: true
---

# Plan 05 - Format Celery Failure Tracebacks

<objective>
To extract a detailed, human-readable error trace stack rather than just printing the physical memory object pointer (`<traceback object...>`) during celery task failures.
</objective>

<verification>
A background worker exception should log the actual traceback string containing lines of stack execution in `error_traceback`.
</verification>

<must_haves>
- Uses `traceback.format_exception()` or Celery's built-in `einfo` traceback representation. 
</must_haves>

<tasks>
<task id="08-05-01" description="Format traceback error correctly">
<read_first>
- server/app/domains/sys_worker/celery_signals.py
</read_first>
<action>
1. Edit `server/app/domains/sys_worker/celery_signals.py`. Make sure `import traceback` is maintained.
2. Inside `task_failure_handler`, when setting `log.error_traceback`, we check `kwargs.get('einfo')` if available, otherwise fallback to `traceback.format_tb(traceback)` (joined as a string if it's a list) or just `str(exception)`.
Specifically, we can write:
```python
        formatted_tb = None
        if "einfo" in kwargs and kwargs["einfo"]:
            formatted_tb = str(kwargs["einfo"].traceback)
        elif traceback:
            import traceback as tb
            formatted_tb = "".join(tb.format_tb(traceback))
        elif exception:
            formatted_tb = str(exception)
            
        log.error_traceback = formatted_tb
```
</action>
<acceptance_criteria>
- `log.error_traceback` safely catches the human-readable traceback formatting.
</acceptance_criteria>
</task>
</tasks>
