@echo off

set PROJECT_ROOT=C:\Users\srika\Documents\Srikanth_Amazon_BI_Project
set PYTHON_EXE=C:\Users\srika\anaconda3\envs\srikanth_amazon_bi\python.exe

cd /d "%PROJECT_ROOT%"

echo ================================================== >> "%PROJECT_ROOT%\logs\task_scheduler_output.log"
echo Pipeline started at %date% %time% >> "%PROJECT_ROOT%\logs\task_scheduler_output.log"

"%PYTHON_EXE%" "%PROJECT_ROOT%\scripts\run_etl_pipeline.py" >> "%PROJECT_ROOT%\logs\task_scheduler_output.log" 2>&1

if errorlevel 1 (
    echo Pipeline FAILED at %date% %time% >> "%PROJECT_ROOT%\logs\task_scheduler_output.log"
    exit /b 1
) else (
    echo Pipeline completed successfully at %date% %time% >> "%PROJECT_ROOT%\logs\task_scheduler_output.log"
    exit /b 0
)