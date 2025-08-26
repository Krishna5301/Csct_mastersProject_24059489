# PowerShell script to set up TensorFlow Nightly environment
#
# NOTE: If you cannot run this script, you may need to change your PowerShell execution policy.
# To do so, run PowerShell as an Administrator and execute the following command:
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Check if pip is installed
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "Error: pip is not installed or not in PATH. Please install Python and pip first." -ForegroundColor Red
    exit 1
}

$pythonExecutable = "python"
$pipExecutable = "pip"

# --- Create a virtual environment (optional) ---
$createVenv = Read-Host "Do you want to create a virtual environment? (y/n)"
if ($createVenv.ToLower() -eq "y") {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    & $pythonExecutable -m venv tf_env

    # Set paths to use the venv's executables
    $pythonExecutable = ".\tf_env\Scripts\python.exe"
    $pipExecutable = ".\tf_env\Scripts\pip.exe"

    Write-Host "Virtual environment 'tf_env' created." -ForegroundColor Green
    Write-Host "Packages will be installed into this environment." -ForegroundColor Yellow
} else {
    Write-Host "Skipping virtual environment creation. Using the current Python environment." -ForegroundColor Yellow
}

# --- Install TensorFlow Nightly ---
Write-Host "Installing TensorFlow Nightly..." -ForegroundColor Green
Write-Host "Note: For GPU support, you must have the compatible NVIDIA drivers, CUDA Toolkit, and cuDNN installed." -ForegroundColor Yellow
& $pipExecutable install tf-nightly

# --- Install other requirements ---
$requirementsFile = "requirements.txt"
if (-not (Test-Path $requirementsFile)) {
    Write-Host "Warning: '$requirementsFile' not found. Skipping installation of other requirements." -ForegroundColor Yellow
    Write-Host "If you have other dependencies, please create a '$requirementsFile' file." -ForegroundColor Yellow
} else {
    Write-Host "Installing other requirements from $requirementsFile..." -ForegroundColor Green
    & $pipExecutable install -r $requirementsFile
}

# --- Verify installation ---
Write-Host "Verifying TensorFlow installation..." -ForegroundColor Green
& $pythonExecutable -c "import tensorflow as tf; print('TensorFlow Version:', tf.__version__); print('Num GPUs Available: ', len(tf.config.list_physical_devices('GPU')))"

# --- Final Instructions ---
Write-Host "Setup complete!" -ForegroundColor Green

if ($createVenv.ToLower() -eq "y") {
    Write-Host "To use the new environment, first activate it by running:" -ForegroundColor Green
    Write-Host ".\tf_env\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "Then you can run the TensorFlow notebook:" -ForegroundColor Green
    Write-Host "jupyter notebook notebooks/model_development_tensorflow.ipynb" -ForegroundColor Cyan
} else {
    Write-Host "You can now run the TensorFlow notebook:" -ForegroundColor Green
    Write-Host "jupyter notebook notebooks/model_development_tensorflow.ipynb" -ForegroundColor Cyan
}