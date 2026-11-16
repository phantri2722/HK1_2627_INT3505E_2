$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot

try {
    New-Item -ItemType Directory -Force -Path reports | Out-Null

    newman run postman/books-api.postman_collection.json `
        -e postman/local.postman_environment.json `
        -r "cli,junit" `
        --reporter-junit-export reports/junit.xml

    if ($LASTEXITCODE -ne 0) {
        throw "Newman tests failed."
    }
}
finally {
    Pop-Location
}