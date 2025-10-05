@echo off
REM Reinstall conda environment for the project
echo ========================================
echo Reinstalling turing0.1 environment
echo ========================================

echo.
echo Step 1: Removing old environment...
call conda deactivate
call conda env remove -n turing0.1 -y

echo.
echo Step 2: Creating fresh environment with Python 3.11...
call conda create -n turing0.1 python=3.11 -y

echo.
echo Step 3: Activating environment...
call conda activate turing0.1

echo.
echo Step 4: Installing PyTorch with CUDA support...
call conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

echo.
echo Step 5: Installing requirements from requirements.txt...
call pip install -r requirements.txt

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo To activate the environment, run:
echo   conda activate turing0.1
echo.
echo Then test with:
echo   python embed_companies_qdrant.py
echo   python test_incentive_matching.py
echo.
pause
