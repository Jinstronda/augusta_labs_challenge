@echo off
REM Quick fix for missing dependencies
echo ========================================
echo Installing missing dependencies
echo ========================================

echo.
echo Activating turing0.1 environment...
call conda activate turing0.1

echo.
echo Installing missing packages...
call pip install datasets>=2.14.0 transformers>=4.30.0 accelerate>=0.20.0

echo.
echo Upgrading existing packages to ensure compatibility...
call pip install --upgrade sentence-transformers FlagEmbedding

echo.
echo ========================================
echo Dependencies fixed!
echo ========================================
echo.
echo You can now run:
echo   python embed_companies_qdrant.py
echo   python test_incentive_matching.py
echo.
pause
