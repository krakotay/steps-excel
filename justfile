set shell := ["pwsh", "-Command"]

prep:
    if (-not (Test-Path "release/backend")) { New-Item -ItemType Directory -Path "release/backend" }
    cd backend && Get-ChildItem -Filter *.py -File | Copy-Item -Destination "../release/backend" -Force
    uv pip freeze > "requirements.txt"
    release/backend/python/python.exe -m pip install -r requirements.txt --break-system-packages --no-warn-script-location 

release: prep
    Remove-Item -Path "release/ПО_ШАГАМ_*.7z" -Force -ErrorAction SilentlyContinue
    cd release && 7z a -mx=1 "ПО_ШАГАМ_2.0.7z" "."
