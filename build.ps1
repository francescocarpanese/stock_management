# Create conda environment
$condaEnvName = "build_env"
$condaCreateCmd = "conda create -n $condaEnvName python=3.10 -y"
Invoke-Expression -Command $condaCreateCmd

# Activate conda environment
$activateEnvCmd = "conda activate $condaEnvName"
Invoke-Expression -Command $activateEnvCmd

# Install packages from requirements.txt
$requirementsFile = "requirements.txt"
$installRequirementsCmd = "pip install -r $requirementsFile"
Invoke-Expression -Command $installRequirementsCmd

# Run pyinstaller with the skimage location
$pyInstallerCmd = @'
pyinstaller --onefile ./stock_management/main.py
'@

Invoke-Expression -Command $pyInstallerCmd