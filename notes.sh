#!/bin/bash

# 1. Define your three target directories
DIRS=(
    "cc5_sis_availability/CybORG/tests"
    "cc5_sis_integrity/CybORG/tests"
    "cc5_sis_confidentiality/CybORG/tests"
)

# 2. Define the path to your virtual environment
VENV_DIR="venv"

# 3. Activate the environment safely
if [ -d "$VENV_DIR" ]; then
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo "Error: Virtual environment directory '$VENV_DIR' not found."
    exit 1
fi

# Store the starting directory so we can return to it later
START_DIR=$(pwd)

# 4. Loop through each directory
for dir in "${DIRS[@]}"; do
    echo -e "\n==================================="
    echo "Entering directory: $dir"
    echo "==================================="
    
    # Check if the directory exists before entering
    if [ -d "$dir" ]; then
        
        # Determine the correct notes subfolder based on the path keyword
        if [[ "$dir" == *"availability"* ]]; then
            NOTE_SUBDIR="notes/availability"
        elif [[ "$dir" == *"integrity"* ]]; then
            NOTE_SUBDIR="notes/integrity"
        elif [[ "$dir" == *"confidentiality"* ]]; then
            NOTE_SUBDIR="notes/confidentiality"
        else
            NOTE_SUBDIR="notes/misc"
        fi
        
        # Create the specific notes directory if it doesn't exist yet
        mkdir -p "$START_DIR/$NOTE_SUBDIR"
        
        cd "$dir" || continue
        
        # Loop through and run every Python file in this folder
        for file in *.py; do
            # Check if files actually exist to prevent errors in an empty folder
            [ -e "$file" ] || continue
            
            # Remove the ".py" extension from the filename to use it for the text log
            base_name="${file%.py}"
            output_file="$START_DIR/$NOTE_SUBDIR/${base_name}_output.txt"
            
            echo "Running: $file (Saving output to $NOTE_SUBDIR/${base_name}_output.txt)"
            
            # Run the file and save BOTH regular logs and errors (2>&1) to the text file
            python "$file" > "$output_file" 2>&1
            
            echo "Finished: $file"
            echo "-----------------------------------"
        done
        
        # Go back to the starting directory
        cd "$START_DIR" || exit
    else
        echo "Warning: Directory '$dir' does not exist. Skipping."
    fi
done

# 5. Deactivate the environment when done
deactivate
echo "All scripts across all directories finished."
