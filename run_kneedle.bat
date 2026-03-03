@echo off
setlocal

REM === 1. Sprawdzenie czy Python jest zainstalowany ===
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [BŁĄD] Python nie jest zainstalowany lub nie jest w PATH.
    echo Pobierz go z: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python znaleziony.

REM === 2. Utworzenie wirtualnego środowiska (tylko raz) ===
IF NOT EXIST venv_kneedle (
    echo Tworzenie srodowiska wirtualnego...
    python -m venv venv_kneedle
)

REM === 3. Aktywacja środowiska ===
call venv_kneedle\Scripts\activate.bat

REM === 4. Instalacja zależności tylko raz ===
IF NOT EXIST venv_kneedle\installed.ok (
    echo Instalowanie zaleznosci z requirements.txt...
    pip install --upgrade pip
    pip install -r requirements.txt

    IF %ERRORLEVEL% NEQ 0 (
        echo.
        echo [BŁĄD] Instalacja zależności nie powiodła się.
        pause
        exit /b 1
    )

    echo OK > venv_kneedle\installed.ok
    echo Zaleznosci zainstalowane.
) ELSE (
    echo Zaleznosci juz byly zainstalowane — pomijam.
)

REM === 5. Uruchomienie programu ===
echo Uruchamianie aplikacji Kneedle...
python kneedle_app.py

pause
