# TASK: Install Java 17 (Temurin) and Start Neo4j

## 1️⃣ Download latest Temurin JDK 17 MSI for Windows
```powershell
# Create Neo4j directory
New-Item -ItemType Directory -Force -Path "C:\Neo4j"

# Download latest Temurin JDK 17 MSI
$javaUrl = "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse"
Write-Host "Downloading Java 17 from: $javaUrl"
Invoke-WebRequest -Uri $javaUrl -OutFile "C:\Neo4j\OpenJDK17.msi"
Write-Host "Java 17 MSI downloaded successfully"
```

## 2️⃣ Install Java 17 silently
```powershell
Write-Host "Installing Java 17 silently..."
Start-Process msiexec.exe -Wait -ArgumentList '/i "C:\Neo4j\OpenJDK17.msi" /qn ADDLOCAL=FeatureMain,FeatureEnvironment ADDENVIRONMENTVARIABLE=1'
Write-Host "Java 17 installation completed"
```

## 3️⃣ Verify installation
```powershell
Write-Host "Verifying Java installation..."
java -version
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Java 17 installed successfully"
} else {
    Write-Host "❌ Java installation failed"
    exit 1
}
```

## 4️⃣ Download and setup Neo4j Community Edition
```powershell
# Download Neo4j Community Edition
$neo4jUrl = "https://dist.neo4j.org/neo4j-community-5.23.0-windows.zip"
Write-Host "Downloading Neo4j Community Edition..."
Invoke-WebRequest -Uri $neo4jUrl -OutFile "C:\Neo4j\neo4j-community-5.23.0-windows.zip"

# Extract Neo4j
Write-Host "Extracting Neo4j..."
Expand-Archive -Path "C:\Neo4j\neo4j-community-5.23.0-windows.zip" -DestinationPath "C:\Neo4j\" -Force
Write-Host "Neo4j extracted successfully"
```

## 5️⃣ Configure Neo4j
```powershell
# Set initial password
$neo4jPath = "C:\Neo4j\neo4j-community-5.23.0"
Write-Host "Setting Neo4j initial password..."
& "$neo4jPath\bin\neo4j-admin.bat" dbms set-initial-password 12345
Write-Host "Neo4j password set to: 12345"
```

## 6️⃣ Start Neo4j
```powershell
Write-Host "Starting Neo4j..."
cd "$neo4jPath\bin"
Start-Process -FilePath ".\neo4j.bat" -ArgumentList "console" -NoNewWindow
Write-Host "Neo4j is starting... Check http://localhost:7474 in a few moments"
Write-Host "Default credentials: neo4j / 12345"
```

## ✅ Verification
```powershell
# Wait a moment for Neo4j to start
Start-Sleep -Seconds 10

# Test Neo4j connection
try {
    $response = Invoke-WebRequest -Uri "http://localhost:7474" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Neo4j is running successfully at http://localhost:7474"
        Write-Host "✅ Java 17 and Neo4j setup completed!"
    }
} catch {
    Write-Host "⚠️ Neo4j may still be starting up. Check http://localhost:7474 manually"
}
```

---

## 🎯 Expected Results

After completion:
- ✅ Java 17 installed and in PATH
- ✅ Neo4j Community Edition running on port 7474
- ✅ Web interface available at http://localhost:7474
- ✅ Default credentials: neo4j / 12345
- ✅ Ready for TERAG v2 graph integration

## 🆘 Troubleshooting

If Neo4j doesn't start:
1. Check if port 7474 is available
2. Verify Java 17 is in PATH: `java -version`
3. Check Neo4j logs in `C:\Neo4j\neo4j-community-5.23.0\logs`
4. Try manual start: `cd C:\Neo4j\neo4j-community-5.23.0\bin && .\neo4j.bat console`
